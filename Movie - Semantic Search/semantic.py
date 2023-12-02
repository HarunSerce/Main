from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

# for semantic search, I use openai embedding model to vectorize user's text. For similarity search used Faiss.
# In this document you have provide a openai api key to run code.

def semantic_search(user_input):
    if user_input.isspace() or not user_input:
        print("No text")
        return [] 

    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        api_key = "OpenAi api-key"
    )
    db = FAISS.load_local("openai_faiss_index", embeddings)

    query = user_input

    result_docs = db.similarity_search(query,k=5)
    
    result_ids = [int(result.page_content.split('\n')[0].split(': ')[1]) for result in result_docs]

    return result_ids