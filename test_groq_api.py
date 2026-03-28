"""
Comprehensive Groq API test - checks multiple aspects
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("GROQ API COMPREHENSIVE TEST")
print("=" * 60)

# Load environment
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

print(f"\n1. API Key Check:")
print(f"   Key loaded: {api_key[:20]}...{api_key[-10:]}")
print(f"   Key length: {len(api_key)} characters")

# Try importing Groq
print(f"\n2. Import Check:")
try:
    from groq import Groq
    print("   ✅ Groq library imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import Groq: {e}")
    exit(1)

# Try creating client
print(f"\n3. Client Creation:")
try:
    client = Groq(api_key=api_key)
    print("   ✅ Groq client created successfully")
except Exception as e:
    print(f"   ❌ Failed to create client: {e}")
    exit(1)

# Test different models
models_to_test = [
    "llama3-8b-8192",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
]

print(f"\n4. Model Access Tests:")
for model in models_to_test:
    print(f"\n   Testing: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'test'"}],
            temperature=0.5,
            max_tokens=10,
        )
        result = response.choices[0].message.content
        print(f"   ✅ {model} works!")
        print(f"      Response: {result}")
        break  # If one works, we're good
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            print(f"   ❌ 403 Forbidden - No access to this model")
        elif "401" in error_msg:
            print(f"   ❌ 401 Unauthorized - Invalid API key")
        elif "429" in error_msg:
            print(f"   ❌ 429 Rate Limited - Too many requests")
        else:
            print(f"   ❌ Error: {error_msg[:100]}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

print("\n📋 Summary:")
print("   If all models show 403: API key doesn't have model access")
print("   If 401: API key is invalid")
print("   If 429: Rate limited (wait and retry)")
print("   If one model works: Use that model in the app!")

print("\n🔗 Get help at: https://console.groq.com")