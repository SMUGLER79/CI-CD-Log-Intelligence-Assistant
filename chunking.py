import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from embedding_utils import load_model, embed_texts

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PIENCONE_INDEX_NAME")


def init_pinecone():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    model = load_model()
    dim = model.get_sentence_embedding_dimension()
    existing = pc.list_indexes().names()

    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=dim,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    return pc.Index(INDEX_NAME)


def upsert_chunks(index, chunks, batch_size=100):
    vectors = []

    for chunk in chunks:
        vec = embed_texts([chunk["text"]])[0].tolist()

        meta = {
            "job_id": chunk.get("job_id"),
            "step_name": chunk.get("step_name"),
            "status": chunk.get("status"),
            "timestamp": chunk.get("timestamp"),
            "source": chunk.get("source"),
            "chunk_id": chunk.get("chunk_id"),
            "preview": chunk["text"][:250]
        }

        vectors.append((chunk["chunk_id"], vec, meta))

    total = len(vectors)

    for i in range(0, total, batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)

    return total


def query_index(index, query_text, top_k=5, filter_meta=None): #metadata filtering
    qvec = embed_texts([query_text])[0].tolist()
    res = index.query(vector=qvec, top_k=top_k, include_metadata=True, filter=filter_meta)
    return res.get("matches", [])


#test run
if __name__ == "__main__":
    idx = init_pinecone()
    print("Index is ready.")

    test_vector = embed_texts(["ERROR: Failed Test at line 42"])[0]

    idx.upsert([
        ("test-id-1", test_vector.tolist())
    ])

    print("Inserted test vector successfully!")

