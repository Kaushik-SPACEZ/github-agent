"""End-to-end RAG pipeline test (Test 4 from RAG_COMPLETE_GUIDE.md)"""

from rag import RAGRetriever

# Create test repository
test_repo = {
    'vulnerable.py': '''
def unsafe_query(user_input):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_input}"
    return query
''',
    'safe.py': '''
def safe_query(user_input):
    # Parameterized query — safe from SQL injection
    query = "SELECT * FROM users WHERE id = ?"
    return query, (user_input,)
'''
}

# Initialize RAG
rag = RAGRetriever()
rag.clear_index()

files = [{'filename': k, 'content': v} for k, v in test_repo.items()]
rag.index_repository(files)

# Get context for vulnerable file
context = rag.get_context_for_file('vulnerable.py', 'SQL injection')
print("Context retrieved for vulnerable.py:")
print(context)

# The safe.py or its content should surface as similar pattern
assert context != "", "Context should not be empty"
print("✅ RAG provides relevant code context!")

# Test that clear works
rag.clear_index()
stats = rag.get_stats()
assert stats['total_embeddings'] == 0, "Index should be empty after clear"
print("✅ clear_index() works correctly!")

print("\n🎉 End-to-end test passed!")