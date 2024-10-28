import re
import os
import json

# Function to fetch patterns from a log file
def fetch_patterns_from_log(log_file, patterns):
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found.")
        return []
    
    matched_lines = []
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                for pattern in patterns:
                    if re.search(pattern, line):
                        matched_lines.append(line.strip())
    except Exception as e:
        print(f"Error reading log file {log_file}: {str(e)}")
    return matched_lines

# Main function that processes the log files and patterns
def main():
    try:
        # Load inputs from environment variables
        log_files = json.loads(os.getenv("log_files", "[]"))
        log_patterns = json.loads(os.getenv("log_patterns", "[]"))

        if not log_files or not log_patterns:
            print("No log files or patterns provided.")
            return

        results = {}
        for log_file in log_files:
            results[log_file] = fetch_patterns_from_log(log_file, log_patterns)
        
        # Output results (can be ingested by Dynatrace)
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
