from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
import os

## Creating vector db for movie overviews
## You need a Openai key for movie overview embeddings

def vector():

    if os.path.exists("openai_faiss_index"):

        print("Already indexed")

        return True

    loader = CSVLoader('desc.csv')
    documents = loader.load()

    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",  api_key="Openai api-key"
    )

    text_splitter = CharacterTextSplitter(chunk_size=2048, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    db = FAISS.from_documents(docs, embeddings)

    db.save_local("openai_faiss_index")

    print("Indexing completed")

    return True

if __name__ == "__main__":

    vector()