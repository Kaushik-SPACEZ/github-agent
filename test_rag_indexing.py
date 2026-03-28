"""Test RAG indexing with sample code"""

from rag import RAGRetriever

# Initialize RAG
rag = RAGRetriever()

# Sample Python files
python_files = [
    {
        'filename': 'main.py',
        'content': '''
def calculate_total(items):
    """Calculate total price of items"""
    total = 0
    for item in items:
        total += item['price']
    return total

def apply_discount(total, discount_percent):
    """Apply discount to total"""
    discount = total * (discount_percent / 100)
    return total - discount
'''
    },
    {
        'filename': 'utils.py',
        'content': '''
class DatabaseHelper:
    """Helper class for database operations"""
    
    def __init__(self, connection_string):
        self.conn = connection_string
    
    def execute_query(self, query):
        """Execute SQL query"""
        # WARNING: This is vulnerable to SQL injection!
        return f"SELECT * FROM users WHERE name = '{query}'"
'''
    }
]

# Index the repository
print("Indexing repository...")
rag.index_repository(python_files)

# Check statistics
stats = rag.get_stats()
print(f"\n📊 Statistics:")
print(f"  Total embeddings: {stats['total_embeddings']}")
print(f"  Dimension: {stats['dimension']}")
print(f"  FAISS available: {stats['faiss_available']}")

# Test retrieval
print("\n🔍 Testing retrieval...")
context = rag.get_context_for_file('utils.py', 'SQL injection')
print(context)

print("\n✅ Indexing test complete!")