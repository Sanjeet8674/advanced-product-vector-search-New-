---
title: Advanced Product Vector Search
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
# Advanced Product Vector Search

![Project Preview](project_preview.png)

## 🚀 Live Project

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Sanjeet8674/advanced-product-vector-search)

**[🔴 View Live Demo](https://huggingface.co/spaces/Sanjeet8674/advanced-product-vector-search2)** | **[View Source on GitHub](https://github.com/Sanjeet8674/advanced-product-vector-search-New-)**

> **Note**: This is a robust backend system with a simulated local frontend. To run the "Live" version, follow the local setup instructions below.

## 📖 Description
This project is an **AI-Powered Semantic Search Engine** designed to demonstrate advanced vector search capabilities. Unlike traditional keyword matching, this system understands the *context* and *meaning* of user queries using state-of-the-art Natural Language Processing (NLP).

It uses **Sentence Transformers** to convert products and queries into high-dimensional vectors and performs **Cosine Similarity** search to find the most relevant results, even handling typos and synonyms (e.g., searching for "cell" finds "mobile phone").

### ✨ Key Features
*   **🧠 Semantic Understanding**: Uses `all-MiniLM-L6-v2` embeddings to understand user intent.
*   **⚡ High Performance**: Optimized vector comparison using `scikit-learn` and `numpy`.
*   **🛠️ Full Pipeline**:
    *   **Data Generation**: Custom script to generate realistic synthetic product data with typos.
    *   **Vector Database**: Stores embeddings in MySQL (or SQLite for local demo) using JSON.
    *   **Serverless Ready**: Includes AWS Lambda handler for scalable deployment.
*   **🎨 Modern UI**: Includes a sleek, dark-mode web interface (`Flask`) for testing.

## 🛠️ Tech Stack
*   **Language**: Python 3.9+
*   **ML/AI**: `sentence-transformers`, `scikit-learn`, `numpy`
*   **Backend**: Flask (Local), AWS Lambda (Cloud)
*   **Database**: MySQL (Production), SQLite (Local Demo)
*   **Infrastructure**: Terraform (IaC)

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/Sanjeet8674/advanced-product-vector-search-New-.git
cd advanced-product-vector-search-New-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install flask
```

### 3. Run the Application
You can run the full interactive demo with:
```bash
python app.py
```
Then open your browser to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### 4. Alternative: Run CLI Demo
If you prefer a command-line interface:
```bash
python scripts/run_local_demo.py
```

## ☁️ AWS Deployment
The project includes complete Terraform scripts to deploy to AWS.
1. Configure AWS Credentials.
2. Run:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

## 📂 Project Structure
*   `app.py`: Flask Web Server for the local UI.
*   `scripts/`: Utilities for generating synthetic data and creating embeddings.
*   `lambda/`: The Serverless function handler for AWS.
*   `terraform/`: Infrastructure validation.
*   `sql/`: Database schema definitions.

## 🤝 Contribution
Feel free to fork this repository and submit Pull Requests!

---
*Created by [Sanjeet](https://github.com/Sanjeet8674)*
