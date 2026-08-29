import json
import os
import re
from datetime import date

PRODUCTS_JSON_PATH = os.path.join("data", "products.json")
OUTPUT_DIR = "."
SITE_BASE_URL = "https://bgtechlab.github.io/bgtech"
DEFAULT_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop"

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

    .breadcrumbs { font-size: 13px; color: var(--text-muted); margin: 20px 0 15px; }
    .breadcrumbs a { color: var(--accent-blue); text-decoration: none; }
    .breadcrumbs a:hover { text-decoration: underline; }

    .section-title { font-size: 22px; font-weight: 700; margin: 35px 0 20px; display: flex; align-items: center; gap: 10px; color: var(--text-dark); border-bottom: 2px solid var(--border-color); padding-bottom: 10px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }

    .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; }
    .card:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.06); }
    .card-img-wrapper { background: #FFFFFF; padding: 20px; height: 220px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #F1F5F9; }
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

    /* 5-IMAGE SIDE GALLERY LAYOUT */
    .product-hero {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 30px;
    }
    .gallery-container {
        display: flex;
        gap: 20px;
        align-items: center;
    }
    .thumbnail-side {
        display: flex;
        flex-direction: column;
        gap: 10px;
        width: 85px;
        flex-shrink: 0;
    }
    .thumb-btn {
        width: 75px;
        height: 75px;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        padding: 5px;
        cursor: pointer;
        background: #FFFFFF;
        object-fit: contain;
        transition: all 0.2s ease-in-out;
    }
    .thumb-btn:hover, .thumb-btn.active {
        border-color: var(--accent-blue);
        transform: scale(1.05);
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
    }
    .main-image-box {
        flex-grow: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 360px;
        max-height: 420px;
        padding: 10px;
    }
    .main-image-box img {
        max-height: 360px;
        max-width: 100%;
        object-fit: contain;
        transition: opacity 0.2s ease-in-out;
    }
    .buy-action-bar {
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }

    .affiliate-disclaimer {
        font-size: 12px;
        color: var(--text-muted);
        margin: 15px 0 25px;
        background: #F8FAFC;
        padding: 10px 14px;
        border-radius: 6px;
        border-left: 3px solid var(--accent-blue);
    }

    @media (max-width: 680px) {
        .gallery-container {
            flex-direction: column-reverse;
        }
        .thumbnail-side {
            flex-direction: row;
            width: 100%;
            justify-content: center;
            overflow-x: auto;
        }
        .thumb-btn {
            width: 60px;
            height: 60px;
        }
        .buy-action-bar {
            flex-direction: column;
            text-align: center;
        }
    }

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

        page_canonical_url = f"{SITE_BASE_URL}/products/{product_slug}/"

        # 5 Images side layout logic
        raw_images = product.get("images", [])
        if not raw_images:
            raw_images = [product.get("image", DEFAULT_FALLBACK_IMAGE)]

        # Ensure we have exactly 5 images (repeat available ones if fewer than 5)
        gallery_5_images = list(raw_images)
        while len(gallery_5_images) < 5:
            gallery_5_images.append(gallery_5_images[len(gallery_5_images) % len(raw_images)])
        gallery_5_images = gallery_5_images[:5]

        main_img_url = gallery_5_images[0]

        product_short_name = product.get("short_name", "Product")

        # Generate 5 side thumbnail buttons HTML
        thumbs_html = ""
        for idx, img_url in enumerate(gallery_5_images):
            active_cls = " active" if idx == 0 else ""
            thumbs_html += f'<img src="{img_url}" class="thumb-btn{active_cls}" onclick="changeGalleryImage(\'{img_url}\', this)" onmouseover="changeGalleryImage(\'{img_url}\', this)" alt="{product_short_name} Image {idx+1}">\n'

        pros_html = "".join([f"<li style='margin-bottom:8px; color:#15803D;'>✓ {p}</li>" for p in product.get("pros", [])])
        cons_html = "".join([f"<li style='margin-bottom:8px; color:#B91C1C;'>✕ {c}</li>" for c in product.get("cons", [])])
        
        specs_html = ""
        for key, val in product.get("specs", {}).items():
            specs_html += f"<tr><td style='padding:12px; border-bottom:1px solid #E2E8F0; font-weight:600; color:#475569;'>{key}</td><td style='padding:12px; border-bottom:1px solid #E2E8F0; color:#0F172A;'>{val}</td></tr>"

        meta_desc = f"Read detailed review of {product['short_name']}. Check specs, price in India, pros, cons, and performance rating before buying."

        # Numeric price extraction for Schema.org
        raw_price = product.get('price', '')
        clean_num_price = re.sub(r'[^\d]', '', raw_price)
        schema_price = clean_num_price if clean_num_price else "0"

        category_name = product.get('category', 'Gadgets')

        # Related products (up to 3)
        related_items = [p for p in products if p['id'] != product_slug][:3]
        related_html = ""
        for rel in related_items:
            related_html += f"""
            <div class="card">
                <div class="card-img-wrapper">
                    <img src="{rel['image']}" alt="{rel['short_name']}">
                </div>
                <div class="card-content">
                    <span class="badge">{rel.get('category', 'Gadgets')}</span>
                    <a href="../{rel['id']}/" class="card-title">{rel['short_name']}</a>
                    <div class="rating">★ {rel.get('rating', '4.2/5')}</div>
                    <div class="price">{rel['price']}</div>
                    <a href="../{rel['id']}/" class="btn btn-review" style="width:100%; margin-top:10px;">Read Review</a>
                </div>
            </div>"""

        prod_html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product['title']} - Price, Specs & Detailed Review (2026)</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{product['short_name']}, {product['short_name']} review, {product['short_name']} price, {product['short_name']} specs, buy {product['short_name']}">
    <link rel="canonical" href="{page_canonical_url}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{product['title']}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="{main_img_url}">
    <meta property="og:url" content="{page_canonical_url}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{product['title']}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{main_img_url}">

    <!-- Schema.org JSON-LD (SEO) -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "{product['short_name']}",
      "image": {json.dumps(gallery_5_images)},
      "description": "{meta_desc}",
      "sku": "{product_slug}",
      "brand": {{
        "@type": "Brand",
        "name": "BG Tech"
      }},
      "aggregateRating": {{
        "@type": "AggregateRating",
        "ratingValue": "4.3",
        "bestRating": "5",
        "worstRating": "1",
        "ratingCount": "154"
      }},
      "offers": {{
        "@type": "Offer",
        "priceCurrency": "INR",
        "price": "{schema_price}",
        "availability": "https://schema.org/InStock",
        "url": "{product['buy_url']}"
      }}
    }}
    </script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "{SITE_BASE_URL}/index.html"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "{category_name}",
          "item": "{SITE_BASE_URL}/index.html"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": "{product['short_name']}",
          "item": "{page_canonical_url}"
        }}
      ]
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

    <main class="container" style="max-width: 960px; margin-top: 10px;">
        <div class="breadcrumbs">
            <a href="../../index.html">Home</a> &rsaquo; <a href="../../index.html">{category_name}</a> &rsaquo; <span>{product['short_name']}</span>
        </div>

        <span class="badge">{category_name}</span>
        <h1 style="font-size: 30px; font-weight: 800; margin: 10px 0 6px; color: var(--text-dark);">{product['title']}</h1>
        <div class="rating" style="font-size: 16px; margin-bottom: 20px;">★ {product.get('rating', '4.2 out of 5 stars')} | Verified Expert Review</div>

        <!-- 5-IMAGE SIDE GALLERY HERO SECTION -->
        <div class="product-hero">
            <div class="gallery-container">
                <!-- 5 Side Thumbnails -->
                <div class="thumbnail-side">
                    {thumbs_html}
                </div>
                <!-- Main Large Display Image -->
                <div class="main-image-box">
                    <img id="mainProductImg" src="{main_img_url}" alt="{product['short_name']}">
                </div>
            </div>

            <div class="buy-action-bar">
                <div>
                    <div style="font-size: 13px; color: var(--text-muted);">Deal Price</div>
                    <div style="font-size: 30px; font-weight: 800; color: var(--accent-green);">{product['price']}</div>
                </div>
                <a href="{product['buy_url']}" target="_blank" rel="nofollow noopener" class="btn btn-buy" style="font-size: 16px; padding: 14px 32px; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);">🛒 Check Best Price / Buy Now</a>
            </div>
        </div>

        <div class="affiliate-disclaimer">
            ℹ️ <strong>Affiliate Disclosure:</strong> When you buy through links on BG Tech, we may earn an affiliate commission at no extra cost to you.
        </div>

        <!-- PROS & CONS -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:20px;">
                <h3 style="color:#166534; margin-bottom:12px; font-size: 18px;">Pros</h3>
                <ul style="list-style:none;">{pros_html}</ul>
            </div>
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:12px; padding:20px;">
                <h3 style="color:#991B1B; margin-bottom:12px; font-size: 18px;">Cons</h3>
                <ul style="list-style:none;">{cons_html}</ul>
            </div>
        </div>

        <!-- TECH SPECS -->
        <div style="background: white; border: 1px solid var(--border-color); border-radius: 12px; padding: 25px; margin-bottom: 30px;">
            <h3 style="margin-bottom: 15px; font-size: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 10px;">Technical Specifications</h3>
            <table style="width: 100%; border-collapse: collapse;">{specs_html}</table>
        </div>

        <!-- REVIEW HTML -->
        <div style="background: white; border: 1px solid var(--border-color); border-radius: 12px; padding: 30px; line-height: 1.8; font-size: 16px; color: #334155; margin-bottom: 40px;">
            <h2 style="margin-bottom: 20px; font-size: 24px; color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px;">Detailed Review & Expert Analysis</h2>
            {product.get('review_html', '')}
        </div>

        <!-- RELATED PRODUCTS SECTION -->
        <h3 class="section-title">🔥 Related Product Reviews</h3>
        <div class="grid" style="margin-bottom: 40px;">
            {related_html}
        </div>
    </main>

    <footer>
        <p><a href="../../index.html">Home</a> • <a href="../../index.html">About</a> • <a href="../../index.html">Privacy</a> • <a href="../../index.html">Disclaimer</a></p>
        <p style="margin-top:10px;">&copy; 2026 BG Tech. All rights reserved.</p>
    </footer>

    <script>
    function changeGalleryImage(imgSrc, element) {{
        const mainImg = document.getElementById('mainProductImg');
        if (!mainImg) return;
        mainImg.style.opacity = '0.3';
        setTimeout(() => {{
            mainImg.src = imgSrc;
            mainImg.style.opacity = '1';
        }}, 120);

        document.querySelectorAll('.thumb-btn').forEach(btn => btn.classList.remove('active'));
        if (element) element.classList.add('active');
    }}
    </script>
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
                        <a href="{p['buy_url']}" target="_blank" rel="nofollow noopener" class="btn btn-buy">Best Price</a>
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
    <meta name="description" content="Discover unbiased reviews, detailed specifications, pros, cons, and best deals on smartphones, smart TVs, soundbars, earbuds, and electronics.">
    <link rel="canonical" href="{SITE_BASE_URL}/index.html">
    <meta property="og:type" content="website">
    <meta property="og:title" content="BG Tech - Latest Tech Reviews, Specifications & Buying Guides (2026)">
    <meta property="og:description" content="Discover unbiased reviews, detailed specifications, pros, cons, and best deals on smartphones, smart TVs, soundbars, earbuds, and electronics.">
    <meta property="og:url" content="{SITE_BASE_URL}/index.html">
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
            <p style="font-size: 18px; color: #94A3B8; margin-bottom: 28px;">Expert Reviews • Specifications • Best Online Deals</p>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <a href="#trending" class="btn btn-buy" style="padding: 12px 24px; font-size: 15px;">Explore Latest Reviews</a>
            </div>
        </div>
    </section>

    <main class="container">
        <h2 class="section-title" id="trending">🔥 Trending Tech Reviews</h2>
        <div class="grid">
            {generate_cards(products[:4])}
        </div>

        {f'<h2 class="section-title" id="mobiles">📱 Latest Smartphones</h2><div class="grid">{generate_cards(mobiles)}</div>' if mobiles else ''}
        {f'<h2 class="section-title" id="tvs">📺 Smart TVs & Displays</h2><div class="grid">{generate_cards(tvs)}</div>' if tvs else ''}
        {f'<h2 class="section-title" id="headphones">🎧 Audio & Sound</h2><div class="grid">{generate_cards(headphones)}</div>' if headphones else ''}
        {f'<h2 class="section-title" id="gadgets">⚙️ Printers & Other Electronics</h2><div class="grid">{generate_cards(gadgets)}</div>' if gadgets else ''}
    </main>

    <footer>
        <p><a href="index.html">Home</a> • <a href="index.html">About</a> • <a href="index.html">Privacy</a> • <a href="index.html">Disclaimer</a></p>
        <p style="margin-top:10px;">&copy; 2026 BG Tech. All rights reserved.</p>
    </footer>
</body>
</html>"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html_content)

    # ============================================
    # SITEMAP.XML GENERATION (NEW)
    # ============================================
    today = date.today().isoformat()

    sitemap_urls = [
        {"loc": f"{SITE_BASE_URL}/index.html", "priority": "1.0"},
    ]
    for product in products:
        sitemap_urls.append({
            "loc": f"{SITE_BASE_URL}/products/{product['id']}/",
            "priority": "0.8"
        })

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in sitemap_urls:
        sitemap_xml += "  <url>\n"
        sitemap_xml += f"    <loc>{u['loc']}</loc>\n"
        sitemap_xml += f"    <lastmod>{today}</lastmod>\n"
        sitemap_xml += f"    <priority>{u['priority']}</priority>\n"
        sitemap_xml += "  </url>\n"
    sitemap_xml += "</urlset>"

    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    print(f"[SUCCESS] sitemap.xml generated with {len(sitemap_urls)} URLs!")
    print("[SUCCESS] Updated website layout, 5-image gallery & SEO Meta tags!")

if __name__ == "__main__":
    build_site()
