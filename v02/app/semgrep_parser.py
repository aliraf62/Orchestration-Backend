
import re

def semgrep_parser(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    results = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if the line resembles a file path
        if re.match(r"\w[-\w./]+\w", line):
            file_path = line
            finding_type = lines[i + 1].strip() if i + 1 < len(lines) else ''
            
            # Attempt to capture the description until a URL or another file path is found
            description_lines = []
            j = i + 2
            while j < len(lines) and not re.match(r"https?://sg.run/\w+|\w[-\w./]+\w", lines[j]):
                description_lines.append(lines[j].strip())
                j += 1
            description = " ".join(description_lines)
            
            # Attempt to capture the details link
            details_link = lines[j].strip() if j < len(lines) and "https://sg.run/" in lines[j] else ''
            
            results.append({
                'file_path': file_path,
                'finding_type': finding_type,
                'description': description,
                'details_link': details_link
            })
            
            i = j + 1 if details_link else j
        else:
            i += 1

    return results


def stepwise_semgrep_parser(data):
    # Placeholder function for stepwise_semgrep_parser
    # This function needs to be implemented to handle the parsing of semgrep results
    # For now, it simply returns the data as-is
    return data
