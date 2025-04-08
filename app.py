from flask import Flask, render_template, request, jsonify
import openai
from openai import OpenAI
import configparser
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import chromadb
from chromadb.config import Settings
import os

app = Flask(__name__)

# Load OpenAI API key from configuration file
config = configparser.ConfigParser()
config.read('config.ini')
OPENAI_KEY = config.get('OPENAI_API', 'OPENAI_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

# Initialize ChromaDB client with persistence
persist_directory = "data/chroma_db"
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

chroma_client = chromadb.PersistentClient(path=persist_directory)

# Get or create collections
try:
    customer_collection = chroma_client.get_collection(name="customer_tweets")
    company_collection = chroma_client.get_collection(name="company_tweets")
except Exception as e:
    print("Collections not found. Please run generate_embeddings.py first.")
    customer_collection = None
    company_collection = None

# Get embedding for a text
def get_embedding(text, model="text-embedding-3-small"):
    """Get embedding for a text using OpenAI's text-embedding-3-small model.
    This model is optimized for speed and cost while maintaining good quality embeddings."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# Find most similar examples
def find_similar_examples(query_embedding, n=3):
    if customer_collection is None or company_collection is None:
        return []
        
    # Query customer collection
    customer_results = customer_collection.query(
        query_embeddings=[query_embedding],
        n_results=n
    )
    
    # Query company collection
    company_results = company_collection.query(
        query_embeddings=[query_embedding],
        n_results=n
    )
    
    # Combine results
    similar_examples = []
    for i in range(n):
        if i < len(customer_results['documents'][0]):
            similar_examples.append((
                i,
                customer_results['distances'][0][i],
                customer_results['documents'][0][i],
                company_results['documents'][0][i] if i < len(company_results['documents'][0]) else ""
            ))
    
    return similar_examples

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data.get('text', '')
    company = data.get('company', '')
    
    try:
        if customer_collection is None or company_collection is None:
            return jsonify({'error': 'Collections not initialized. Please run generate_embeddings.py first.'}), 500
            
        # Get embedding for the input text
        query_embedding = get_embedding(text)
        
        # Find similar examples
        similar_examples = find_similar_examples(query_embedding)
        
        if not similar_examples:
            return jsonify({'error': 'No similar examples found. Please check your embeddings.'}), 500
        
        # Create context from similar examples
        context = "\n".join([
            f"Example {i+1}:\nCustomer: {ex[2]}\nResponse: {ex[3]}\n"
            for i, ex in enumerate(similar_examples)
        ])
        
        # Create the prompt for GPT with RAG context
        prompt = f"""You are a customer service representative for {company}. 
        You are provided with some similar examples of customer interactions and responses.
        Use these examples to guide your response style and tone.
        
        Similar examples:
        {context}
        
        Now, respond to the following customer tweet in a similar style:
        Customer tweet: "{text}"
        
        Response:"""
        
        # Generate response using GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a helpful customer service representative for {company}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        result = response.choices[0].message.content.strip()
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 