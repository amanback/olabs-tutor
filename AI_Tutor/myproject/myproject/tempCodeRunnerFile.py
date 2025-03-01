import os
from groq import Groq

# ✅ Load API Key from Environment Variable (Make sure it's set)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("no")
    
