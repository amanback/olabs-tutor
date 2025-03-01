import os
from groq import Groq
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Check if API key is set
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is missing! Set it in the .env file or as an environment variable.")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Define the chat input
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "Explain Ohm's Law in simple terms."}
]

# Make the API call
completion = client.chat.completions.create(
    model="llama3-8b-8192",  # Ensure this model exists in Groq
    messages=messages,
    temperature=0.7,
    max_tokens=200,
    top_p=1,
    stream=True,
)

# Print the streaming response
print("\n🤖 AI Response:\n")
for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
