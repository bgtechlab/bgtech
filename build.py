import json
import os
from jinja2 import Environment, FileSystemLoader

# 1. Check & Load Products Data
data_file = os.path.join('data', 'products.json')
products = []

if os.path.exists(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        try:
            products = json.load(f)
        except Exception as e:
            print(f"Error loading products.json: {e}")

# Setup Jinja2 Environment
templates_dir = 'templates'
if os.path.exists(templates_dir):
    env = Environment(loader=FileSystemLoader(templates_dir))

    # 2. Generate Product Pages
    if os.path.exists(os.path.join(templates_dir, 'product.html')):
        product_template = env.get_template('product.html')
        for prod in products:
            out_dir = os.path.join('products', prod['id'])
            os.makedirs(out_dir, exist_ok=True)
            
            rendered_html = product_template.render(product=prod)
            with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(rendered_html)

    # 3. Generate Homepage
    if os.path.exists(os.path.join(templates_dir, 'index.html')):
        home_template = env.get_template('index.html')
        home_html = home_template.render(products=products)
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(home_html)

print("✅ Website Built Successfully!")
