import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def moderate_content(question_text):
    """Calls the Groq API to classify questions as study-related or not."""
    if not GROQ_API_KEY:
        raise ValueError("❌ ERROR: GROQ_API_KEY is missing. Check your .env file!")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": """You are an AI moderator for an educational Q&A forum.
                Your job is to classify the given text as either:
                - "study-related" (if it contains academic, technical, or educational discussions related to subjects like Physics, Math, Chemistry, Programming, Engineering, History, Biology, or any STEM or humanities topic taught in schools and universities).
                - "not study-related" (if it is casual talk, a joke, unrelated discussion, social chat, opinion-based, promotional, hate speech, or spam).
                
                The response should be strictly ONE word: "study-related" or "not study-related".
                
                Examples:
                1. "What is Ohm's Law and how is it applied in electrical circuits?" → study-related
                2. "Who is your favorite football player?" → not study-related
                3. "Explain Newton's second law with examples." → study-related
                4. "What are some good movies to watch?" → not study-related
                
                Classify the following text accordingly:
                """
            },
            {"role": "user", "content": question_text}
        ],
        "temperature": 0,
        "max_tokens": 5,
        "top_p": 1,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            ai_response = response.json()["choices"][0]["message"]["content"].strip().lower()
            return ai_response
        except (KeyError, IndexError):
            return "error"
    else:
        return f"error: {response.status_code}, {response.text}"
