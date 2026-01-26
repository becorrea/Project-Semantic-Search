import sys
import os
from app.db.supabase_client import supabase
from app.embedding_service import EmbeddingService

def backfill_vectors():
    embedder = EmbeddingService()

    response = supabase.table("documents").select("*").execute()
    docs = response.data
    
    count = 0
    for doc in docs:
        if doc.get("embedding") is None:
            vector = embedder.embed(doc["content"])

            supabase.table("documents").update({"embedding": vector}).eq("id", doc["id"]).execute()
            count+=1
if __name__ == "__main__":
    backfill_vectors()