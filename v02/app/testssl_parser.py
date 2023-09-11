import re


def testssl_parser(content):
    # Extract target information
    ip_pattern = re.compile(r"Testing all IPv4 addresses \(port 443\): ([\d., ]+)")
    ip_match = ip_pattern.search(content)

    # Extract protocol testing results
    protocol_pattern = re.compile(r"(\w+[\d.]+)\s+(not offered|offered)")
    protocol_matches = protocol_pattern.findall(content)

    # Extract cipher categories
    cipher_pattern = re.compile(r"^(.+?)\s{2,}(not offered \(OK\)|offered \(OK\)|not offered|offered)$", re.MULTILINE)
    cipher_matches = cipher_pattern.findall(content)

    # Extract vulnerabilities
    vulnerabilities = re.findall(r"\(CRITICAL\)\s+(.+?)\n", content)

    results = {
        'target_info': {
            'ip_addresses': ip_match.group(1).split() if ip_match else []
        },
        'protocols': {match[0]: match[1] for match in protocol_matches},
        'ciphers': {match[0].strip(): match[1] for match in cipher_matches},
        'vulnerabilities': vulnerabilities
    }

    return results
