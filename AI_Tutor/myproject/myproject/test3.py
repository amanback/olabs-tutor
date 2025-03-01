import os
import requests
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Retrieve Groq API Key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ Function to moderate content using Groq API
def moderate_content(question_text):
    if not GROQ_API_KEY:
        raise ValueError("❌ ERROR: GROQ_API_KEY is missing. Check your .env file!")

    url = "https://api.groq.com/openai/v1/chat/completions"  # ✅ Correct API URL

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama3-8b-8192",  # ✅ Choose a valid model
        "messages": [
            {
                "role": "system",
                "content": """You are an AI moderator for an educational Q&A forum.
                Your job is to classify the following user question as either:
                - "study-related" (if it is about subjects like Physics, Math, Chemistry, Programming, Engineering, History, Biology, or any educational topic).
                - "not study-related" (if it is casual, off-topic, a joke, or hate speech).

                Respond with ONLY one word: "study-related" or "not study-related"."""
            },
            {"role": "user", "content": question_text}
        ],
        "temperature": 0.2,
        "max_tokens": 10,
        "top_p": 1,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            ai_response = response.json()["choices"][0]["message"]["content"].strip().lower()
            return ai_response
        except (KeyError, IndexError):
            return "Error: Invalid response format from API"
    else:
        return f"Error: {response.status_code}, {response.text}"


# ✅ **Test the function**
if __name__ == "__main__":
    user_question = input("Enter a question: ")
    classification = moderate_content(user_question)
    print(f"🔍 AI Classification: {classification}")
