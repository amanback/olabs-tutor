from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAI  # Update if using Gemini
from get_embedding_function import get_embedding_function

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Database & Retriever
embedding_function = get_embedding_function()
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
retriever = db.as_retriever(search_type="mmr", search_kwargs={"fetch_k": 10, "k": 5})

#llm = GoogleGenerativeAI(model="gemini-pro")  # Change if using another model
llm = GoogleGenerativeAI(model="gemini-1.5-pro", api_key="AIzaSyDR1nrVF50H2bw8JT8cJRi-kZ_gBXQ12K8")


class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "FastAPI RAG server is running with CORS enabled"}

@app.post("/query")
async def query_rag(data: QueryRequest):
    query_text = data.query
    relevant_docs = retriever.get_relevant_documents(query_text)
    context = "\n".join([doc.page_content for doc in relevant_docs if doc.page_content])

    if not context:
        context = "No relevant context found."

    # Generate response
    response = llm.invoke(f"Context:\n{context}\n\nQuestion: {query_text}")

    return {
        "query": query_text,
        "response": response,
        "context": context
    }