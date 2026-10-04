from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from matcher.bm25_search import load_jobs

# Where vectors are saved on disk
DB_FOLDER = Path("data/vector_db")

# Small free model that turns text into numbers (embeddings)
EMBED_MODEL = "all-MiniLM-L6-v2"


def open_job_collection():
    """Open (or create) the vector database collection named 'jobs'."""
    DB_FOLDER.mkdir(parents=True, exist_ok=True)

    # Disk-backed Chroma DB
    db = chromadb.PersistentClient(path=str(DB_FOLDER))

    # This function turns text -> vector automatically
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    # Like a table inside the DB
    collection = db.get_or_create_collection(
        name="jobs",
        embedding_function=embedder,
    )
    return collection


def build_index_if_needed():
    """
    Put all jobs into the vector DB once.
    If they are already there, just reuse them.
    """
    collection = open_job_collection()

    # Already built? Do nothing.
    if collection.count() > 0:
        return collection

    jobs = load_jobs()  # same jobs BM25 uses

    ids = []
    texts = []
    extras = []

    for job in jobs:
        ids.append(job["id"])
        texts.append(job["text"])          # this text gets embedded
        extras.append({
            "title": job["title"],
            "employer": job["employer"],
        })

    # Save jobs as vectors
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=extras,
    )
    return collection


def search_jobs(resume_text, top_k=10):
    """
    1) Make sure job vectors exist
    2) Embed the resume
    3) Find the closest jobs
    """
    collection = build_index_if_needed()

    # Ask Chroma: which jobs are closest in meaning to this resume?
    answer = collection.query(
        query_texts=[resume_text],
        n_results=top_k,
    )

    results = []
    matched_ids = answer["ids"][0]
    matched_meta = answer["metadatas"][0]
    matched_dist = answer["distances"][0]

    for i in range(len(matched_ids)):
        distance = float(matched_dist[i])   # smaller = closer
        similarity = 1 - distance           # flip so bigger = better

        results.append({
            "id": matched_ids[i],
            "title": matched_meta[i]["title"],
            "employer": matched_meta[i]["employer"],
            "score": round(similarity, 3),
        })

    return results