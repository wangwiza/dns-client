# DNS Client - Python Implementation

This repository contains a Python-based DNS client that sends DNS queries to a specified server and parses the responses. It supports querying for various DNS record types, including `A`, `NS`, and `MX` records.

## Features

- Query DNS servers for `A`, `NS`, and `MX` records.
- Command-line interface for flexible use.
- Support for custom timeout, retries, and port configurations.
- Response parsing for `Answer`, `Authority`, and `Additional` sections.
- Error handling for common DNS response codes.

## Requirements

- Python 3.7 or higher.

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/your-username/dns-client.git
cd dns-client
```

## Usage

Run the DNS client using the command line:

```bash
python dnsClient.py [-t TIMEOUT] [-r MAX_RETRIES] [-p PORT] [-mx|-ns] @SERVER NAME
```

### Parameters:
- `-t TIMEOUT`: Timeout in seconds (default: 5 seconds).
- `-r MAX_RETRIES`: Maximum number of retries for queries (default: 3 retries).
- `-p PORT`: Port number for the DNS server (default: 53).
- `-mx`: Query for MX records.
- `-ns`: Query for NS records.
- `@SERVER`: DNS server's IP address, prefixed with `@` (e.g., `@8.8.8.8`).
- `NAME`: Domain name to query.

### Examples:

1. Query `A` records for `example.com` using Google's DNS server:
   ```bash
   python dnsClient.py @8.8.8.8 example.com
   ```

2. Query `MX` records for `example.com` with a timeout of 3 seconds:
   ```bash
   python dnsClient.py -t 3 -mx @8.8.8.8 example.com
   ```

3. Query `NS` records for `example.com` with a custom port:
   ```bash
   python dnsClient.py -p 5353 -ns @8.8.8.8 example.com
   ```

## Output

The client displays the query details, including:
- The requested domain name.
- Server and request type.
- Response time and retry attempts.
- Parsed DNS records from the response, including:
  - **Answer Section**: Resolved records (e.g., IP addresses, CNAMEs).
  - **Additional Section**: Supplementary records (e.g., additional IPs).

## Error Handling

The client provides detailed error messages for:
- Invalid command-line arguments.
- DNS server response errors (`Format error`, `Server failure`, `Name error`, etc.).
- Timeout and retry limits.

## Code Structure

- **DNSHeader**: Represents the DNS packet header.
- **DNSQuestion**: Encodes DNS query details.
- **DNSRecord**: Represents DNS resource records.
- **DNSPacket**: Encapsulates a complete DNS response.

### Key Functions:

- `build_dns_query`: Constructs a DNS query packet.
- `parse_dns_packet`: Parses the DNS server's response.
- `verify_command_line_args`: Validates command-line arguments.
- `decode_dns_name`: Decodes DNS names from the response.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Contributions, issues, and feature requests are welcome. Feel free to fork the repository and submit a pull request.

---

For any questions or support, please open an issue or reach out to the repository maintainer. Happy querying! 🚀

Program written and tested using Python 3.11.1
