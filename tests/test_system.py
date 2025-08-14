#!/usr/bin/env python3
"""Test script to verify the RAG system components."""

import asyncio
import sys
from pathlib import Path

# Add project root to path before imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup to avoid lint warnings  # noqa: E402
from src.database.client import SupabaseClient  # noqa: E402
from src.generation.agent import RAGAgent  # noqa: E402
from src.ingestion.embeddings import EmbeddingGenerator  # noqa: E402


async def test_database_connection():
    """Test database connection and basic functionality."""
    print("Testing database connection...")
    try:
        db_client = SupabaseClient()
        # Test connection by getting documents list
        documents = await db_client.get_documents_list(limit=1)
        print(f"✅ Database connection successful. Found {len(documents)} documents.")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_embeddings():
    """Test embedding generation with OpenAI."""
    print("Testing embedding generation...")
    try:
        embedding_gen = EmbeddingGenerator()
        # Test connection to OpenAI
        await embedding_gen.test_connection()
        # Generate test embeddings
        embeddings = await embedding_gen.generate_embeddings(["test query"])
        print(
            f"✅ Embedding generation successful. Got {len(embeddings[0])} dimensions."
        )
        return True
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False


async def test_rag_agent():
    """Test RAG agent initialization and health check."""
    print("Testing RAG agent...")
    try:
        agent = RAGAgent()
        health = agent.health_check()  # Not async - returns dict with health status
        print(f"✅ RAG agent initialization successful. Health: {health}")
        return True
    except Exception as e:
        print(f"❌ RAG agent initialization failed: {e}")
        return False


async def test_full_pipeline():
    """Test the complete RAG pipeline end-to-end."""
    print("Testing full RAG pipeline...")
    try:
        # Initialize all components
        db_client = SupabaseClient()
        embedding_gen = EmbeddingGenerator()
        agent = RAGAgent()

        # Test with a sample query
        test_question = "What is the main topic covered in the documents?"
        response = await agent.query(
            question=test_question,
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
