''' DNS Client (command line application)
Authors: William Wang 261113954
         Kevin-RuiKai Li  
'''
import argparse


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

args = parser.parse_args()
print(args.mx)
# Sends a query to the server for the given domain name using a UDP socket;

# Waits for the response to be returned from the server;

# Interprets the response and outputs the result to terminal display (STDOUT).

