import os
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from get_embedding_function import get_embedding_function
from langchain_google_genai import GoogleGenerativeAI

#load vector database
embedding_function = get_embedding_function()
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# retriever = db.as_retriever(search_kwargs={"k": 3})
# retrieved_docs = retriever.get_relevant_documents("how to bend a glass tube?")

# print("\n🔍 Retrieved Documents Manually:\n", retrieved_docs)

# Load LLM
#llm = Ollama(model="mistral",streaming=True)
#llm = GoogleGenerativeAI(model="gemini-1.5-pro", api_key="AIzaSyDR1nrVF50H2bw8JT8cJRi-kZ_gBXQ12K8")
llm = GoogleGenerativeAI(model="gemini-1.5-pro", api_key="AIzaSyDIi7HJ0Hb-8qT7y_vz9IAfnkseZjDWm_U")


'''prompt_template = """You are an AI teacher helping students understand topics.
Answer the following question based on the provided context. 

Context:
{context}

Question:
{question}

Provide a detailed, well-explained answer. Mention figures if any are referenced in the context
Also return the context i'm giving you
"""'''

'''prompt_template = """You are an AI teacher with extensive experience in providing clear and structured educational responses. Your specialty is breaking down complex topics into easy-to-understand points or steps that facilitate learning.



Use the following **context** to answer the question. If the context is irrelevant or insufficient, state that instead of guessing.

---
Context:
{context}
---

Question
{question}

Answer
Explain thoroughly. If referring to figures, mention them explicitly
Please construct your response in a list format, ensuring each point or step is clearly articulated. Leave one line space between each point to enhance readability.

Keep in mind that I am looking for a thorough  explanation that covers the essential aspects of the topic)
---

"""
'''

prompt_template="""
You are an educational AI assistant focused on providing clear, well-structured explanations.

When answering the question below, please follow these guidelines:
-refer to figures explicityly if available in the context.
- Base your answer only on the provided context
- Present information in a clean, organized format
- Use clear paragraphs with proper spacing between them
- If creating a list, use proper numbering and spacing
- DO NOT use asterisks or markdown for emphasis
- Use plain text formatting with clear structure
- If mentioning figures, clearly indicate them
- Make your response visually easy to read

Context:
{context}

Question:
{question}

Your response should be comprehensive but well-organized. Focus on clarity and readability.
also return the context you recceived from me so that the user can refer after the answer
if the question is irrelevant or does not have context politely tell them you can't answer at the moment.
"""



prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])


# retrievalQA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=db.as_retriever(search_type="mmr", search_kwargs={"fetch_k": 10, "k": 5, "lambda_mult": 0.5}),
    #retriever=None,
    chain_type="stuff",  # Specify the chain type explicitly
    chain_type_kwargs={"prompt": prompt}
)



def ask_ai_teacher(question):
    response = qa.invoke({"query": question})

    #print("\n🔍 Full Response Dictionary:\n", response)  # Print everything

    retrieved_docs = response.get("source_documents", [])
    for doc in retrieved_docs:
        print(f"\n📜 Retrieved from: {doc.metadata.get('source', 'Unknown')}")
        print(doc.page_content)
    #context_used = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else "No context retrieved"
    #context_used="\n\n--\n\n".join()

    #print("\n📚 Context Used:\n", context_used)  # Print retrieved context

    return response["result"]



if __name__ == "__main__":
# Example usage
    while True:
        query = input("\nAsk your question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        print("\nAI Teacher:", ask_ai_teacher(query))
        print(db._collection.count())
        #print(context)
        