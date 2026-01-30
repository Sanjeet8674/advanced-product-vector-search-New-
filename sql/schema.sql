-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS vector_search_db;
USE vector_search_db;

-- Drop table if exists to start fresh
DROP TABLE IF EXISTS products_vectors;

-- Create table
-- Requirement: product_id (primary key), product_name, vector (as JSON or BLOB)
CREATE TABLE products_vectors (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    vector JSON, -- Using JSON type for vector storage.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for product lookups
CREATE INDEX idx_product_name ON products_vectors(product_name);
