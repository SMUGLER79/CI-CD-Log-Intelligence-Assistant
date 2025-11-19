from fastapi import FastAPI
from pydantic import BaseModel
from chunking import init_pinecone, query_index
from generate import clean_matches, generate_answer
from typing import List, Dict
import requests
import json
import os

OLLAMA_URL = os.getenv("OLLAMA_URL")
app = FastAPI(title="CI/CD Log Intelligent Assistant")
index = init_pinecone()

class Query(BaseModel):
    question: str
    job_id: str | None = None


def call_ollama(prompt: str) -> str:
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "temperature": 0.1
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    answer = ""

    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            answer += chunk.get("response", "")

    return answer.strip()


def build_prompt(question: str, docs: List[Dict]) -> str:
    context = "\n\n".join(
        f"[Chunk {i}] {m['metadata']['preview']}"
        for i, m in enumerate(docs, 1)
    )

    return f"""
        You are a CI/CD log analysis assistant.
        Use ONLY the information in the retrieved log chunks.

        Question:
        {question}

        Relevant Logs:
        {context}

        Answer:
        """.strip()


@app.post("/query")
async def query_logs(q: Query):
    filter_meta = {"job_id": {"$eq": q.job_id}} if q.job_id else None
    raw_matches = query_index(index, q.question, top_k=10, filter_meta=filter_meta)
    matches = clean_matches(raw_matches)

    if not matches:
        # result = generate_answer(q.question, [], max_tokens=0)
        
        return {
            "answer": "",
            "sources": [],
            #"prompt_used": result["prompt"],
        }

    result = generate_answer(q.question, matches)

    return {
        "answer": result.get("answer", ""),
        "sources": [m["id"] for m in matches],
        #"prompt_used": result["prompt"]
    }