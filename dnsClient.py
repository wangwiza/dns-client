''' DNS Client (command line application)
Authors: William Wang 261113954
         Kevin-Ruikai Li 261120382 
'''
import argparse
import sys
import socket


# Is invoked from the command line (STDIN);
# python dnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name

parser = argparse.ArgumentParser(
                    prog='Command Line DNS Client',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout in seconds')
parser.add_argument('-r', '--max-retries', type=int, default=3, help='Maximum number of retries')
parser.add_argument('-p', '--port', type=int, default=53, help='Port number')
parser.add_argument('-mx', '--mx', action='store_true', help='MX flag')
parser.add_argument('-ns', '--ns', action='store_true', help='NS flag')
parser.add_argument('server', type=str, help='Server name')
parser.add_argument('name', type=str, help='Name')

args = parser.parse_args()

if args.server[0] != '@':
    print('Error: Server name must start with @')
    sys.exit(1)

server = args.server[1:]
if server.split('.').count != 4 or not all(0 <= int(x) < 256 for x in server.split('.')):
    print('Error: Server name must be in the format of an IP address (x.x.x.x) and each x must be between 0 and 255')
    sys.exit(1)

# Sends a query to the server for the given domain name using a UDP socket;

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Waits for the response to be returned from the server;

# Interprets the response and outputs the result to terminal display (STDOUT).

