# Advanced Product Vector Search - Lambda Handler
# This code handles vector search requests using Cosine Similarity.
# Designed for robust error handling and cold-start optimization.

import json

import os
import mysql.connector
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize model outside handler for re-use (Cold Start optimization)
print("Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

# DB Config
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'host.docker.internal'),
    'database': os.environ.get('DB_NAME', 'vector_search_db'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password')
}

def get_vectors_from_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        # Fetch only what's needed
        cursor.execute("SELECT product_id, product_name, vector FROM products_vectors")
        results = cursor.fetchall()
        conn.close()
        
        # Parse JSON vectors
        for row in results:
            if isinstance(row['vector'], str):
                row['vector'] = json.loads(row['vector'])
            # If already list/json object (depending on connector/driver), do nothing
            
        return results
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def lambda_handler(event, context):
    """
    AWS Lambda Handler
    Event format expected: { "queryStringParameters": { "q": "search term" } }
    """
    # Handle API Gateway proxy integration or direct invoke
    query = ""
    if 'queryStringParameters' in event and event['queryStringParameters']:
        query = event['queryStringParameters'].get('q', '')
    else:
        # Fallback for direct invocation test
        query = event.get('q', '')
    
    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing query parameter "q"'})
        }

    # 1. Embed Query
    query_vector = model.encode([query])[0]
    
    # 2. Fetch Candidates
    products = get_vectors_from_db()
    
    if not products:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'No products found in database or DB connection failed'})
        }

    # 3. Calculate Similarity
    # Prepare matrix
    try:
        product_vectors = np.array([p['vector'] for p in products])
        
        # Reshape query for scikit-learn (1, D)
        query_vector_reshaped = query_vector.reshape(1, -1)
        
        # Compute Cosine Similarity
        similarities = cosine_similarity(query_vector_reshaped, product_vectors)[0]
        
        # 4. Rank Results
        # Attach score to product
        for i, product in enumerate(products):
            product['score'] = float(similarities[i])
            del product['vector'] # Remove vector from response
        
        # Sort by score descending
        sorted_products = sorted(products, key=lambda x: x['score'], reverse=True)
        
        # Top 5
        top_results = sorted_products[:5]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'query': query,
                'results': top_results
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Processing error: {str(e)}"})
        }

if __name__ == "__main__":
    # Local Test
    test_event = {'queryStringParameters': {'q': 'smartphone'}}
    print(lambda_handler(test_event, None))
