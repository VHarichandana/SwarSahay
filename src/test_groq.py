from dotenv import load_dotenv
from groq import Groq
import os

# Load variables from .env
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Simple test
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Reply with only the word: Connected"
        }
    ]
)

print(response.choices[0].message.content)