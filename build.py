import json
import os

PRODUCTS_JSON_PATH = os.path.join("data", "products.json")
OUTPUT_DIR = "."

def build_site():
    if not os.path.exists(PRODUCTS_JSON_PATH):
        print("❌ products.json file not found!")
        return

    with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    # 1. Generate Product Detail Pages
    for product in products:
        product_slug = product["id"]
        prod_dir = os.path.join("products", product_slug)
        os.makedirs(prod_dir, exist_ok=True)

        pros_html = "".join([f"<li>✅ {p}</li>" for p in product.get("pros", [])])
        cons_html = "".join([f"<li>❌ {c}</li>" for c in product.get("cons", [])])
        
        specs_html = ""
        for key, val in product.get("specs", {}).items():
            specs_html += f"<tr><td style='padding:8px;border:1px solid #ddd;font-weight:bold;'>{key}</td><td style='padding:8px;border:1px solid #ddd;'>{val}</td></tr>"

        prod_html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product['title']} - BG Tech</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f4f6f8; color: #333; }}
        .container {{ max-width: 800px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        img {{ max-width: 100%; height: auto; border-radius: 8px; display: block; margin: auto; }}
        .price {{ font-size: 24px; color: #d9534f; font-weight: bold; margin: 15px 0; }}
        .btn-buy {{ display: inline-block; background: #ff9900; color: #fff; text-decoration: none; padding: 12px 25px; font-weight: bold; border-radius: 5px; margin-top: 15px; }}
        .pros-cons {{ display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }}
        .pros, .cons {{ flex: 1; min-width: 250px; background: #f9f9f9; padding: 15px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../../index.html">← Back to Home</a>
        <h1>{product['title']}</h1>
        <img src="{product['image']}" alt="{product['short_name']}">
        <div class="price">Price: {product['price']}</div>
        <a href="{product['buy_url']}" target="_blank" class="btn-buy">🛒 Buy Now / Check Best Offer</a>
        
        <div class="pros-cons">
            <div class="pros"><h3>Pros</h3><ul>{pros_html}</ul></div>
            <div class="cons"><h3>Cons</h3><ul>{cons_html}</ul></div>
        </div>

        <h3>Specifications</h3>
        <table>{specs_html}</table>

        <div style="margin-top: 25px; line-height: 1.6;">
            {product.get('review_html', '')}
        </div>
    </div>
</body>
</html>"""

        with open(os.path.join(prod_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(prod_html_content)

    # 2. Generate Homepage (index.html)
    cards_html = ""
    for product in products:
        cards_html += f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 20px; background: #fff; display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
            <img src="{product['image']}" alt="{product['short_name']}" style="width: 150px; height: 150px; object-fit: contain; border-radius: 5px;">
            <div style="flex: 1;">
                <span style="background: #0073e6; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">{product.get('category', 'Gadgets')}</span>
                <h2 style="margin: 10px 0 5px 0;"><a href="products/{product['id']}/" style="text-decoration: none; color: #333;">{product['short_name']}</a></h2>
                <p style="color: #666; margin: 0 0 10px 0;">Rating: {product.get('rating', '4.2 out of 5 stars')}</p>
                <div style="font-size: 20px; color: #d9534f; font-weight: bold;">{product['price']}</div>
                <a href="products/{product['id']}/" style="display: inline-block; background: #0073e6; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; margin-top: 10px; font-weight: bold;">Read Review & Deals →</a>
            </div>
        </div>"""

    index_html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BG Tech - Best Tech Reviews & Deals</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f6f8; color: #333; }}
        header {{ background: #1a1a2e; color: white; text-align: center; padding: 30px 15px; }}
        .container {{ max-width: 900px; margin: 20px auto; padding: 0 15px; }}
    </style>
</head>
<body>
    <header>
        <h1>BG Tech</h1>
        <p>Unbiased product reviews, specs breakdown, and best buying links.</p>
    </header>
    <div class="container">
        {cards_html}
    </div>
</body>
</html>"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html_content)

    print("✅ Successfully built index.html and product pages!")

if __name__ == "__main__":
    build_site()