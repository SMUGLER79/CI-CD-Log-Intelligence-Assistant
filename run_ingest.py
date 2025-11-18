from pinecone_client import init_pinecone, upsert_chunks
from ingest import chunk_log_lines

def main():
    idx = init_pinecone()

    with open("logs/github_actions_10000_logs.txt", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    chunks = chunk_log_lines(lines, source="ci_log.txt")
    count = upsert_chunks(idx, chunks, batch_size=50)
    print(f"Upserted {count} chunks")

if __name__ == "__main__":
    main()
