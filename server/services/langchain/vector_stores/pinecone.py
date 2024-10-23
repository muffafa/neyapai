import os
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone

def initialize_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    pinecone.init(api_key=api_key, environment="us-west1-gcp")
    return pinecone

def build_vector_store(index_name: str):
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    pinecone_client = initialize_pinecone()
    return LangchainPinecone.from_existing_index(index_name, embeddings)
