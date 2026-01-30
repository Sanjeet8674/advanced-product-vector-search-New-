import sqlite3
import pandas as pd
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration
INPUT_FILE = os.path.join(os.path.dirname(__file__), '../data/products.csv')
DB_FILE = os.path.join(os.path.dirname(__file__), '../data/local_demo.db')

def run_demo():
    print("=== STARTING LOCAL DEMO (SQLite Mode) ===")
    
    # 1. Check Data
    if not os.path.exists(INPUT_FILE):
        print("Data file not found. Running generation...")
        try:
            from generate_products import generate_products
            generate_products()
        except ImportError:
            # Fallback if running from a different cwd or issues with imports
            print("Could not import generate_products. Please run generate_products.py first.")
            return

    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} products from CSV.")

    # 2. Setup SQLite DB
    print("Setting up local SQLite database...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS products_vectors")
    cursor.execute("""
        CREATE TABLE products_vectors (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            vector TEXT
        )
    """)
    
    # 3. Generate Embeddings & Store
    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Embedding products and storing in SQLite...")
    texts = df['product_name'].tolist()
    embeddings = model.encode(texts)
    
    data_to_insert = []
    for i, row in df.iterrows():
        vector_json = json.dumps(embeddings[i].tolist())
        data_to_insert.append((
            int(row['product_id']), 
            row['product_name'], 
            vector_json
        ))
    
    cursor.executemany("INSERT INTO products_vectors (product_id, product_name, vector) VALUES (?, ?, ?)", data_to_insert)
    conn.commit()
    print(f"Stored {len(data_to_insert)} vectors in SQLite.")

    # 4. Simulate Lambda Search
    print("\n--- Simulating Search Query ---")
    query_term = "smart phone" # Intentional space vs "smartphone" to test semantic match
    print(f"Query: '{query_term}'")
    
    # a. Embed Query
    query_vector = model.encode([query_term])[0]
    
    # b. Fetch All Vectors
    cursor.execute("SELECT product_name, vector FROM products_vectors")
    results = cursor.fetchall()
    
    product_names = [r[0] for r in results]
    product_vectors = np.array([json.loads(r[1]) for r in results])
    
    # c. Compute Similarity
    query_vector_reshaped = query_vector.reshape(1, -1)
    similarities = cosine_similarity(query_vector_reshaped, product_vectors)[0]
    
    # d. Rank
    ranked_indices = np.argsort(similarities)[::-1]
    
    print(f"\nTop 5 Results for '{query_term}':")
    for i in range(5):
        idx = ranked_indices[i]
        score = similarities[idx]
        name = product_names[idx]
        print(f"{i+1}. {name} (Score: {score:.4f})")
    
    conn.close()
    print("\n=== DEMO COMPLETE ===")

if __name__ == "__main__":
    run_demo()
