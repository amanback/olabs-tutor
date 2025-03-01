import os
import argparse
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma  # ✅ Use langchain_chroma
from get_embedding_function import get_embedding_function


CHROMA_PATH = "./chroma_db"
DATA_PATH = "./textbooks"
BATCH_SIZE = 150  

def main():
    """Main function to process documents and store embeddings in ChromaDB."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def load_documents():
    """Loads PDFs from the 'textbooks' directory."""
    loader = PyPDFDirectoryLoader(DATA_PATH)
    return loader.load()

def split_documents(documents):
    """Splits text into smaller chunks for better vector search."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks):
    """Stores document embeddings in ChromaDB with batch processing."""
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    print(f"✅ Processing {len(chunks)} chunks...")
    
    
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        try:
            db.add_documents(batch)
            print(f"✅ Inserted batch {i // BATCH_SIZE + 1} ({len(batch)} documents)")
        except Exception as e:
            print(f"❌ Failed to insert batch {i // BATCH_SIZE + 1}: {e}")

    print(f"✅ Database populated with {len(chunks)} textbook embeddings.")

def clear_database():
    """Deletes existing ChromaDB data to reset the database."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print("✅ Database cleared.")

if __name__ == "__main__":
    main()