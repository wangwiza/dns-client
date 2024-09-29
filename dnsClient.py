''' DNS Client (command line application)
Authors: William Wang 261113954
         Kevin-Ruikai Li 261120382 
'''
import argparse
import random
import sys
import socket
import struct
import dataclasses
from dataclasses import dataclass

RECURSIVE_FLAG = 256

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
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout in seconds')
    parser.add_argument('-r', '--max-retries', type=int, default=3, help='Maximum number of retries')
    parser.add_argument('-p', '--port', type=int, default=53, help='Port number')
    parser.add_argument('-mx', '--mx', action='store_true', help='MX flag')
    parser.add_argument('-ns', '--ns', action='store_true', help='NS flag')
    parser.add_argument('server', type=str, help='Server name')
    parser.add_argument('name', type=str, help='Name')
    return parser

def verify_command_line_args(args: argparse.Namespace) -> None:
    if args.timeout <= 0:
        print('Error: Timeout must be greater than 0')
        sys.exit(1)
    if args.max_retries <= 0:
        print('Error: Max retries must be greater than 0')
        sys.exit(1)
    if args.port < 0 or args.port > 65535:
        print('Error: Port number must be between 0 and 65535')
        sys.exit(1)
    if args.mx and args.ns:
        print('Error: Cannot have both MX and NS flags')
        sys.exit(1)
    if args.server[0] != '@':
        print('Error: Server name must start with @')
        sys.exit(1)
    server = args.server[1:]
    if len(server.split('.')) != 4 or not all(0 <= int(x) < 256 for x in server.split('.')):
        print(f'Error: Server name must be in the format of an IP address (x.x.x.x) and each x must be between 0 and 255')
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

def parse_dns_header() -> DNSHeader:
    pass

def parse_dns_answer():
    pass



if __name__ == "__main__":
    # Is invoked from the command line (STDIN);
    parser = create_command_line_parser()
    args = parser.parse_args()
    verify_command_line_args(args)

    print("DnsClient sending request for", args.name)
    print("Server:", args.server[1:])
    print("Request type:", "MX" if args.mx else "NS" if args.ns else "A")

    # Sends a query to the server for the given domain name using a UDP socket;
    query = build_dns_query(args.name, 15 if args.mx else 2 if args.ns else 1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(query, (args.server[1:], args.port))


    # Waits for the response to be returned from the server;

    response, _ = sock.recvfrom(1024)
    print(response)
