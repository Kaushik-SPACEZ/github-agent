"""Test similarity search accuracy (Test 2 from RAG_COMPLETE_GUIDE.md)"""

from rag import RAGRetriever

rag = RAGRetriever()
rag.clear_index()  # start clean

# Index multiple files
files = [
    {'filename': 'auth.py',   'content': 'def login(user, pwd):\n    if user == "admin" and pwd == "admin": return True\n    return False'},
    {'filename': 'db.py',     'content': 'def query(sql):\n    return f"SELECT * FROM t WHERE x = {sql}"'},
    {'filename': 'api.py',    'content': 'def handle_request(req):\n    return process(req.body)'},
]
rag.index_repository(files)

# Search for authentication-related code
results = rag.retrieve_context("user authentication and login", k=3)

print(f"Found {len(results)} similar chunks:")
for i, r in enumerate(results, 1):
    print(f"\n{i}. File     : {r['filename']}")
    print(f"   Distance : {r['distance']:.4f}")
    print(f"   Text     : {r['text'][:80]}...")

# auth.py should rank highest for authentication query
assert len(results) > 0, "No results returned"
assert results[0]['filename'] == 'auth.py', \
    f"Expected auth.py as top result, got {results[0]['filename']}"

print("\n✅ Similarity search working correctly!")