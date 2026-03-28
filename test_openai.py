"""
Test OpenAI API connection
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("OPENAI API TEST")
print("=" * 60)

print(f"\n1. API Key Check:")
print(f"   Key loaded: {api_key[:20]}...{api_key[-10:]}")

print(f"\n2. Creating OpenAI client...")
try:
    client = OpenAI(api_key=api_key)
    print("   ✅ Client created successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

print(f"\n3. Testing API call with gpt-4o-mini...")
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'Hello! OpenAI is working!'"}],
        temperature=0.5,
        max_tokens=20,
    )
    result = response.choices[0].message.content
    print(f"   ✅ SUCCESS!")
    print(f"   Response: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ OPENAI API IS WORKING!")
print("=" * 60)
print("\nYou can now run: streamlit run main.py")