import csv
import os
import random
from faker import Faker

# Configuration
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '../data/products.csv')
NUM_PRODUCTS = 500
CATEGORIES = ['Electronics', 'Fashion', 'Grocery']

fake = Faker()

def generate_typo(text):
    """Introduces a random typo in the text."""
    if len(text) < 4: return text
    idx = random.randint(0, len(text) - 2)
    # Swap characters
    chars = list(text)
    chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
    return "".join(chars)

def generate_products():
    products = []
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    print(f"Generating {NUM_PRODUCTS} products...")

    for i in range(1, NUM_PRODUCTS + 1):
        category = random.choice(CATEGORIES)
        base_name = ""
        
        if category == 'Electronics':
            base_name = f"{fake.company()} {random.choice(['Phone', 'Laptop', 'Headphones', 'Watch', 'Monitor'])}"
        elif category == 'Fashion':
            base_name = f"{fake.color_name()} {random.choice(['T-Shirt', 'Jeans', 'Sneakers', 'Jacket', 'Dress'])}"
        elif category == 'Grocery':
            base_name = f"{fake.word().capitalize()} {random.choice(['Cereal', 'Coffee', 'Juice', 'Snack', 'Sauce'])}"
        
        # 10% chance to create a "similar" variant (Edge Case 1)
        if i > 1 and random.random() < 0.10:
            variant_type = random.choice(['Pro', 'Lite', 'Max', '2025 Edition'])
            product_name = f"{products[-1]['product_name']} {variant_type}"
            # Ensure different ID
        # 5% chance to create a typo (Edge Case 2)
        elif random.random() < 0.05:
            product_name = generate_typo(base_name)
        else:
            product_name = base_name

        # Requirement: Output CSV: product_id, product_name.
        products.append({
            'product_id': i,
            'product_name': product_name
        })

    # Write to CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['product_id', 'product_name'])
        writer.writeheader()
        writer.writerows(products)

    print(f"Successfully generated {len(products)} products in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_products()
