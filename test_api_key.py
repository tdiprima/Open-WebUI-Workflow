import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response)
except Exception as e:
    print(f"Error: {e}")
