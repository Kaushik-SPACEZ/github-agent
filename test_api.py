"""
Quick test script to verify Groq API key works
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key loaded: {api_key[:20]}...")

try:
    client = Groq(api_key=api_key)
    
    # Simple test call
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "Say hello"}],
        temperature=0.5,
        max_tokens=50,
    )
    
    print("\n✅ API Key works!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ API Error: {e}")
    print("\nPossible issues:")
    print("1. API key is invalid or expired")
    print("2. API key doesn't have access to this model")
    print("3. Rate limit exceeded")
    print("\nGet a new key at: https://console.groq.com")