"""Benchmark RAG performance (Test 3 from RAG_COMPLETE_GUIDE.md)"""

import time
from rag import RAGRetriever

rag = RAGRetriever()
rag.clear_index()

# Generate 100 test files
test_files = []
for i in range(100):
    test_files.append({
        'filename': f'file_{i}.py',
        'content': f'def function_{i}(x, y):\n    """Function number {i}"""\n    return x + y + {i}\n' * 5
    })

# Benchmark indexing
print("⏱  Benchmarking indexing (100 files)...")
start = time.time()
rag.index_repository(test_files)
index_time = time.time() - start

# Benchmark retrieval
print("⏱  Benchmarking retrieval (100 queries)...")
start = time.time()
for _ in range(100):
    rag.retrieve_context("function definition with parameters", k=5)
retrieval_time = time.time() - start

stats = rag.get_stats()
print(f"\n📊 Performance Results:")
print(f"  Indexing time   : {index_time:.2f}s for 100 files")
print(f"  Retrieval time  : {retrieval_time/100*1000:.2f}ms per query (avg over 100 queries)")
print(f"  Total embeddings: {stats['total_embeddings']}")
print(f"  Embedding dim   : {stats['dimension']}")

assert stats['total_embeddings'] > 0, "No embeddings created"
print("\n✅ Performance benchmark complete!")