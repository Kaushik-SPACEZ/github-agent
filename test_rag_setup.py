"""Test RAG installation and setup"""

print("Testing RAG setup...")

# Test 1: Import modules
try:
    from rag import RAGRetriever, VectorStore, CodeEmbedder
    print("✅ RAG modules imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Check FAISS
try:
    import faiss
    print(f"✅ FAISS available (version: {faiss.__version__})")
except ImportError:
    print("⚠️ FAISS not installed (RAG will use fallback)")

# Test 3: Check sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers available")
except ImportError:
    print("⚠️ sentence-transformers not installed (will use dummy embeddings)")

# Test 4: Initialize RAG
try:
    rag = RAGRetriever()
    stats = rag.get_stats()
    print(f"✅ RAG initialized: {stats}")
except Exception as e:
    print(f"❌ RAG initialization failed: {e}")
    exit(1)

print("\n🎉 RAG setup complete!")