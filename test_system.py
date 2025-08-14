#!/usr/bin/env python3
"""Test script to verify the RAG system components."""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.database.client import SupabaseClient
from src.ingestion.embeddings import EmbeddingGenerator
from src.generation.agent import RAGAgent


async def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        db_client = SupabaseClient()
        documents = await db_client.get_documents_list(limit=1)
        print(f"✅ Database connection successful. Found {len(documents)} documents.")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_embeddings():
    """Test embedding generation."""
    print("Testing embedding generation...")
    try:
        embedding_gen = EmbeddingGenerator()
        await embedding_gen.test_connection()
        embeddings = await embedding_gen.generate_embeddings(["test query"])
        print(
            f"✅ Embedding generation successful. Got {len(embeddings[0])} dimensions."
        )
        return True
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False


async def test_rag_agent():
    """Test RAG agent."""
    print("Testing RAG agent...")
    try:
        agent = RAGAgent()
        health = await agent.health_check()
        print(f"✅ RAG agent initialization successful. Health: {health}")
        return True
    except Exception as e:
        print(f"❌ RAG agent initialization failed: {e}")
        return False


async def test_full_pipeline():
    """Test the full RAG pipeline."""
    print("Testing full RAG pipeline...")
    try:
        # Initialize components
        db_client = SupabaseClient()
        embedding_gen = EmbeddingGenerator()
        agent = RAGAgent()

        # Test query
        response = await agent.query(
            question="What is the main topic covered in the documents?",
            db_client=db_client,
            embedding_generator=embedding_gen,
        )

        print("✅ Full pipeline test successful!")
        print(f"   Answer: {response.answer[:100]}...")
        print(f"   Confidence: {response.confidence}")
        print(f"   Sources: {len(response.sources)}")
        return True

    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting RAG System Tests")
    print("RAG System Component Tests")
    print("=" * 50)

    tests = [
        test_database_connection,
        test_embeddings,
        test_rag_agent,
        test_full_pipeline,
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
        print()

    # Summary
    print("=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("The RAG system is ready to use.")
    else:
        print(f"⚠️  Some tests failed. ({passed}/{total} passed)")
        print("Please check the errors above and fix any issues.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
