''' DNS Client (command line application)
Authors: William Wang 261113954
         Kevin-Ruikai Li 261120382 
'''
import argparse
from io import BytesIO
import random
import sys
import socket
import struct
import time
import dataclasses
from dataclasses import dataclass

RECURSIVE_FLAG = 0x0100
TYPE_A = 1
TYPE_NS = 2
TYPE_CNAME = 5
TYPE_MX = 15

@dataclass
class DNSHeader:
    id: int
    flags: int
    qdcount: int = 0
    ancount: int = 0
    nscount: int = 0
    arcount: int = 0

@dataclass
class DNSQuestion:
    name: bytes
    qtype: int
    qclass: int

@dataclass
class DNSRecord:
    name: bytes
    type_: int
    class_: int
    ttl: int
    data: bytes

@dataclass
class DNSPacket:
    header: DNSHeader
    questions: list[DNSQuestion]
    answers: list[DNSRecord]
    authorities: list[DNSRecord]
    additionals: list[DNSRecord]

def header_to_bytes(header: DNSHeader) -> bytes:
    fields = dataclasses.astuple(header)
    return struct.pack('!HHHHHH', *fields)

# e.g. www.mcgill.ca -> (www, mcgill, ca) with lengts 3, 6, 2
def question_to_bytes(question: DNSQuestion) -> bytes:
    question_bytes = question.name
    question_bytes += struct.pack('!HH', question.qtype, question.qclass)
    return question_bytes

def encode_dns_name(name: str) -> bytes:
    name_bytes = b''
    for part in name.split('.'):
        name_bytes += struct.pack('!B', len(part))
        name_bytes += part.encode()
    name_bytes += b'\x00'
    return name_bytes

def create_command_line_parser() -> argparse.ArgumentParser:
    # python dnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name
    parser = argparse.ArgumentParser(description='DNS Client')
    parser.add_argument('-t', '--timeout', type=float, default=5, help='Timeout in seconds')
    parser.add_argument('-r', '--max-retries', type=int, default=3, help='Maximum number of retries')
    parser.add_argument('-p', '--port', type=int, default=53, help='Port number')
    parser.add_argument('-mx', '--mx', action='store_true', help='MX flag')
    parser.add_argument('-ns', '--ns', action='store_true', help='NS flag')
    parser.add_argument('server', type=str, help='Server name')
    parser.add_argument('name', type=str, help='Name')
    return parser

def verify_command_line_args(args: argparse.Namespace) -> None:
    if args.timeout <= 0:
        print('ERROR\tIncorrect input syntax: Timeout must be greater than 0')
        sys.exit(1)
    if args.max_retries <= 0:
        print('ERROR\tIncorrect input syntax: Max retries must be greater than 0')
        sys.exit(1)
    if args.port < 0 or args.port > 65535:
        print('ERROR\tIncorrect input syntax: Port number must be between 0 and 65535')
        sys.exit(1)
    if args.mx and args.ns:
        print('ERROR\tIncorrect input syntax: Cannot have both MX and NS flags')
        sys.exit(1)
    if args.server[0] != '@':
        print('ERROR\tIncorrect input syntax: Server name must start with @')
        sys.exit(1)
    server = args.server[1:]
    if len(server.split('.')) != 4 or not all(0 <= int(x) < 256 for x in server.split('.')):
        print(f'ERROR\tIncorrect input syntax: Server name must be in the format of an IP address (x.x.x.x) and each x must be between 0 and 255')
        sys.exit(1)

def build_dns_query(name: str, qtype: int) -> bytes:
    header = DNSHeader(
        id=random.randint(0, 65535),
        flags=RECURSIVE_FLAG,
        qdcount=1
    )

    question = DNSQuestion(
        name=encode_dns_name(name),
        qtype=qtype,
        qclass=1
    )
    query_bytes = header_to_bytes(header) + question_to_bytes(question)
    return query_bytes

def parse_dns_header(reader) -> DNSHeader:
    items = struct.unpack('!HHHHHH', reader.read(12))
    return DNSHeader(*items)

def decode_dns_name(reader):
    parts = []
    while (length := reader.read(1)[0]) != 0:
        if length & 0b1100_0000:
            parts.append(decode_compressed_dns_name(length, reader))
            break
        else:
            parts.append(reader.read(length))
    return b".".join(parts)


def decode_compressed_dns_name(length, reader):
    pointer_halfword = bytes([length & 0b0011_1111]) + reader.read(1)
    pointer = struct.unpack("!H", pointer_halfword)[0]
    current_pos = reader.tell()
    reader.seek(pointer)
    result = decode_dns_name(reader)
    reader.seek(current_pos)
    return result

def parse_dns_question(reader):
    name = decode_dns_name(reader)
    qtype, qclass = struct.unpack('!HH', reader.read(4))
    return DNSQuestion(name, qtype, qclass)

def parse_dns_record(reader):
    name = decode_dns_name(reader)
    type_, class_, ttl, rdlength = struct.unpack('!HHIH', reader.read(10))
    if type_ == TYPE_A:
        data = ip_to_string(reader.read(rdlength))
    elif type_ == TYPE_NS:
        data = decode_dns_name(reader)
    elif type_ == TYPE_CNAME:
        data = decode_dns_name(reader)
    elif type_ == TYPE_MX:
        preference = struct.unpack('!H', reader.read(2))[0]
        exchange = decode_dns_name(reader)
        data = (preference, exchange)
    else:
        data = reader.read(rdlength)
    return DNSRecord(name, type_, class_, ttl, data)

def parse_dns_packet(data):
    reader = BytesIO(data)
    header = parse_dns_header(reader)
    questions = [parse_dns_question(reader) for _ in range(header.qdcount)]
    answers = [parse_dns_record(reader) for _ in range(header.ancount)]
    authorities = [parse_dns_record(reader) for _ in range(header.nscount)]
    additionals = [parse_dns_record(reader) for _ in range(header.arcount)]

    return DNSPacket(header, questions, answers, authorities, additionals)

def ip_to_string(ip):
    return ".".join([str(x) for x in ip])


if __name__ == "__main__":
    start_time = time.time()
    
    # Is invoked from the command line (STDIN);
    parser = create_command_line_parser()
    args = parser.parse_args()
    verify_command_line_args(args)

    print("DnsClient sending request for", args.name)
    print("Server:", args.server[1:])
    print("Request type:", "MX" if args.mx else "NS" if args.ns else "A")

    # Create a DNS query packet and instantiate a UDP socket;
    query = build_dns_query(args.name, 15 if args.mx else 2 if args.ns else 1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send the query to the server and wait for a response;
    sock.settimeout(args.timeout)
    for attempt in range(args.max_retries + 1):
        try:
            sock.sendto(query, (args.server[1:], args.port))
            response, _ = sock.recvfrom(1024)

            # Record the time taken to receive the response;
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Break if a response is received;
            print(f"Response received after {elapsed_time} seconds ({attempt} retries)")
            break
        except socket.timeout:
            print(f"ERROR\tTimeout error: the server did not respond within the specified timeout ({args.timeout} seconds)")
            if attempt >= args.max_retries:
                print(f"ERROR\tMax number of retries ({args.max_retries}) exceeded")
                sys.exit(1)
            print(f"Retrying... ({attempt+1}/{args.max_retries})")

    # Parse the response and print the results;
    packet = parse_dns_packet(response)

    # Error handling
    rcode = packet.header.flags & 0x000F
    authoritive = packet.header.flags & 0x0400
    if rcode == 1:
        print("ERROR\tFormat error: the name server was unable to interpret the query.")
        sys.exit(1)
    elif rcode == 2:
        print("ERROR\tServer failure: the name server was unable to process this query due to a problem with the name server.")
        sys.exit(1)
    elif rcode == 3:
        print("NOTFOUND\tName Error: the domain name referenced in the query does not exist.")
        sys.exit(1)
    elif rcode == 4:
        print("ERROR\tNot Implemented: the name server does not support the requested kind of query.")
        sys.exit(1)
    elif rcode == 5:
        print("ERROR\tRefused: the name server refuses to perform the specified operation for policy reasons.")
        sys.exit(1)
    elif rcode != 0:
        print(f"ERROR\tUnknown error")
        sys.exit(1)

    if packet.answers:
        print(f"***Answer Section ({packet.header.ancount} records)***")
        for record in packet.answers:
            if record.type_ == TYPE_A:
                print(f"IP\t{record.data}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            elif record.type_ == TYPE_NS:
                print(f"NS\t{record.data.decode()}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            elif record.type_ == TYPE_CNAME:
                print(f"CNAME\t{record.data.decode()}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            elif record.type_ == TYPE_MX:
                print(f"MX\t{record.data[1].decode()}\t{record.data[0]}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            else:
                pass
    if packet.additionals:
        print(f"***Additional Section ({packet.header.arcount} records)***")
        for record in packet.additionals:
            if record.type_ == TYPE_A:
                print(f"IP\t{record.data}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            elif record.type_ == TYPE_NS:
                print(f"NS\t{record.data.decode()}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            elif record.type_ == TYPE_CNAME:
                print(f"CNAME\t{record.data.decode()}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            elif record.type_ == TYPE_MX:
                print(f"MX\t{record.data[1].decode()}\t{record.data[0]}\t{record.ttl}\t{'auth' if authoritive else 'nonauth'}")
            else:
                pass
    sock.close()
