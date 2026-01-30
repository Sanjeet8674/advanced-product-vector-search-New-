# Advanced Product Vector Search - Embedding Script
# Generates vector embeddings for products and stores them in MySQL.

import pandas as pd

import mysql.connector
import json
import os
from sentence_transformers import SentenceTransformer
from mysql.connector import Error

# Configuration
INPUT_FILE = os.path.join(os.path.dirname(__file__), '../data/products.csv')

# Database Code - Update these with your actual DB credentials or use Env Vars
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'vector_search_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password') # CHANGE THIS
}

def embed_and_store():
    # 1. Load Data
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run generate_products.py first.")
        return
        
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} products.")

    # 2. Initialize Model
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    # Using a small, efficient model suitable for local/lambda usage if packaged
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 3. Generate Embeddings
    print("Generating embeddings...")
    texts = df['product_name'].tolist()
    embeddings = model.encode(texts)
    
    # 4. Connect to DB and Insert
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Prepare query
            # Requirement: product_id, product_name, vector
            insert_query = """
            INSERT INTO products_vectors (product_id, product_name, vector)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE product_name=VALUES(product_name), vector=VALUES(vector);
            """
            
            data_to_insert = []
            for i, row in df.iterrows():
                vector_json = json.dumps(embeddings[i].tolist())
                data_to_insert.append((
                    int(row['product_id']), 
                    row['product_name'], 
                    vector_json
                ))
            
            # Batch insert
            print(f"Inserting {len(data_to_insert)} records to MySQL...")
            cursor.executemany(insert_query, data_to_insert)
            conn.commit()
            print(f"Successfully inserted/updated {cursor.rowcount} records.")
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    embed_and_store()
