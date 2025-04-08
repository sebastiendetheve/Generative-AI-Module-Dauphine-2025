import pandas as pd
import numpy as np
from openai import OpenAI
import configparser
import chromadb
from chromadb.config import Settings
from sklearn.metrics.pairwise import cosine_similarity
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Load OpenAI API key
config = configparser.ConfigParser()
config.read('config.ini')
OPENAI_KEY = config.get('OPENAI_API', 'OPENAI_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

# Initialize ChromaDB client with persistence
persist_directory = "data/chroma_db"
if not os.path.exists(persist_directory):
    raise Exception(f"ChromaDB directory not found at {persist_directory}. Please run generate_embeddings.py first.")

chroma_client = chromadb.PersistentClient(path=persist_directory)

# Get collections
try:
    customer_collection = chroma_client.get_collection(name="customer_tweets")
    company_collection = chroma_client.get_collection(name="company_tweets")
except Exception as e:
    print("Error accessing ChromaDB collections. Please make sure you've run generate_embeddings.py first.")
    raise e

def get_embedding(text, model="text-embedding-3-small"):
    """Get embedding for a text using OpenAI's API"""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def find_similar_examples(query_embedding, n=3):
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

def generate_response(text, company, similar_examples):
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
    
    return response.choices[0].message.content.strip()

def plot_results(results_df):
    # Set style
    plt.style.use('ggplot')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Evaluation Results Analysis', fontsize=16)
    
    # 1. Distribution of similarity scores
    sns.histplot(data=results_df, x='similarity_score', bins=10, ax=axes[0, 0], color='skyblue')
    axes[0, 0].set_title('Distribution of Similarity Scores', fontsize=12)
    axes[0, 0].set_xlabel('Similarity Score', fontsize=10)
    axes[0, 0].set_ylabel('Count', fontsize=10)
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Box plot of similarity scores
    sns.boxplot(data=results_df, y='similarity_score', ax=axes[0, 1], color='lightgreen')
    axes[0, 1].set_title('Box Plot of Similarity Scores', fontsize=12)
    axes[0, 1].set_ylabel('Similarity Score', fontsize=10)
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Scatter plot of response lengths
    results_df['reference_length'] = results_df['reference_response'].apply(len)
    results_df['generated_length'] = results_df['generated_response'].apply(len)
    sns.scatterplot(data=results_df, x='reference_length', y='generated_length', 
                   ax=axes[1, 0], color='coral', alpha=0.7)
    axes[1, 0].set_title('Response Length Comparison', fontsize=12)
    axes[1, 0].set_xlabel('Reference Response Length', fontsize=10)
    axes[1, 0].set_ylabel('Generated Response Length', fontsize=10)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Add diagonal line for perfect length match
    min_len = min(results_df['reference_length'].min(), results_df['generated_length'].min())
    max_len = max(results_df['reference_length'].max(), results_df['generated_length'].max())
    axes[1, 0].plot([min_len, max_len], [min_len, max_len], 'r--', alpha=0.5)
    
    # 4. Line plot of similarity scores
    sns.lineplot(data=results_df, x=results_df.index, y='similarity_score', 
                ax=axes[1, 1], color='purple', marker='o')
    axes[1, 1].set_title('Similarity Scores Over Examples', fontsize=12)
    axes[1, 1].set_xlabel('Example Index', fontsize=10)
    axes[1, 1].set_ylabel('Similarity Score', fontsize=10)
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add horizontal line for average similarity
    avg_similarity = results_df['similarity_score'].mean()
    axes[1, 1].axhline(y=avg_similarity, color='r', linestyle='--', alpha=0.5)
    axes[1, 1].text(0, avg_similarity, f'Avg: {avg_similarity:.2f}', 
                   color='r', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    plt.savefig('evaluation_plots.png', dpi=300, bbox_inches='tight')
    plt.close()

def evaluate_system():
    # Load evaluation data
    df_eval = pd.read_csv('data/twitter_data_clean_eval.csv')
    
    # Limit to first 20 rows
    df_eval = df_eval.head(20)
    print(f"Evaluating system on {len(df_eval)} examples...")
    
    results = []
    
    for idx, row in df_eval.iterrows():
        print(f"Processing example {idx+1}/{len(df_eval)}...")
        
        # Get embedding for the customer tweet
        query_embedding = get_embedding(row['customer_tweet'])
        
        # Find similar examples
        similar_examples = find_similar_examples(query_embedding)
        
        # Generate response
        generated_response = generate_response(
            row['customer_tweet'],
            "the company",  # You might want to specify the company name
            similar_examples
        )
        
        # Get embeddings for similarity comparison
        reference_embedding = get_embedding(row['company_tweet'])
        generated_embedding = get_embedding(generated_response)
        
        # Calculate cosine similarity
        similarity = cosine_similarity([reference_embedding], [generated_embedding])[0][0]
        
        results.append({
            'customer_tweet': row['customer_tweet'],
            'reference_response': row['company_tweet'],
            'generated_response': generated_response,
            'similarity_score': similarity
        })
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Calculate statistics
    avg_similarity = results_df['similarity_score'].mean()
    std_similarity = results_df['similarity_score'].std()
    min_similarity = results_df['similarity_score'].min()
    max_similarity = results_df['similarity_score'].max()
    
    print("\nEvaluation Statistics:")
    print(f"Average similarity score: {avg_similarity:.4f}")
    print(f"Standard deviation: {std_similarity:.4f}")
    print(f"Minimum similarity: {min_similarity:.4f}")
    print(f"Maximum similarity: {max_similarity:.4f}")
    
    # Generate plots
    plot_results(results_df)
    print("\nPlots saved to evaluation_plots.png")
    
    # Save results
    results_df.to_csv('evaluation_results.csv', index=False)
    print("Results saved to evaluation_results.csv")

if __name__ == "__main__":
    evaluate_system() 