"""
Test search functionality with debugging
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").absolute()))


async def test_search():
    from src.database.client import SupabaseClient
    from src.ingestion.embeddings import EmbeddingGenerator

    db = SupabaseClient()
    emb = EmbeddingGenerator()

    # Get documents
    docs = await db.get_documents_list(limit=5)
    print(f"Documents: {len(docs)}")
    for doc in docs:
        print(f"  - {doc.get('filename', 'Unknown')}: {doc.get('status', 'Unknown')}")

    # Test search with very low threshold
    embeddings = await emb.generate_embeddings(["Gabriel name person applicant"])
    results = await db.search_similar_chunks(
        query_embedding=embeddings[0], limit=5, similarity_threshold=0.1
    )
    print(f"Search results with 0.1 threshold: {len(results)}")
    for i, result in enumerate(results):
        print(f"  {i + 1}. Similarity: {result.get('similarity', 'N/A')}")
        print(f"      Content: {result.get('content', 'N/A')[:100]}...")

    # Test with even lower threshold
    results2 = await db.search_similar_chunks(
        query_embedding=embeddings[0], limit=5, similarity_threshold=0.01
    )
    print(f"Search results with 0.01 threshold: {len(results2)}")
    for i, result in enumerate(results2):
        print(f"  {i + 1}. Similarity: {result.get('similarity', 'N/A')}")
        print(f"      Content: {result.get('content', 'N/A')[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_search())
