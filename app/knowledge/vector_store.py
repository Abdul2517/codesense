import os
import chromadb
from chromadb.config import Settings

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name="merged_prs",
    metadata={"heuristic": "cosine"}
)

def ingest_merged_pr(pr_number: int, pr_title: str, diff: str, repo: str):
    try:
        doc_id = f"{repo}_{pr_number}"
        collection.upsert(
            ids=[doc_id],
            documents=[diff[:5000]],
            metadatas=[{
                "pr_number": pr_number,
                "pr_title": pr_title,
                "repo": repo
            }]
        )
        print(f"Ingested PR #{pr_number} into knowledge base")
        return True
    except Exception as e:
        print(f"Error ingesting PR #{pr_number}: {e}")
        return False

def get_similar_prs(query: str, n_results: int = 3) -> list:
    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )
        return results.get("documents", [[]])[0]
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        return []

def get_pr_count() -> int:
    try:
        return collection.count()
    except:
        return 0