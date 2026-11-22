"""Answer keys for closed questions with explicit source answers.

Keys are relative course paths and the ordinal of the "Check Your Answer"
disclosure. Open-ended exercises and live captures use the source self-check.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: str
    fields: tuple
    kind: str = "exercise"
    choices: tuple = ()

    def check(self, answers):
        if not isinstance(answers, list) or len(answers) != len(self.fields):
            raise ValueError("Enter an answer for each field.")
        if any(not isinstance(value, str) or not value.strip() or len(value) > 256
               for value in answers):
            raise ValueError("Enter an answer of 1 to 256 characters in each field.")

        def matches(value, expected):
            if self.kind == "challenge" or expected.startswith("-"):
                return value.strip() == expected
            normalize = lambda text: " ".join(text.casefold().split())
            return normalize(value) == normalize(expected)

        return [any(matches(value, key) for key in accepted)
                for value, (_, accepted) in zip(answers, self.fields)]


# Labels name the original prompts. Explanations and examples stay in Markdown.
CHECKS = {("/network/" + page, number): fields for (page, number), fields in {
    ("networking-fundamentals/osi-model", 1): (
        ("Layer for IP addresses", ("3", "layer 3", "network")),
        ("Layer for MAC addresses", ("2", "layer 2", "data link")),
        ("Layer for TCP and UDP", ("4", "layer 4", "transport")),
        ("Layer 2 PDU", ("frame",)),
    ),
    ("networking-fundamentals/osi-model", 2): (
        ("Unplugged cable", ("1", "physical")),
        ("Routing by IP address", ("3", "network")),
        ("Switch looking up a MAC address", ("2", "data link")),
        ("Browser sending an HTTP request", ("7", "application")),
    ),
    ("networking-fundamentals/osi-model", 3): (
        ("Switch", ("2", "layer 2", "l2")), ("Router", ("3", "layer 3", "l3")),
        ("Basic packet-filter firewall", ("3/4", "l3/l4", "3 and 4", "layer 3 and 4")),
    ),
    ("networking-fundamentals/tcp-ip-model", 1): (
        ("UDP", ("transport",)), ("IPv4", ("internet",)),
        ("DNS", ("application",)), ("Ethernet", ("network access", "link")),
    ),
    ("networking-fundamentals/tcp-ip-model", 2): (
        ("Ethernet II", ("network access", "link")), ("IPv4", ("internet",)),
        ("TCP", ("transport",)), ("HTTP", ("application",)),
    ),
    ("networking-fundamentals/osi-vs-tcpip", 1): (
        ("TCP/IP layer for OSI Layer 3", ("internet",)),
        ("TCP/IP layer for OSI Layer 5", ("application",)),
    ),
    ("networking-fundamentals/encapsulation", 1): (
        ("Header with the destination port", ("tcp/udp", "tcp", "udp", "transport")),
        ("Header with the source MAC", ("ethernet", "link", "data link")),
    ),
    ("networking-fundamentals/encapsulation", 2): (
        ("Order of steps (A, B, C)", ("B, C, A", "B,C,A", "B C A", "BCA")),
    ),
    ("addressing/ipv4", 1): (
        ("Decimal 10 in 8-bit binary", ("00001010",)),
        ("Binary 11111111 in decimal", ("255",)),
    ),
    ("addressing/ipv4", 2): (
        ("8.8.8.8", ("public",)), ("172.20.4.9", ("private",)),
        ("172.32.0.1", ("public",)), ("127.0.0.1", ("loopback", "special")),
        ("169.254.10.5", ("link-local", "link local", "special")),
    ),
    ("addressing/mac-addresses", 1): (
        ("OUI", ("00:1A:2B", "00-1A-2B", "001A2B")),
        ("Meaning of ff:ff:ff:ff:ff:ff", ("broadcast", "local broadcast")),
    ),
    ("addressing/arp", 1): (
        ("How is the ARP request sent?", ("broadcast",)),
        ("ARP works across routers (true or false)", ("false", "no")),
    ),
    ("addressing/arp", 2): (("Whose MAC address?", ("default gateway", "gateway", "router")),),
    ("addressing/subnetting", 1): (
        ("Host bits", ("8",)), ("Total addresses", ("256",)), ("Usable hosts", ("254",)),
    ),
    ("addressing/subnetting", 3): (("Prefix length", ("/27", "27")),),
    ("protocols/http-https", 1): (
        ("HTTPS default port", ("443",)),
        ("HTTP status 404", ("not found", "resource not found", "page not found",
                            "the resource was not found")),
        ("What the Host header names", ("website", "host", "hostname", "domain", "virtual host")),
    ),
    ("protocols/http-https", 2): (
        ("Method", ("POST",)), ("URI", ("/login",)), ("Header", ("host",)),
        ("Is the password protected?", ("no", "false", "plain text", "plaintext")),
    ),
    ("protocols/dns", 1): (("Record type", ("A",)), ("Default port", ("53",))),
    ("protocols/dhcp", 1): (
        ("First message", ("discover",)), ("Second message", ("offer",)),
        ("Third message", ("request",)), ("Fourth message", ("ack", "acknowledgment")),
    ),
    ("protocols/ftp", 1): (
        ("Status 230", ("login successful", "successful login", "logged in")),
        ("What USER sends", ("username", "user name", "the username")),
    ),
    ("protocols/ssh", 1): (
        ("Default port", ("22",)), ("Can Wireshark read the session content?", ("no", "false")),
    ),
    ("protocols/icmp", 1): (("Ping request type", ("8", "type 8")), ("Uses ports?", ("no", "false"))),
    ("ports-and-tcp/ports-and-services", 1): (
        ("SSH", ("22",)), ("HTTPS", ("443",)), ("DNS", ("53",)), ("MySQL", ("3306",)),
    ),
    ("ports-and-tcp/ports-and-services", 2): (
        ("No response", ("filtered",)), ("RST response", ("closed",)),
    ),
    ("ports-and-tcp/tcp-handshake", 3): (
        ("SYN-ACK packet number", ("2", "packet 2")),
        ("Client IP and port", ("192.168.1.50:51514", "192.168.1.50 51514")),
        ("Server IP and port", ("93.184.216.34:80", "93.184.216.34 80")),
        ("Likely service", ("HTTP",)),
    ),
    ("network-devices", 1): (
        ("Forwards using MAC addresses", ("switch",)),
        ("Chooses a path using IP", ("router",)),
        ("Connects LAN to Internet and often does NAT", ("router", "gateway")),
    ),
    ("network-devices/network-topologies", 1): (
        ("Uses a central switch", ("star",)), ("Most resilient", ("mesh", "full mesh")),
        ("Links in a full mesh of five nodes", ("10", "10 links")),
    ),
    ("nmap/host-discovery", 2): (("Discovery option", ("-sn",)), ("Total addresses", ("16",))),
    ("nmap/introduction", 1): (
        ("First stage", ("host discovery",)), ("Second stage", ("port scanning", "port scan")),
        ("Third stage", ("version detection", "service detection")),
    ),
    ("nmap/port-scanning", 1): (
        ("Total ports scanned", ("1000", "1,000")), ("Filtered port", ("139",)),
    ),
    ("nmap/port-scanning", 2): (
        ("Option before a port list", ("-p",)), ("Option for all TCP ports", ("-p-",)),
    ),
    ("nmap/service-detection", 1): (
        ("First SSH port", ("22",)), ("Second SSH port", ("2222",)),
        ("Does the version string prove vulnerability?", ("no", "false")),
    ),
    ("nmap/service-detection", 2): (
        ("Service and version detection option", ("-sV",)), ("OS detection option", ("-O",)),
    ),
    ("nmap/reading-results", 1): (
        ("Which conclusion is valid?", ("A MySQL service is reachable on this host.",)),
    ),
    ("wireshark/capturing-packets", 1): (
        ("Filter style for port 80", ("capture", "capture filter", "bpf")),
        ("Filter applied before capture", ("capture", "capture filter", "bpf")),
    ),
    ("wireshark/display-filters", 1): (
        ("From 10.0.0.5", ("ip.src == 10.0.0.5", "ip.src==10.0.0.5", "ip.src eq 10.0.0.5")),
        ("To or from TCP port 443", ("tcp.port == 443", "tcp.port==443", "tcp.port eq 443")),
    ),
    ("wireshark/introduction", 1): (
        ("Pane with raw hex", ("packet bytes", "bytes", "3")),
        ("Pane with protocol layers", ("packet details", "details", "2")),
    ),
    ("wireshark/protocol-analysis", 1): (
        ("Stack from Ethernet to the application protocol",
         ("Ethernet / IPv4 / UDP / DNS", "Ethernet/IPv4/UDP/DNS", "Ethernet, IPv4, UDP, DNS")),
    ),
    ("wireshark/protocol-analysis", 4): (
        ("Request method", ("GET",)), ("Host header", ("www.lab.local",)),
        ("Request URI", ("/admin/login.php",)), ("Response status code", ("200", "200 ok")),
    ),
    ("wireshark/protocol-analysis", 6): (
        ("Sender IP", ("192.168.56.20",)), ("Sender MAC", ("08:00:27:bb:bb:02",)),
        ("Target IP", ("192.168.56.101",)), ("Target MAC", ("08:00:27:aa:aa:01",)),
    ),
}.items()}

CHOICES = {
    ("/network/nmap/reading-results", 1): (
        "The server is vulnerable to SQL injection.",
        "A MySQL service is reachable on this host.",
        "The SSH password is weak.",
    ),
}
