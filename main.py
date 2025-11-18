from fastapi import FastAPI
from pydantic import BaseModel
from pinecone_client import init_pinecone, query_index
from generate import generate_answer

app = FastAPI()

index = init_pinecone()


class Query(BaseModel):
    job_id: str | None = None
    question: str


@app.post("/query")
async def query_logs(q: Query):
    filter_meta = {"job_id": {"$eq": q.job_id}} if q.job_id else None #filters by jobid (opt)

    matches = query_index(
        index,
        q.question,
        top_k=6,
        filter_meta=filter_meta
    )

    result = generate_answer(q.question, matches)

    return {
        "answer": result["answer"],
        "sources": [m["id"] for m in matches],
        "prompt_used": result["prompt"]
    }
