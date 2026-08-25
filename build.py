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

    COMMON_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --bg-main: #F8FAFC;
        --nav-bg: #0F172A;
        --nav-sub-bg: #1E293B;
        --accent-blue: #2563EB;
        --accent-green: #16A34A;
        --text-dark: #0F172A;
        --text-muted: #64748B;
        --card-bg: #FFFFFF;
        --border-color: #E2E8F0;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    body { background-color: var(--bg-main); color: var(--text-dark); line-height: 1.6; }

    header { background: var(--nav-bg); color: white; position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; }
    .logo { font-size: 24px; font-weight: 800; color: #fff; text-decoration: none; letter-spacing: -0.5px; }
    .logo span { color: var(--accent-blue); }

    .sub-nav { background: var(--nav-sub-bg); border-top: 1px solid rgba(255,255,255,0.08); overflow-x: auto; white-space: nowrap; scrollbar-width: none; }
    .sub-nav::-webkit-scrollbar { display: none; }
    .sub-nav-container { max-width: 1200px; margin: 0 auto; display: flex; gap: 18px; padding: 10px 20px; }
    .sub-nav-container a { color: #CBD5E1; text-decoration: none; font-size: 13px; font-weight: 500; transition: color 0.2s; }
    .sub-nav-container a:hover { color: #38BDF8; }

    .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

    .section-title { font-size: 22px; font-weight: 700; margin: 35px 0 20px; display: flex; align-items: center; gap: 10px; color: var(--text-dark); border-bottom: 2px solid var(--border-color); padding-bottom: 10px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }

    .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; }
    .card:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.06); }
    .card-img-wrapper { background: #F1F5F9; padding: 20px; height: 220px; display: flex; align-items: center; justify-content: center; }
    .card-img-wrapper img { max-height: 100%; max-width: 100%; object-fit: contain; }
    .card-content { padding: 20px; display: flex; flex-direction: column; flex-grow: 1; }
    .badge { align-self: flex-start; background: #EFF6FF; color: var(--accent-blue); font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; margin-bottom: 10px; }
    .card-title { font-size: 17px; font-weight: 700; color: var(--text-dark); text-decoration: none; margin-bottom: 8px; line-height: 1.3; }
    .card-title:hover { color: var(--accent-blue); }
    .rating { color: #F59E0B; font-size: 14px; font-weight: 600; margin-bottom: 12px; }
    .price { font-size: 20px; font-weight: 800; color: var(--accent-green); margin-top: auto; margin-bottom: 15px; }
    .card-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .btn { display: inline-block; text-align: center; padding: 10px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; text-decoration: none; transition: 0.2s; }
    .btn-review { background: #F1F5F9; color: var(--text-dark); }
    .btn-review:hover { background: #E2E8F0; }
    .btn-buy { background: var(--accent-blue); color: white; }
    .btn-buy:hover { background: #1D4ED8; }

    footer { background: var(--nav-bg); color: #94A3B8; text-align: center; padding: 40px 20px; margin-top: 60px; font-size: 14px; }
    footer a { color: #CBD5E1; text-decoration: none; margin: 0 10px; }
    """

    NAV_MENU_HTML = """
    <div class="sub-nav">
        <div class="sub-nav-container">
            <a href="../../index.html">Home</a>
            <a href="../../index.html#mobiles">Mobiles</a>
            <a href="../../index.html#tvs">Smart TV</a>
            <a href="../../index.html#headphones">Audio & Sound</a>
            <a href="../../index.html#gadgets">Printers & Gadgets</a>
        </div>
    </div>
    """

    NAV_MENU_HOME_HTML = NAV_MENU_HTML.replace("../../index.html", "index.html")

    # Generate Product Detail Pages
    for product in products:
        product_slug = product["id"]
        prod_dir = os.path.join("products", product_slug)
        os.makedirs(prod_dir, exist_ok=True)

        pros_html = "".join([f"<li style='margin-bottom:8px; color:#15803D;'>✓ {p}</li>" for p in product.get("pros", [])])
        cons_html = "".join([f"<li style='margin-bottom:8px; color:#B91C1C;'>✕ {c}</li>" for c in product.get("cons", [])])
        
        specs_html = ""
        for key, val in product.get("specs", {}).items():
            specs_html += f"<tr><td style='padding:12px; border-bottom:1px solid #E2E8F0; font-weight:600; color:#475569;'>{key}</td><td style='padding:12px; border-bottom:1px solid #E2E8F0; color:#0F172A;'>{val}</td></tr>"

        meta_desc = f"Read detailed review of {product['short_name']}. Check specifications, pricing, pros, cons, and performance verdict before buying."

        prod_html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product['title']} - Price, Specs & Detailed Review (2026)</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{product['short_name']}, {product['short_name']} price in India, {product['short_name']} specs, buy {product['short_name']}">
    
    <meta property="og:title" content="{product['title']}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="{product['image']}">
    <meta property="og:type" content="article">
    
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "{product['short_name']}",
      "image": ["{product['image']}"],
      "description": "{meta_desc}",
      "offers": {{
        "@type": "Offer",
        "priceCurrency": "INR",
        "price": "{product['price'].replace('₹','').replace(',','')}",
        "availability": "https://schema.org/InStock",
        "url": "{product['buy_url']}"
      }}
    }}
    </script>
    <style>{COMMON_CSS}</style>
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="../../index.html" class="logo">BG <span>TECH</span></a>
        </div>
        {NAV_MENU_HTML}
    </header>

    <main class="container" style="max-width: 900px; margin-top: 30px;">
        <span class="badge">{product.get('category', 'Gadgets')}</span>
        <h1 style="font-size: 32px; font-weight: 800; margin: 10px 0;">{product['title']}</h1>
        <div class="rating" style="font-size: 16px; margin-bottom: 20px;">★ {product.get('rating', '4.2 out of 5 stars')}</div>

        <div style="background: white; border: 1px solid var(--border-color); border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 30px;">
            <img src="{product['image']}" alt="{product['short_name']}" style="max-height: 350px; width: auto; object-fit: contain;">
            <div style="font-size: 28px; font-weight: 800; color: var(--accent-green); margin: 20px 0 10px;">{product['price']}</div>
            <a href="{product['buy_url']}" target="_blank" class="btn btn-buy" style="font-size: 16px; padding: 14px 32px;">🛒 Check Best Price / Buy Now</a>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:20px;">
                <h3 style="color:#166534; margin-bottom:12px;">Pros</h3>
                <ul style="list-style:none;">{pros_html}</ul>
            </div>
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:12px; padding:20px;">
                <h3 style="color:#991B1B; margin-bottom:12px;">Cons</h3>
                <ul style="list-style:none;">{cons_html}</ul>
            </div>
        </div>

        <div style="background: white; border: 1px solid var(--border-color); border-radius: 12px; padding: 25px; margin-bottom: 30px;">
            <h3 style="margin-bottom: 15px; font-size: 20px;">Technical Specifications</h3>
            <table style="width: 100%; border-collapse: collapse;">{specs_html}</table>
        </div>

        <div style="background: white; border: 1px solid var(--border-color); border-radius: 12px; padding: 30px; line-height: 1.8; font-size: 16px; color: #334155;">
            <h2 style="margin-bottom: 20px; font-size: 24px; color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px;">Detailed Review & Expert Analysis</h2>
            {product.get('review_html', '')}
        </div>
    </main>

    <footer>
        <p><a href="../../index.html">About</a> • <a href="../../index.html">Contact</a> • <a href="../../index.html">Privacy</a> • <a href="../../index.html">Disclaimer</a></p>
        <p style="margin-top:10px;">&copy; 2026 BG Tech. All rights reserved.</p>
    </footer>
</body>
</html>"""

        with open(os.path.join(prod_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(prod_html_content)

    def generate_cards(items):
        html = ""
        for p in items:
            html += f"""
            <div class="card">
                <div class="card-img-wrapper">
                    <img src="{p['image']}" alt="{p['short_name']}">
                </div>
                <div class="card-content">
                    <span class="badge">{p.get('category', 'Gadgets')}</span>
                    <a href="products/{p['id']}/" class="card-title">{p['short_name']}</a>
                    <div class="rating">★ {p.get('rating', '4.2/5')}</div>
                    <div class="price">{p['price']}</div>
                    <div class="card-buttons">
                        <a href="products/{p['id']}/" class="btn btn-review">Full Review</a>
                        <a href="{p['buy_url']}" target="_blank" class="btn btn-buy">Best Price</a>
                    </div>
                </div>
            </div>"""
        return html

    # Category Filtering for Homepage Grid
    mobiles = [p for p in products if p.get('category') == 'Mobiles']
    tvs = [p for p in products if p.get('category') in ['TV', 'Television', 'Smart TV']]
    headphones = [p for p in products if p.get('category') in ['Headphones', 'Audio']]
    gadgets = [p for p in products if p.get('category') not in ['Mobiles', 'TV', 'Television', 'Smart TV', 'Headphones', 'Audio']]

    # Generate Homepage (index.html)
    index_html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BG Tech - Latest Tech Reviews, Specifications & Buying Guides (2026)</title>
    <meta name="description" content="Discover unbiased reviews, detailed specifications, pros, cons, and best deals on smartphones, smart TVs, earbuds, and electronics.">
    <style>{COMMON_CSS}</style>
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="index.html" class="logo">BG <span>TECH</span></a>
        </div>
        {NAV_MENU_HOME_HTML}
    </header>

    <section style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: white; padding: 60px 20px; text-align: center;">
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="font-size: 40px; font-weight: 800; margin-bottom: 16px; letter-spacing: -1px;">FIND THE BEST TECH BEFORE YOU BUY</h1>
            <p style="font-size: 18px; color: #94A3B8; margin-bottom: 28px;">Expert Reviews • Specs • Best Deals</p>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <a href="#trending" class="btn btn-buy" style="padding: 12px 24px; font-size: 15px;">Explore Reviews</a>
            </div>
        </div>
    </section>

    <main class="container">
        <h2 class="section-title" id="trending">🔥 Trending Tech</h2>
        <div class="grid">
            {generate_cards(products[:4])}
        </div>

        {f'<h2 class="section-title" id="mobiles">📱 Latest Smartphones</h2><div class="grid">{generate_cards(mobiles)}</div>' if mobiles else ''}
        {f'<h2 class="section-title" id="tvs">📺 Smart TVs & Displays</h2><div class="grid">{generate_cards(tvs)}</div>' if tvs else ''}
        {f'<h2 class="section-title" id="headphones">🎧 Audio & Sound</h2><div class="grid">{generate_cards(headphones)}</div>' if headphones else ''}
        {f'<h2 class="section-title" id="gadgets">⚙️ Printers & Other Electronics</h2><div class="grid">{generate_cards(gadgets)}</div>' if gadgets else ''}
    </main>

    <footer>
        <p><a href="index.html">About</a> • <a href="index.html">Contact</a> • <a href="index.html">Privacy</a> • <a href="index.html">Disclaimer</a></p>
        <p style="margin-top:10px;">&copy; 2026 BG Tech. All rights reserved.</p>
    </footer>
</body>
</html>"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html_content)

    print("✅ Successfully updated website layout & SEO Meta tags!")

if __name__ == "__main__":
    build_site()