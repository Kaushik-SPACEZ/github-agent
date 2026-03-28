"""Standalone RAG demonstration — run this during the hackathon demo"""

from rag import RAGRetriever

# Initialize
print("🚀 Initializing RAG...")
rag = RAGRetriever()

# Sample repository with realistic security issues
python_files = [
    {
        'filename': 'auth.py',
        'content': '''
def authenticate(username, password):
    # WARNING: Hardcoded credentials
    if username == "admin" and password == "admin123":
        return True
    return False

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()
'''
    },
    {
        'filename': 'database.py',
        'content': '''
def execute_query(user_input):
    # WARNING: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query

def safe_execute(user_input):
    # Safe parameterized query
    query = "SELECT * FROM users WHERE name = ?"
    return query, (user_input,)
'''
    },
    {
        'filename': 'api.py',
        'content': '''
import os

def get_secret():
    # WARNING: hardcoded API key
    API_KEY = "sk-abc123supersecretkey"
    return API_KEY

def get_secret_safe():
    return os.getenv("API_KEY")
'''
    }
]

# Index
print("\n📚 Indexing repository...")
rag.index_repository(python_files)

# Show stats
stats = rag.get_stats()
print(f"\n📊 Statistics:")
print(f"  Total embeddings : {stats['total_embeddings']}")
print(f"  Embedding dim    : {stats['dimension']}")
print(f"  FAISS available  : {stats['faiss_available']}")
print(f"  Embedder model   : {stats['embedder_model']}")

# Test retrievals
print("\n" + "="*60)
print("🔍 Query: 'SQL injection' → retrieving similar code...")
print("="*60)
context = rag.get_context_for_file('database.py', 'SQL injection')
print(context)

print("="*60)
print("🔍 Query: 'hardcoded credentials' → retrieving similar code...")
print("="*60)
context2 = rag.get_context_for_file('auth.py', 'hardcoded credentials')
print(context2)

# Show persisted files
import os
db_path = "./rag/vector_db"
if os.path.exists(db_path):
    print("="*60)
    print("💾 Persisted vector database files:")
    for f in os.listdir(db_path):
        size = os.path.getsize(os.path.join(db_path, f))
        print(f"  {f}  ({size} bytes)")

print("\n✅ Demo complete!")