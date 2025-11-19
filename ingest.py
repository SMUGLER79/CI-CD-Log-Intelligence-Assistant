import re
import os
from typing import List, Dict


def chunk_log_lines(lines: List[str], source = "jenkins_console_10000_logs.txt") -> List[Dict]:
    chunks = []
    current = []
    meta = {}
    idx = 0
    for line in lines:
        m = re.search(r'job=(?P<job>[^ ]+).*step=(?P<step>[^|]+)\|?\s*(?P<rest>.*)', line)
        
        if m:
            if current:
                chunks.append({
                    "text": "\n".join(current),
                    "job_id": meta.get("job_id"),
                    "step_name": meta.get("step_name"),
                    "status": meta.get("status"),
                    "timestamp": meta.get("timestamp"),
                    "source": source,
                    "chunk_id": f"{source}_{idx}"
                })

                idx += 1
                current = []

            meta = {
                "job_id": m.group("job"),
                "step_name": m.group("step").strip(),
                "status": "ERROR" if "ERROR" in line else ("WARN" if "WARN" in line else "INFO"),
                "timestamp": line.split("|")[0].strip()
            }

        current.append(line)

    if current:
        chunks.append({
            "text": "\n".join(current),
            "job_id": meta.get("job_id"),
            "step_name": meta.get("step_name"),
            "status": meta.get("status"),
            "timestamp": meta.get("timestamp"),
            "source": source,
            "chunk_id": f"{source}_{idx}"
        })
    
    return chunks

#test run
if __name__ == "__main__":
    with open("logs/jenkins_console_10000_logs.txt") as f:
        lines = f.read().splitlines()
    chunks = chunk_log_lines(lines, source="jenkins_console_10000_logs.txt")
    for c in chunks:
        print(c["chunk_id"], c["job_id"], c["step_name"], "---")
        print(c["text"][:200], "\n---\n")
