from groq import Groq

# Replace with your actual API key
API_KEY = "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"

client = Groq(api_key=API_KEY)

try:
    response = client.chat.completions.create(
        model="llama-3.1-405b-reasoning",
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )

    print("✅ API Key is working fine")
    print("Response:", response.choices[0].message.content)

except Exception as e:
    print("❌ API Key failed")
    print("Error:", e)