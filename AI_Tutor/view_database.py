from langchain_chroma import Chroma  # ✅ Updated import
from get_embedding_function import get_embedding_function

# Load database
embedding_function = get_embedding_function()
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# Fetch all documents
docs = db.get(include=['documents'])

# Print all stored documents
for i, doc in enumerate(docs["documents"]):
    print(f"\n📄 Document {i+1}:\n{doc}")