"""
Simple test script to verify memory system installation and functionality.
Run this after installing dependencies to ensure everything works.
"""

import sys
import os

print("=" * 60)
print("Memory System Installation Test")
print("=" * 60)

# Test 1: Check Python version
print("\n[1/7] Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 8:
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
else:
    print(f"❌ Python {version.major}.{version.minor} (need 3.8+)")
    sys.exit(1)

# Test 2: Import core dependencies
print("\n[2/7] Testing core dependencies...")
try:
    import sentence_transformers
    import chromadb
    import flask
    import openai
    from dotenv import load_dotenv
    print("✅ All core packages installed")
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: Load environment variables
print("\n[3/7] Testing environment configuration...")
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key.startswith('sk-'):
    print(f"✅ OpenAI API key loaded (sk-...{api_key[-4:]})")
else:
    print("⚠️  OpenAI API key not found or invalid")
    print("Create .env file with: OPENAI_API_KEY=your_key_here")

# Test 4: OpenAI API key
print("\n[4/7] Testing OpenAI API key...")
api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key.startswith('sk-'):
    print(f"✅ OpenAI API key loaded (sk-...{api_key[-4:]})")
else:
    print("⚠️  OpenAI API key not found or invalid")
    print("Create .env file with: OPENAI_API_KEY=your_key_here")

# Test 5: SentenceTransformer
print("\n[5/7] Testing embedding model...")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode("Test text")
    print(f"✅ Embedding model loaded (dimension: {len(embedding)})")
except Exception as e:
    print(f"❌ Embedding model error: {e}")
    sys.exit(1)

# Test 6: ChromaDB
print("\n[6/7] Testing ChromaDB...")
try:
    from chromadb import PersistentClient
    client = PersistentClient(path="./test_chroma_db")
    collection = client.get_or_create_collection("test_collection")
    print("✅ ChromaDB initialized successfully")
    # Cleanup
    import shutil
    shutil.rmtree("./test_chroma_db", ignore_errors=True)
except Exception as e:
    print(f"❌ ChromaDB error: {e}")
    sys.exit(1)

# Test 7: Import custom modules
print("\n[7/7] Testing custom modules...")
try:
    from memory import MemoryCompressor, VectorMemoryStore, MemoryRetriever
    from nlp import EntityExtractor
    from services import PromptBuilder
    print("✅ All custom modules imported successfully")
except ImportError as e:
    print(f"❌ Module import error: {e}")
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\nYour memory system is ready to use!")
print("\nNext steps:")
print("1. Create .env file with your OPENAI_API_KEY")
print("\nNext steps:")
print("2. Run: python api.py")
print("3. Test API: curl http://localhost:5001/health")
print("\n" + "=" * 60)
