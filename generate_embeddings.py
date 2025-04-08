import pandas as pd
import numpy as np
from openai import OpenAI
import configparser
import os
import chromadb
from chromadb.config import Settings

# Load OpenAI API key
config = configparser.ConfigParser()
config.read('config.ini')
OPENAI_KEY = config.get('OPENAI_API', 'OPENAI_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

# Create directory for ChromaDB if it doesn't exist
persist_directory = "data/chroma_db"
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

# Initialize ChromaDB client with persistence
chroma_client = chromadb.PersistentClient(path=persist_directory)

def get_embedding(text, model="text-embedding-3-small"):
    """Get embedding for a text using OpenAI's API"""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def main():
    # Read the CSV file
    df = pd.read_csv('data/twitter_data_clean_sample.csv')
    
    # Create collections with specific metadata
    customer_collection = chroma_client.get_or_create_collection(
        name="customer_tweets",
        metadata={"hnsw:space": "cosine"}
    )
    
    company_collection = chroma_client.get_or_create_collection(
        name="company_tweets",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Generate embeddings for customer tweets
    print("Generating embeddings for customer tweets...")
    customer_embeddings = df['customer_tweet'].apply(get_embedding)
    
    # Add customer tweets to collection
    customer_collection.add(
        embeddings=customer_embeddings.tolist(),
        documents=df['customer_tweet'].tolist(),
        ids=[f"customer_{i}" for i in range(len(df))]
    )
    
    # Generate embeddings for company tweets
    print("Generating embeddings for company tweets...")
    company_embeddings = df['company_tweet'].apply(get_embedding)
    
    # Add company tweets to collection
    company_collection.add(
        embeddings=company_embeddings.tolist(),
        documents=df['company_tweet'].tolist(),
        ids=[f"company_{i}" for i in range(len(df))]
    )
    
    print("Done! Embeddings stored in ChromaDB.")
    print(f"Collections created in: {persist_directory}")

if __name__ == "__main__":
    main() 