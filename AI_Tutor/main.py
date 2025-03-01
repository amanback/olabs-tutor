from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAI
from get_embedding_function import get_embedding_function
from fastapi.middleware.cors import CORSMiddleware
from collections import deque
from typing import Dict
import json
from langchain_community.llms import Ollama
import re


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# db and embedding function
embedding_function = get_embedding_function()
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
retriever = db.as_retriever(search_type="mmr", search_kwargs={"fetch_k": 10, "k": 5})

# gemini
llm = GoogleGenerativeAI(model="gemini-1.5-pro", api_key="AIzaSyDIi7HJ0Hb-8qT7y_vz9IAfnkseZjDWm_U")


#memory storage (stores last 5 interactions per user)
conversation_memory: Dict[str, deque] = {}

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query text")
    user_id: str = Field(..., min_length=1, description="Unique user identifier")
    conversation_history: list = Field(default=[], description="Conversation history")

def format_response(text):
    """
    Format the response text:
    1. Remove asterisks which are used for bold markdown
    2. Clean up formatting
    3. Apply proper paragraph spacing
    """
    #remove asterisks
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    #remove markdown section identifiers
    text = re.sub(r'^---$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^Answer:$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^Context:$', '', text, flags=re.MULTILINE)
    
    #remove redundant newlines but preserve paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Clean up any remaining special markdown formatting
    text = re.sub(r'#+ ', '', text)
    
    # Ensure numbered lists are properly formatted
    text = re.sub(r'(\d+)\.\s+', r'\1. ', text)
    
    return text.strip()

@app.post("/query")
async def query_rag(request: Request):
    try:
        # Log the raw request data
        raw_data = await request.json()
        print("Received request:", json.dumps(raw_data, indent=2))

        # Validate request format
        if "query" not in raw_data or "user_id" not in raw_data:
            raise HTTPException(status_code=400, detail="Both 'query' and 'user_id' are required in the request.")

        data = QueryRequest(**raw_data)  # Validate fields with Pydantic

        user_id = data.user_id.strip()
        query_text = data.query.strip()
        
        # Use conversation_history if provided, otherwise use the stored memory
        if hasattr(data, 'conversation_history') and data.conversation_history:
            # Extract conversation content from the history
            conversation_content = []
            for msg in data.conversation_history:
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role and content:
                    conversation_content.append(f"{role.capitalize()}: {content}")
            past_conversations = "\n".join(conversation_content)
        else:
            # Retrieve user conversation history from memory
            if user_id not in conversation_memory:
                conversation_memory[user_id] = deque(maxlen=5)
            past_conversations = "\n".join(conversation_memory[user_id])

        # Retrieve relevant documents
        relevant_docs = retriever.get_relevant_documents(query_text)
        doc_context = "\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else "No relevant documents found."

        # Prepare context with memory and documents
        full_context = f"""
Previous Conversation:
{past_conversations}

Reference Documents:
{doc_context}

User Query: {query_text}

Please provide a clear, well-structured response. Do not use asterisks for emphasis.
Format the information in an easy-to-read way with proper spacing between paragraphs.
If you're listing points, use clear numbering and leave space between items.
also return the context i gave you for reference and give it after the answer with the heading "context referenced"
if the question is irrelevant or lacks usable context, politely refuse to answer.if this is the case, no need to show context
"""

        # generate response
        try:
            response = llm.invoke(full_context)
            
            # formatting response
            formatted_response = format_response(response)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

        # store latest interaction
        conversation_memory[user_id].append(f"User: {query_text}\nAI: {formatted_response}")

        return {
            "query": query_text,
            "response": formatted_response,
            "context": doc_context,
            "memory": list(conversation_memory[user_id])
        }

    except Exception as e:
        print("Error processing request:", str(e))
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")