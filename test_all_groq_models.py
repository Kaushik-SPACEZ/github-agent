"""
Test all possible Groq models to find which ones work
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

print("=" * 70)
print("TESTING ALL GROQ MODELS")
print("=" * 70)

client = Groq(api_key=api_key)

# Comprehensive list of Groq models to test
models_to_test = [
    # Llama 3.1 models
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama-3.1-405b-reasoning",
    
    # Llama 3.2 models
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
    
    # Llama 3.3 models
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-specdec",
    
    # Llama 3 models (older)
    "llama3-8b-8192",
    "llama3-70b-8192",
    "llama3-groq-8b-8192-tool-use-preview",
    "llama3-groq-70b-8192-tool-use-preview",
    
    # Mixtral models
    "mixtral-8x7b-32768",
    
    # Gemma models
    "gemma-7b-it",
    "gemma2-9b-it",
]

working_models = []
failed_models = []

print(f"\nTesting {len(models_to_test)} models...\n")

for i, model in enumerate(models_to_test, 1):
    print(f"{i:2d}. Testing: {model:45s} ", end="")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'ok'"}],
            temperature=0.5,
            max_tokens=5,
        )
        result = response.choices[0].message.content
        print(f"✅ WORKS! Response: {result}")
        working_models.append(model)
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            print(f"❌ 403 Forbidden")
            failed_models.append((model, "403 Forbidden"))
        elif "404" in error_msg:
            print(f"❌ 404 Not Found")
            failed_models.append((model, "404 Not Found"))
        elif "401" in error_msg:
            print(f"❌ 401 Unauthorized")
            failed_models.append((model, "401 Unauthorized"))
        else:
            print(f"❌ Error: {error_msg[:50]}")
            failed_models.append((model, error_msg[:50]))

print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)

if working_models:
    print(f"\n✅ WORKING MODELS ({len(working_models)}):")
    for model in working_models:
        print(f"   • {model}")
    print(f"\n🎉 SUCCESS! Use any of these models in your app!")
else:
    print(f"\n❌ NO WORKING MODELS FOUND")
    print(f"\nThis means:")
    print(f"   1. API key doesn't have model access")
    print(f"   2. Account needs to be activated")
    print(f"   3. Or there's a regional restriction")
    print(f"\n💡 Solutions:")
    print(f"   • Check Groq console: https://console.groq.com")
    print(f"   • Try a different Groq account")
    print(f"   • Or switch to OpenAI API")

print(f"\n📊 Failed: {len(failed_models)} models")
print("=" * 70)