import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY1")
GROQ_API_URL = os.getenv("GROQ_API_URL")

def classify_message():
    user_message = input("Enter a message to classify: ").strip()
    
    if not user_message:
        print("Error: Message cannot be empty.")
        return

    # Define the strict moderation prompt
    prompt_text = (
        "You are a strict content moderation AI designed for a Q&A forum focused only on study-related discussions. "
        "Your task is to classify user messages as either:\n"
        "1. \"study-related\" - Only allow messages that are strictly academic, educational, or related to learning.\n"
        "2. \"not study-related\" - Reject casual conversations, off-topic messages, and hate speech.\n\n"
        "### Examples:\n"
        "✅ \"What is the integral of x^2?\" → study-related\n"
        "✅ \"Can someone explain Newton’s Third Law?\" → study-related\n"
        "❌ \"Hey, what’s up?\" → not study-related\n"
        "❌ \"You’re dumb!\" → not study-related\n\n"
        "### Task:\n"
        "Classify the following user message strictly as either \"study-related\" or \"not study-related\". "
        "Only return the classification label as the output."
    )

    # API request payload
    payload = {
        "text": user_message,
        "prompt": prompt_text
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            print("\n🔹 Classification Result:", result)
        else:
            print(f"\n❌ API Error: {response.status_code}")
            print("Details:", response.text)

    except requests.RequestException as e:
        print("\n❌ Request Failed:", str(e))

if __name__ == "__main__":
    classify_message()
