from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Configuration
DB_FILE = os.path.join(os.path.dirname(__file__), 'data/local_demo.db')
# Use /tmp for writing in restricted environments like HF Spaces if needed, 
# but for Docker Spaces, the working dir is usually writable or we use a volume.
# For simplicity in this demo, we'll try to keep it local or use /tmp if permission denied.
if not os.access(os.path.dirname(__file__), os.W_OK):
   # Fallback to tmp if current dir is read-only
   DB_FILE = '/tmp/local_demo.db'

MODEL_NAME = 'all-MiniLM-L6-v2'

print("Loading model... this may take a moment.")
model = SentenceTransformer(MODEL_NAME)
print("Model loaded.")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    try:
        # 1. Embed Query
        query_vector = model.encode([query])[0]
        
        # 2. Fetch Vectors from DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, product_name, vector FROM products_vectors")
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return jsonify([])

        # 3. Calculate Similarity
        product_vectors = []
        product_data = []
        
        for row in results:
            product_vectors.append(json.loads(row['vector']))
            product_data.append({
                'id': row['product_id'],
                'name': row['product_name']
            })
            
        product_vectors = np.array(product_vectors)
        query_vector_reshaped = query_vector.reshape(1, -1)
        
        similarities = cosine_similarity(query_vector_reshaped, product_vectors)[0]
        
        # 4. Rank and Clean Results
        ranked_results = []
        for i in range(len(product_data)):
            ranked_results.append({
                'name': product_data[i]['name'],
                'score': float(similarities[i])
            })
            
        # Sort by score desc, take top 10
        ranked_results.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(ranked_results[:10])

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Auto-generate data if missing (Crucial for Cloud Deployment)
    if not os.path.exists(DB_FILE):
        print("Database not found. Generating data for first-time run...")
        # We need to import the logic or run the script. 
        # Since scripts/run_local_demo.py is a script, let's just run the generation logic here or call it via subprocess
        try:
             # Quick inline regeneration for standalone capability
            from scripts.generate_products import generate_products
            generate_products()
            
            # Re-run embedding
            from scripts.run_local_demo import run_demo
            # Hack: run_demo() relies on fixed paths in that file. 
            # Ideally we refactor, but for now let's just use subprocess to ensure paths align relative to CWD
            import subprocess
            subprocess.run(["python", "scripts/run_local_demo.py"], check=True)
            print("Data generation complete.")
        except Exception as e:
            print(f"Warning: Could not auto-generate data: {e}")

    print("Starting Flask server...")
    # Hugging Face Spaces expects port 7860
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
