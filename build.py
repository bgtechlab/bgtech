import json
import os
import re
from datetime import date
from collections import OrderedDict

PRODUCTS_JSON_PATH = os.path.join("data", "products.json")
OUTPUT_DIR = "."
SITE_BASE_URL = "https://bgtechlab.github.io/bgtech"
DEFAULT_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop"

# Category display configuration
CATEGORY_CONFIG = OrderedDict([
    ("Mobiles",                {"title": "📱 Latest Smartphones",      "id": "mobiles",        "icon": "📱"}),
    ("TV",                     {"title": "📺 Smart TVs & Displays",    "id": "tvs",            "icon": "📺"}),
    ("Smart TV",               {"title": "📺 Smart TVs & Displays",    "id": "tvs",            "icon": "📺"}),
    ("Television",             {"title": "📺 Smart TVs & Displays",    "id": "tvs",            "icon": "📺"}),
    ("Audio",                  {"title": "🎧 Audio & Sound",           "id": "headphones",     "icon": "🎧"}),
    ("Headphones",             {"title": "🎧 Audio & Sound",           "id": "headphones",     "icon": "🎧"}),
    ("Laptops",                {"title": "💻 Laptops",                 "id": "laptops",        "icon": "💻"}),
    ("Printers",               {"title": "🖨️ Printers",                "id": "printers",       "icon": "🖨️"}),
    ("Smartwatches",           {"title": "⌚ Smartwatches",            "id": "smartwatches",   "icon": "⌚"}),
    ("Gadgets",                {"title": "⚙️ Gadgets & Accessories",   "id": "gadgets",        "icon": "⚙️"}),
    ("Kitchen",                {"title": "🍳 Kitchen",                 "id": "kitchen",        "icon": "🍳"}),
    ("Home & Kitchen",         {"title": "🏠 Home & Kitchen",          "id": "home-kitchen",   "icon": "🏠"}),
    ("Accessories",            {"title": "👜 Accessories",             "id": "accessories",    "icon": "👜"}),
    ("For Women",              {"title": "👩 For Women",               "id": "for-women",      "icon": "👩"}),
    ("Women Western",          {"title": "👗 Women Western",           "id": "women-western",  "icon": "👗"}),
    ("Kurti, Saree & Lehenga", {"title": "🥻 Kurti, Saree & Lehenga",  "id": "ethnic-wear",    "icon": "🥻"}),
    ("Lingerie",               {"title": "👙 Lingerie",                "id": "lingerie",       "icon": "👙"}),
    ("For Men",                {"title": "👨 For Men",                 "id": "for-men",        "icon": "👨"}),
    ("Men",                    {"title": "👨 Men",                     "id": "men",            "icon": "👨"}),
    ("Travel",                 {"title": "✈️ Travel",                  "id": "travel",         "icon": "✈️"}),
    ("Car & Motorbike",        {"title": "🚗 Car & Motorbike",         "id": "car-motorbike",  "icon": "🚗"}),
    ("Books",                  {"title": "📚 Books",                   "id": "books",          "icon": "📚"}),
])

def build_site():
    if not os.path.exists(PRODUCTS_JSON_PATH):
        print("❌ products.json file not found!")
        return

    with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    COMMON_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    :root {
        --bg-body: #F4F7FB;
        --bg-card: #FFFFFF;
        --primary-blue: #1A56DB;
        --primary-dark: #0F172A;
        --nav-dark: #0A192F;
        --nav-accent: #2563EB;
        --accent-cyan: #06B6D4;
        --accent-green: #059669;
        --accent-orange: #EA580C;
        --rating-gold: #F59E0B;
        --text-heading: #0F172A;
        --text-body: #334155;
        --text-muted: #64748B;
        --border-light: #E2E8F0;
        --border-subtle: #F1F5F9;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
        --shadow-lg: 0 10px 25px -5px rgba(15, 23, 42, 0.1);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    body { background-color: var(--bg-body); color: var(--text-body); line-height: 1.6; }
    a { text-decoration: none; color: inherit; }
    
    /* TOP MAIN HEADER */
    .top-header {
        background: #FFFFFF;
        border-bottom: 1px solid var(--border-light);
        padding: 12px 0;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .header-container {
        max-width: 1320px;
        margin: 0 auto;
        padding: 0 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }
    .brand-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
    }
    .logo-badge {
        background: linear-gradient(135deg, #1D4ED8 0%, #0284C7 100%);
        color: #FFFFFF;
        font-weight: 800;
        font-size: 22px;
        padding: 6px 12px;
        border-radius: 8px;
        letter-spacing: -0.5px;
        box-shadow: 0 2px 8px rgba(29, 78, 216, 0.3);
    }
    .brand-text-wrap {
        display: flex;
        flex-direction: column;
    }
    .brand-title {
        font-size: 21px;
        font-weight: 800;
        color: var(--text-heading);
        line-height: 1.1;
        letter-spacing: -0.3px;
    }
    .brand-title span {
        color: var(--primary-blue);
    }
    .brand-subtitle {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        letter-spacing: 0.2px;
    }
    
    /* SEARCH BAR */
    .header-search-wrap {
        flex: 1;
        max-width: 620px;
        position: relative;
    }
    .search-box {
        display: flex;
        align-items: center;
        background: #F8FAFC;
        border: 1.5px solid var(--border-light);
        border-radius: 30px;
        overflow: hidden;
        transition: all 0.2s ease;
    }
    .search-box:focus-within {
        border-color: var(--primary-blue);
        background: #FFFFFF;
        box-shadow: 0 0 0 4px rgba(26, 86, 219, 0.1);
    }
    .search-input {
        flex: 1;
        border: none;
        background: transparent;
        padding: 10px 18px;
        font-size: 14px;
        color: var(--text-heading);
        outline: none;
    }
    .search-btn {
        background: var(--primary-blue);
        color: white;
        border: none;
        padding: 10px 22px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: background 0.2s;
    }
    .search-btn:hover {
        background: #1E40AF;
    }
    
    /* USER ACTIONS */
    .header-user-actions {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .user-action-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-heading);
        cursor: pointer;
    }
    .user-action-item:hover {
        color: var(--primary-blue);
    }
    .action-icon {
        font-size: 18px;
    }
    
    /* NAV BAR (DARK) */
    .nav-bar-dark {
        background: var(--nav-dark);
        border-top: 1px solid rgba(255,255,255,0.06);
    }
    .nav-container {
        max-width: 1320px;
        margin: 0 auto;
        padding: 0 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .nav-menu-list {
        display: flex;
        align-items: center;
        list-style: none;
        overflow-x: auto;
        white-space: nowrap;
        scrollbar-width: none;
    }
    .nav-menu-list::-webkit-scrollbar { display: none; }
    .nav-menu-item a {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #E2E8F0;
        font-size: 13px;
        font-weight: 600;
        padding: 12px 14px;
        transition: all 0.2s;
    }
    .nav-menu-item a:hover, .nav-menu-item.active a {
        color: #FFFFFF;
        background: rgba(255,255,255,0.08);
    }
    .nav-trust-badges {
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 12px;
        font-weight: 600;
        color: #94A3B8;
    }
    .nav-trust-badges span {
        color: #38BDF8;
    }
    
    /* MAIN WRAPPER */
    .site-main-wrap {
        max-width: 1320px;
        margin: 24px auto;
        padding: 0 20px;
    }
    
    /* HERO SECTION */
    .hero-banner-section {
        background: linear-gradient(135deg, #EFF6FF 0%, #E0F2FE 55%, #F0FDF4 100%);
        border: 1px solid #BFDBFE;
        border-radius: var(--radius-lg);
        padding: 36px 36px 30px;
        margin-bottom: 28px;
        box-shadow: var(--shadow-sm);
        display: grid;
        grid-template-columns: 1.15fr 0.85fr;
        gap: 28px;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    .hero-content h1 {
        font-size: 36px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
        letter-spacing: -0.5px;
        margin-bottom: 12px;
    }
    .hero-badges-row {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 22px;
        font-size: 13px;
        font-weight: 600;
        color: #1E40AF;
    }
    .hero-badge-pill {
        background: rgba(255,255,255,0.85);
        border: 1px solid #BFDBFE;
        padding: 4px 12px;
        border-radius: 20px;
    }
    .hero-search-box {
        display: flex;
        background: #FFFFFF;
        border: 2px solid #3B82F6;
        border-radius: 30px;
        padding: 4px 6px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.12);
    }
    .hero-search-input {
        flex: 1;
        border: none;
        outline: none;
        padding: 10px 16px;
        font-size: 15px;
        color: #0F172A;
    }
    .hero-search-btn {
        background: #1D4ED8;
        color: #FFFFFF;
        border: none;
        border-radius: 24px;
        padding: 10px 24px;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
    }
    .hero-search-btn:hover { background: #1E40AF; }
    .popular-tags-wrap {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        font-size: 12px;
        color: #475569;
    }
    .popular-tag-btn {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        padding: 3px 10px;
        border-radius: 14px;
        font-weight: 600;
        color: #0F172A;
        cursor: pointer;
        transition: all 0.2s;
    }
    .popular-tag-btn:hover {
        border-color: #2563EB;
        color: #2563EB;
        background: #EFF6FF;
    }
    
    /* HERO RIGHT FEATURE CARDS */
    .hero-features-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .hero-feat-card {
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(255,255,255,0.8);
        border-radius: var(--radius-md);
        padding: 14px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        backdrop-filter: blur(4px);
    }
    .feat-icon-box {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    .feat-blue { background: #EFF6FF; color: #1D4ED8; }
    .feat-green { background: #ECFDF5; color: #059669; }
    .feat-cyan { background: #ECFEFF; color: #0891B2; }
    .feat-amber { background: #FFFBEB; color: #D97706; }
    .feat-text-box h4 {
        font-size: 13px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 2px;
    }
    .feat-text-box p {
        font-size: 11px;
        color: #64748B;
        line-height: 1.3;
    }
    
    /* SHOP BY CATEGORY TILES */
    .section-header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 32px 0 16px;
    }
    .section-heading {
        font-size: 20px;
        font-weight: 800;
        color: var(--text-heading);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-view-all {
        font-size: 13px;
        font-weight: 700;
        color: var(--primary-blue);
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .section-view-all:hover { text-decoration: underline; }
    
    .category-tiles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
        gap: 12px;
        margin-bottom: 30px;
    }
    .category-tile-card {
        background: #FFFFFF;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 14px 10px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    .category-tile-card:hover {
        transform: translateY(-3px);
        border-color: var(--primary-blue);
        box-shadow: var(--shadow-md);
    }
    .cat-tile-icon {
        font-size: 28px;
    }
    .cat-tile-title {
        font-size: 12px;
        font-weight: 700;
        color: var(--text-heading);
        line-height: 1.2;
    }
    
    /* 2-COLUMN MAIN CONTENT + SIDEBAR LAYOUT */
    .content-sidebar-layout {
        display: grid;
        grid-template-columns: 1fr 340px;
        gap: 28px;
        align-items: flex-start;
    }
    
    /* PRODUCT CARDS GRID */
    .products-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 18px;
    }
    .product-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: var(--shadow-sm);
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
        border-color: #CBD5E1;
    }
    .card-img-box {
        background: #FFFFFF;
        height: 190px;
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #F1F5F9;
        position: relative;
    }
    .card-img-box img {
        max-height: 100%;
        max-width: 100%;
        object-fit: contain;
        transition: transform 0.3s;
    }
    .product-card:hover .card-img-box img {
        transform: scale(1.04);
    }
    .card-category-badge {
        position: absolute;
        top: 10px;
        left: 10px;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
    }
    .card-info {
        padding: 16px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .card-title-link {
        font-size: 15px;
        font-weight: 700;
        color: var(--text-heading);
        line-height: 1.35;
        margin-bottom: 6px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        height: 40px;
    }
    .card-title-link:hover { color: var(--primary-blue); }
    .card-rating-row {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 600;
        color: #F59E0B;
        margin-bottom: 10px;
    }
    .card-rating-count {
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
    }
    .card-price-row {
        margin-top: auto;
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .card-price {
        font-size: 19px;
        font-weight: 800;
        color: var(--accent-green);
    }
    .card-btn-action {
        display: block;
        text-align: center;
        background: var(--primary-blue);
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 700;
        padding: 9px 14px;
        border-radius: var(--radius-sm);
        transition: background 0.2s;
    }
    .card-btn-action:hover {
        background: #1E40AF;
    }
    
    /* PROMO 4-BOX CARDS */
    .promo-banners-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin: 28px 0;
    }
    .promo-card {
        background: #FFFFFF;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        box-shadow: var(--shadow-sm);
    }
    .promo-card h5 {
        font-size: 13px;
        font-weight: 800;
        color: #0F172A;
    }
    .promo-card p {
        font-size: 11px;
        color: var(--text-muted);
        margin: 2px 0 6px;
    }
    .promo-card a {
        font-size: 11px;
        font-weight: 700;
        color: var(--primary-blue);
    }
    .promo-thumb {
        width: 46px;
        height: 46px;
        object-fit: contain;
        flex-shrink: 0;
    }
    
    /* LATEST REVIEWS STRIP */
    .reviews-mini-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
        gap: 14px;
        margin-bottom: 30px;
    }
    .review-mini-card {
        background: #FFFFFF;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: var(--shadow-sm);
    }
    .review-mini-img {
        width: 48px;
        height: 48px;
        object-fit: contain;
        flex-shrink: 0;
    }
    .review-mini-info h6 {
        font-size: 13px;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
        margin-bottom: 4px;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .review-mini-meta {
        font-size: 11px;
        color: #64748B;
        display: flex;
        gap: 8px;
    }
    
    /* SIDEBAR WIDGETS */
    .sidebar-widget {
        background: #FFFFFF;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-sm);
    }
    .widget-title {
        font-size: 16px;
        font-weight: 800;
        color: var(--text-heading);
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border-subtle);
    }
    .widget-title a {
        font-size: 12px;
        font-weight: 700;
        color: var(--primary-blue);
    }
    
    .top-rated-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .top-rated-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid #F1F5F9;
    }
    .top-rated-item:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }
    .top-rated-thumb {
        width: 44px;
        height: 44px;
        object-fit: contain;
        flex-shrink: 0;
    }
    .top-rated-details {
        flex: 1;
    }
    .top-rated-details h6 {
        font-size: 12px;
        font-weight: 700;
        color: #0F172A;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .top-rated-meta {
        font-size: 11px;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .top-rated-price {
        font-size: 12px;
        font-weight: 800;
        color: var(--accent-green);
    }
    .top-rated-view-btn {
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
    }
    .top-rated-view-btn:hover { background: #DBEAFE; }
    
    /* STORE COMPARISON TABLE */
    .store-compare-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }
    .store-compare-table th {
        text-align: left;
        color: #64748B;
        font-weight: 600;
        padding: 6px 8px;
        border-bottom: 1px solid var(--border-light);
    }
    .store-compare-table td {
        padding: 8px 8px;
        border-bottom: 1px solid #F8FAFC;
        color: #0F172A;
    }
    .stock-badge-green {
        color: #059669;
        font-weight: 600;
    }
    .store-buy-mini {
        background: #F59E0B;
        color: #FFFFFF;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
    }
    
    /* ADVISORY CTA BOX */
    .advisory-cta-card {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 1px solid #A7F3D0;
        border-radius: var(--radius-md);
        padding: 16px;
        text-align: center;
    }
    .advisory-cta-card h5 {
        font-size: 14px;
        font-weight: 800;
        color: #065F46;
        margin-bottom: 6px;
    }
    .advisory-cta-card p {
        font-size: 11px;
        color: #047857;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .advisory-btn {
        display: inline-block;
        background: #059669;
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 700;
        padding: 8px 18px;
        border-radius: 20px;
        box-shadow: 0 2px 6px rgba(5, 150, 105, 0.3);
    }
    .advisory-btn:hover { background: #047857; }
    
    /* PRODUCT HERO & GALLERY (FOR REVIEW PAGES) */
    .product-hero {
        background: #FFFFFF;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-sm);
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
        border: 2px solid var(--border-light);
        border-radius: 8px;
        padding: 5px;
        cursor: pointer;
        background: #FFFFFF;
        object-fit: contain;
        transition: all 0.2s ease-in-out;
    }
    .thumb-btn:hover, .thumb-btn.active {
        border-color: var(--primary-blue);
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
        border-top: 1px solid var(--border-light);
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
        background: #EFF6FF;
        padding: 10px 14px;
        border-radius: 6px;
        border-left: 3px solid var(--primary-blue);
    }
    
    /* FOOTER (DARK) */
    .site-footer {
        background: #0A192F;
        color: #94A3B8;
        padding: 50px 0 24px;
        margin-top: 60px;
        border-top: 1px solid rgba(255,255,255,0.08);
    }
    .footer-container {
        max-width: 1320px;
        margin: 0 auto;
        padding: 0 20px;
    }
    .footer-top-grid {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1fr 1fr 1.5fr;
        gap: 30px;
        margin-bottom: 40px;
    }
    .footer-col h5 {
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 14px;
    }
    .footer-links {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 8px;
        font-size: 13px;
    }
    .footer-links a:hover {
        color: #38BDF8;
    }
    .newsletter-form {
        display: flex;
        gap: 6px;
        margin-top: 10px;
    }
    .newsletter-input {
        flex: 1;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        outline: none;
    }
    .newsletter-btn {
        background: var(--primary-blue);
        color: white;
        border: none;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
    }
    .footer-bottom-row {
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
    }
    
    @media (max-width: 992px) {
        .content-sidebar-layout { grid-template-columns: 1fr; }
        .hero-banner-section { grid-template-columns: 1fr; padding: 24px; }
        .promo-banners-row { grid-template-columns: 1fr 1fr; }
        .footer-top-grid { grid-template-columns: 1fr 1fr; }
        .header-search-wrap { display: none; }
    }
    @media (max-width: 680px) {
        .promo-banners-row { grid-template-columns: 1fr; }
        .footer-top-grid { grid-template-columns: 1fr; }
        .gallery-container { flex-direction: column-reverse; }
        .thumbnail-side { flex-direction: row; width: 100%; justify-content: center; overflow-x: auto; }
        .thumb-btn { width: 60px; height: 60px; }
        .buy-action-bar { flex-direction: column; text-align: center; }
        .header-user-actions { display: none; }
    }
    """

    # ========== NAV LINKS DEFINITION ==========
    nav_links_html = """
        <li class="nav-menu-item active"><a href="{PREFIX}index.html">🏠 Home</a></li>
        <li class="nav-menu-item"><a href="{PREFIX}index.html#categories">📑 All Categories</a></li>
        <li class="nav-menu-item"><a href="{PREFIX}index.html#trending">🔥 Best Deals</a></li>
        <li class="nav-menu-item"><a href="{PREFIX}index.html#top-rated">⭐ Top Rated</a></li>
        <li class="nav-menu-item"><a href="{PREFIX}index.html#compare">⚖️ Compare Products</a></li>
        <li class="nav-menu-item"><a href="{PREFIX}index.html#reviews">📝 Reviews</a></li>
        <li class="nav-menu-item"><a href="{PREFIX}index.html#about">ℹ️ About Us</a></li>
        <li class="nav-menu-item"><a href="{PREFIX}index.html#contact">📞 Contact</a></li>
    """

    def get_header(prefix=""):
        p = prefix
        return f"""
    <header class="top-header">
        <div class="header-container">
            <a href="{p}index.html" class="brand-logo">
                <div class="logo-badge">BG</div>
                <div class="brand-text-wrap">
                    <div class="brand-title">Product<span>Check</span></div>
                    <div class="brand-subtitle">Reviews | Compare | Buy Smart</div>
                </div>
            </a>
            
            <div class="header-search-wrap">
                <div class="search-box">
                    <input type="text" id="mainSearchInput" class="search-input" placeholder="Search for products, brands and categories..." onkeyup="filterLiveProducts(this.value)">
                    <button class="search-btn" onclick="triggerSearch()">🔍 Search</button>
                </div>
            </div>
            
            <div class="header-user-actions">
                <div class="user-action-item">
                    <span class="action-icon">👤</span>
                    <div>
                        <div style="font-size:11px; color:#64748B;">Sign In</div>
                        <div style="font-size:12px;">My Account</div>
                    </div>
                </div>
                <div class="user-action-item">
                    <span class="action-icon">❤️</span>
                    <div style="font-size:12px;">Wishlist</div>
                </div>
                <div class="user-action-item">
                    <span class="action-icon">🛒</span>
                    <div style="font-size:12px;">Cart</div>
                </div>
            </div>
        </div>
    </header>
    
    <nav class="nav-bar-dark">
        <div class="nav-container">
            <ul class="nav-menu-list">
                {nav_links_html.replace('{PREFIX}', p)}
            </ul>
            <div class="nav-trust-badges">
                <div><span>✓</span> Trusted Reviews</div>
                <div><span>•</span> Best Prices</div>
                <div><span>•</span> Smart Buying</div>
            </div>
        </div>
    </nav>
    """

    def get_footer(prefix=""):
        p = prefix
        return f"""
    <footer class="site-footer">
        <div class="footer-container">
            <div class="footer-top-grid">
                <div class="footer-col">
                    <a href="{p}index.html" class="brand-logo" style="margin-bottom:12px; display:inline-flex;">
                        <div class="logo-badge">BG</div>
                        <div class="brand-text-wrap">
                            <div class="brand-title" style="color:white;">Product<span style="color:#38BDF8;">Check</span></div>
                            <div class="brand-subtitle" style="color:#94A3B8;">Reviews | Compare | Buy Smart</div>
                        </div>
                    </a>
                    <p style="font-size:13px; line-height:1.6; margin-top:8px;">Your trusted companion for in-depth tech & consumer product reviews, price comparisons, and buying guides in India.</p>
                </div>
                <div class="footer-col">
                    <h5>Quick Links</h5>
                    <ul class="footer-links">
                        <li><a href="{p}index.html">Home</a></li>
                        <li><a href="{p}index.html#categories">All Categories</a></li>
                        <li><a href="{p}index.html#trending">Best Deals</a></li>
                        <li><a href="{p}index.html#top-rated">Top Rated</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h5>Help & Support</h5>
                    <ul class="footer-links">
                        <li><a href="{p}index.html#contact">Contact Us</a></li>
                        <li><a href="{p}index.html">Privacy Policy</a></li>
                        <li><a href="{p}index.html">Terms & Conditions</a></li>
                        <li><a href="{p}index.html">Affiliate Disclosure</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h5>Follow Us</h5>
                    <div style="display:flex; gap:10px; font-size:20px; margin-top:10px;">
                        <a href="https://t.me/bglarenup" target="_blank" title="Telegram">✈️</a>
                        <a href="#" title="YouTube">📺</a>
                        <a href="#" title="Instagram">📷</a>
                        <a href="#" title="Facebook">🌐</a>
                    </div>
                </div>
                <div class="footer-col">
                    <h5>Get Latest Updates</h5>
                    <p style="font-size:12px; margin-bottom:10px;">Subscribe to our newsletter for latest expert reviews and hot deals.</p>
                    <div class="newsletter-form">
                        <input type="email" placeholder="Enter your email" class="newsletter-input">
                        <button class="newsletter-btn">Subscribe</button>
                    </div>
                </div>
            </div>
            <div class="footer-bottom-row">
                <div>&copy; 2026 BG ProductCheck. All rights reserved.</div>
                <div>Made with ❤️ for Smart Shoppers</div>
            </div>
        </div>
    </footer>
    """

    # ========== 1. GENERATE DETAIL PRODUCT PAGES ==========
    for product in products:
        product_slug = product["id"]
        prod_dir = os.path.join("products", product_slug)
        os.makedirs(prod_dir, exist_ok=True)

        page_canonical_url = f"{SITE_BASE_URL}/products/{product_slug}/"

        raw_images = product.get("images", [])
        if not raw_images:
            raw_images = [product.get("image", DEFAULT_FALLBACK_IMAGE)]

        gallery_5_images = list(raw_images)
        while len(gallery_5_images) < 5:
            gallery_5_images.append(gallery_5_images[len(gallery_5_images) % len(raw_images)])
        gallery_5_images = gallery_5_images[:5]

        main_img_url = gallery_5_images[0]
        product_short_name = product.get("short_name", "Product")

        thumbs_html = ""
        for idx, img_url in enumerate(gallery_5_images):
            active_cls = " active" if idx == 0 else ""
            thumbs_html += f'<img src="{img_url}" class="thumb-btn{active_cls}" onclick="changeGalleryImage(\'{img_url}\', this)" onmouseover="changeGalleryImage(\'{img_url}\', this)" alt="{product_short_name} Image {idx+1}">\n'

        pros_html = "".join([f"<li style='margin-bottom:8px; color:#15803D;'>✓ {p}</li>" for p in product.get("pros", [])])
        cons_html = "".join([f"<li style='margin-bottom:8px; color:#B91C1C;'>✕ {c}</li>" for c in product.get("cons", [])])

        specs_html = ""
        for key, val in product.get("specs", {}).items():
            specs_html += f"<tr><td style='padding:12px; border-bottom:1px solid #E2E8F0; font-weight:600; color:#475569;'>{key}</td><td style='padding:12px; border-bottom:1px solid #E2E8F0; color:#0F172A;'>{val}</td></tr>"

        meta_desc = f"Read detailed review of {product['short_name']} on BG ProductCheck. Check specs, price in India, pros, cons, and expert performance rating."

        raw_price = product.get('price', '')
        clean_num_price = re.sub(r'[^\d]', '', raw_price)
        schema_price = clean_num_price if clean_num_price else "0"

        category_name = product.get('category', 'Gadgets')

        related_items = [p for p in products if p['id'] != product_slug][:4]
        related_html = ""
        for rel in related_items:
            related_html += f"""
            <div class="product-card">
                <div class="card-img-box">
                    <span class="card-category-badge">{rel.get('category', 'Gadgets')}</span>
                    <img src="{rel['image']}" alt="{rel['short_name']}">
                </div>
                <div class="card-info">
                    <a href="../{rel['id']}/" class="card-title-link">{rel['short_name']}</a>
                    <div class="card-rating-row">
                        <span>★</span> {rel.get('rating', '4.2 out of 5 stars')}
                    </div>
                    <div class="card-price-row">
                        <div class="card-price">{rel['price']}</div>
                    </div>
                    <a href="../{rel['id']}/" class="card-btn-action">View Review ➔</a>
                </div>
            </div>"""

        prod_html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product['title']} - BG ProductCheck</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{product['short_name']}, {product['short_name']} review, {product['short_name']} price, BG ProductCheck">
    <link rel="canonical" href="{page_canonical_url}">
    
    <meta property="og:type" content="article">
    <meta property="og:title" content="{product['title']} - BG ProductCheck">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="{main_img_url}">
    <meta property="og:url" content="{page_canonical_url}">
    
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{product['title']} - BG ProductCheck">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{main_img_url}">
    
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
        "name": "BG ProductCheck"
      }},
      "aggregateRating": {{
        "@type": "AggregateRating",
        "ratingValue": "4.4",
        "bestRating": "5",
        "worstRating": "1",
        "ratingCount": "180"
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
    <style>{COMMON_CSS}</style>
</head>
<body>
    {get_header("../../")}
    
    <main class="site-main-wrap" style="max-width: 1040px;">
        <div style="font-size: 13px; color: var(--text-muted); margin: 15px 0 10px;">
            <a href="../../index.html" style="color:var(--primary-blue);">Home</a> &rsaquo; 
            <a href="../../index.html#{category_name.lower().replace(' ', '-')}" style="color:var(--primary-blue);">{category_name}</a> &rsaquo; 
            <span>{product['short_name']}</span>
        </div>
        
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <span style="background:#EFF6FF; color:#1D4ED8; font-size:12px; font-weight:700; padding:4px 10px; border-radius:20px;">{category_name}</span>
            <span style="color:#059669; font-size:12px; font-weight:700;">✓ Verified Expert Review</span>
        </div>
        
        <h1 style="font-size: 28px; font-weight: 800; margin-bottom: 8px; color: var(--text-heading);">{product['title']}</h1>
        <div style="font-size: 15px; font-weight:600; color: #F59E0B; margin-bottom: 20px;">★ {product.get('rating', '4.2 out of 5 stars')} | Tested by BG ProductCheck Team</div>
        
        <!-- 5-IMAGE SIDE GALLERY HERO SECTION -->
        <div class="product-hero">
            <div class="gallery-container">
                <div class="thumbnail-side">
                    {thumbs_html}
                </div>
                <div class="main-image-box">
                    <img id="mainProductImg" src="{main_img_url}" alt="{product['short_name']}">
                </div>
            </div>
            <div class="buy-action-bar">
                <div>
                    <div style="font-size: 12px; color: var(--text-muted);">Current Best Deal Price</div>
                    <div style="font-size: 32px; font-weight: 800; color: var(--accent-green);">{product['price']}</div>
                </div>
                <a href="{product['buy_url']}" target="_blank" rel="nofollow noopener" class="hero-search-btn" style="font-size: 16px; padding: 14px 36px; text-decoration:none;">🛒 Check Best Price / Buy Now</a>
            </div>
        </div>
        
        <div class="affiliate-disclaimer">
            ℹ️ <strong>Affiliate Disclosure:</strong> When you buy through links on <strong>BG ProductCheck</strong>, we may earn an affiliate commission at no extra cost to you.
        </div>
        
        <!-- PROS & CONS -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:20px;">
                <h3 style="color:#166534; margin-bottom:12px; font-size: 18px; font-weight:800;">👍 What We Like (Pros)</h3>
                <ul style="list-style:none;">{pros_html}</ul>
            </div>
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:12px; padding:20px;">
                <h3 style="color:#991B1B; margin-bottom:12px; font-size: 18px; font-weight:800;">👎 Keep in Mind (Cons)</h3>
                <ul style="list-style:none;">{cons_html}</ul>
            </div>
        </div>
        
        <!-- TECH SPECS -->
        <div style="background: white; border: 1px solid var(--border-light); border-radius: 12px; padding: 25px; margin-bottom: 30px; box-shadow:var(--shadow-sm);">
            <h3 style="margin-bottom: 15px; font-size: 20px; font-weight:800; border-bottom: 2px solid var(--border-light); padding-bottom: 10px;">Technical Specifications</h3>
            <table style="width: 100%; border-collapse: collapse;">{specs_html}</table>
        </div>
        
        <!-- REVIEW HTML -->
        <div style="background: white; border: 1px solid var(--border-light); border-radius: 12px; padding: 32px; line-height: 1.8; font-size: 16px; color: #334155; margin-bottom: 40px; box-shadow:var(--shadow-sm);">
            <h2 style="margin-bottom: 20px; font-size: 24px; font-weight:800; color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px;">Detailed Review & Expert Analysis</h2>
            {product.get('review_html', '')}
        </div>
        
        <!-- RELATED PRODUCTS SECTION -->
        <h3 class="section-heading" style="margin-bottom:18px;">🔥 Related Product Reviews</h3>
        <div class="products-grid" style="margin-bottom: 40px;">
            {related_html}
        </div>
    </main>
    
    {get_footer("../../")}
    
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

    # ========== 2. HOMEPAGE BUILDING ==========
    def generate_product_cards(items):
        html = ""
        for p in items:
            html += f"""
            <div class="product-card" data-title="{p['short_name'].lower()}" data-category="{p.get('category', '').lower()}">
                <div class="card-img-box">
                    <span class="card-category-badge">{p.get('category', 'Gadgets')}</span>
                    <img src="{p['image']}" alt="{p['short_name']}">
                </div>
                <div class="card-info">
                    <a href="products/{p['id']}/" class="card-title-link">{p['short_name']}</a>
                    <div class="card-rating-row">
                        <span>★</span> {p.get('rating', '4.2 out of 5 stars')}
                    </div>
                    <div class="card-price-row">
                        <div class="card-price">{p['price']}</div>
                    </div>
                    <a href="products/{p['id']}/" class="card-btn-action">View Details ➔</a>
                </div>
            </div>"""
        return html

    # Category Tiles HTML
    cat_tiles_html = ""
    seen_cat_ids = set()
    for cat_name, cfg in CATEGORY_CONFIG.items():
        if cfg["id"] not in seen_cat_ids:
            cat_tiles_html += f"""
            <a href="#{cfg['id']}" class="category-tile-card">
                <div class="cat-tile-icon">{cfg.get('icon', '📦')}</div>
                <div class="cat-tile-title">{cat_name}</div>
            </a>"""
            seen_cat_ids.add(cfg["id"])

    # Group products by category ID
    category_groups = OrderedDict()
    for cat, cfg in CATEGORY_CONFIG.items():
        section_id = cfg["id"]
        if section_id not in category_groups:
            category_groups[section_id] = {
                "title": cfg["title"],
                "products": []
            }

    for p in products:
        cat = p.get("category", "Gadgets")
        cfg = CATEGORY_CONFIG.get(cat)
        if cfg:
            section_id = cfg["id"]
            category_groups[section_id]["products"].append(p)
        else:
            slug = re.sub(r'[^a-z0-9]+', '-', cat.lower()).strip('-')
            if slug not in category_groups:
                category_groups[slug] = {"title": cat, "products": []}
            category_groups[slug]["products"].append(p)

    # Category Sections HTML
    category_sections_html = ""
    for section_id, data in category_groups.items():
        if data["products"]:
            category_sections_html += f"""
            <div class="category-section-block" style="margin-top: 36px;">
                <div class="section-header-row">
                    <h2 class="section-heading" id="{section_id}">{data["title"]}</h2>
                    <a href="#{section_id}" class="section-view-all">View All ({len(data['products'])}) ➔</a>
                </div>
                <div class="products-grid">
                    {generate_product_cards(data["products"])}
                </div>
            </div>"""

    # Top Rated list for sidebar
    top_rated_sidebar_html = ""
    for p in products[:5]:
        top_rated_sidebar_html += f"""
        <div class="top-rated-item">
            <img src="{p['image']}" class="top-rated-thumb" alt="{p['short_name']}">
            <div class="top-rated-details">
                <a href="products/{p['id']}/"><h6>{p['short_name']}</h6></a>
                <div class="top-rated-meta">
                    <span style="color:#F59E0B;">★ {p.get('rating', '4.4')}</span>
                    <span class="top-rated-price">{p['price']}</span>
                </div>
            </div>
            <a href="products/{p['id']}/" class="top-rated-view-btn">View</a>
        </div>"""

    # Latest Reviews Mini List
    latest_reviews_html = ""
    for p in products[:4]:
        latest_reviews_html += f"""
        <a href="products/{p['id']}/" class="review-mini-card">
            <img src="{p['image']}" class="review-mini-img" alt="{p['short_name']}">
            <div class="review-mini-info">
                <h6>{p['short_name']} Review</h6>
                <div class="review-mini-meta">
                    <span>⏱️ 5 min read</span>
                    <span style="color:#F59E0B;">★ 4.5</span>
                </div>
            </div>
        </a>"""

    # Promo Row 4 Cards (Mockup representation)
    p_img1 = products[0]['image'] if len(products) > 0 else DEFAULT_FALLBACK_IMAGE
    p_img2 = products[1]['image'] if len(products) > 1 else DEFAULT_FALLBACK_IMAGE
    p_img3 = products[2]['image'] if len(products) > 2 else DEFAULT_FALLBACK_IMAGE
    p_img4 = products[3]['image'] if len(products) > 3 else DEFAULT_FALLBACK_IMAGE

    promo_row_html = f"""
    <div class="promo-banners-row" id="compare">
        <div class="promo-card">
            <div>
                <h5>🏷️ Best Deals</h5>
                <p>UPTO 70% OFF Top Deals</p>
                <a href="#trending">Shop Now ➔</a>
            </div>
            <img src="{p_img1}" class="promo-thumb" alt="Best Deals">
        </div>
        <div class="promo-card">
            <div>
                <h5>⭐ Top Rated</h5>
                <p>Highly Rated by Users</p>
                <a href="#top-rated">View Top Rated ➔</a>
            </div>
            <img src="{p_img2}" class="promo-thumb" alt="Top Rated">
        </div>
        <div class="promo-card">
            <div>
                <h5>⚖️ Compare Specs</h5>
                <p>Find the Best Choice</p>
                <a href="#categories">Compare Now ➔</a>
            </div>
            <img src="{p_img3}" class="promo-thumb" alt="Compare Products">
        </div>
        <div class="promo-card">
            <div>
                <h5>🚀 New Launches</h5>
                <p>Latest Products Added</p>
                <a href="#trending">Explore Now ➔</a>
            </div>
            <img src="{p_img4}" class="promo-thumb" alt="New Arrivals">
        </div>
    </div>
    """

    index_html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BG ProductCheck - Expert Product Reviews, Price Comparison & Buying Guides (2026)</title>
    <meta name="description" content="BG ProductCheck helps you discover authentic reviews, specifications, price comparisons, pros & cons for smartphones, smart TVs, kitchen appliances, fashion, and tech gadgets.">
    <link rel="canonical" href="{SITE_BASE_URL}/index.html">
    <meta property="og:type" content="website">
    <meta property="og:title" content="BG ProductCheck - Expert Product Reviews & Buying Guides">
    <meta property="og:description" content="Find the right product before you buy. Real reviews, honest opinions, and best online deals.">
    <meta property="og:url" content="{SITE_BASE_URL}/index.html">
    <style>{COMMON_CSS}</style>
</head>
<body>
    {get_header("")}
    
    <main class="site-main-wrap">
        <!-- HERO BANNER SECTION -->
        <section class="hero-banner-section">
            <div class="hero-content">
                <h1>Find the Right Product<br>Before You Buy</h1>
                <div class="hero-badges-row">
                    <span class="hero-badge-pill">Real Reviews</span>
                    <span class="hero-badge-pill">Honest Opinions</span>
                    <span class="hero-badge-pill">Best Prices</span>
                    <span class="hero-badge-pill">Easy Comparison</span>
                </div>
                
                <div class="hero-search-box">
                    <input type="text" id="heroSearchInput" class="hero-search-input" placeholder="Search for products (e.g. iPhone, Laptop, Soundbar, Smart TV)..." onkeyup="filterLiveProducts(this.value)">
                    <button class="hero-search-btn" onclick="triggerSearch()">🔍 Search</button>
                </div>
                
                <div class="popular-tags-wrap">
                    <span style="font-weight:700;">Popular Searches:</span>
                    <button class="popular-tag-btn" onclick="applySearchTag('iPhone')">iPhone</button>
                    <button class="popular-tag-btn" onclick="applySearchTag('Laptop')">Laptop</button>
                    <button class="popular-tag-btn" onclick="applySearchTag('Soundbar')">Soundbar</button>
                    <button class="popular-tag-btn" onclick="applySearchTag('Smart TV')">Smart TV</button>
                    <button class="popular-tag-btn" onclick="applySearchTag('Kitchen')">Kitchen</button>
                    <button class="popular-tag-btn" onclick="applySearchTag('Watch')">Smartwatch</button>
                </div>
            </div>
            
            <div class="hero-features-grid">
                <div class="hero-feat-card">
                    <div class="feat-icon-box feat-blue">📝</div>
                    <div class="feat-text-box">
                        <h4>Expert Reviews</h4>
                        <p>Detailed & Honest Reviews</p>
                    </div>
                </div>
                <div class="hero-feat-card">
                    <div class="feat-icon-box feat-green">📊</div>
                    <div class="feat-text-box">
                        <h4>Price Comparison</h4>
                        <p>Find the Best Price</p>
                    </div>
                </div>
                <div class="hero-feat-card">
                    <div class="feat-icon-box feat-cyan">🛡️</div>
                    <div class="feat-text-box">
                        <h4>Verified Links</h4>
                        <p>Safe & Trusted Stores</p>
                    </div>
                </div>
                <div class="hero-feat-card">
                    <div class="feat-icon-box feat-amber">🏷️</div>
                    <div class="feat-text-box">
                        <h4>Best Deals</h4>
                        <p>Save More Every Day</p>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- SHOP BY CATEGORY SECTION -->
        <section id="categories">
            <div class="section-header-row">
                <h2 class="section-heading">📑 Shop by Category</h2>
                <a href="#categories" class="section-view-all">View All Categories ➔</a>
            </div>
            <div class="category-tiles-grid">
                {cat_tiles_html}
            </div>
        </section>
        
        <!-- MAIN CONTENT + SIDEBAR GRID -->
        <div class="content-sidebar-layout">
            <!-- LEFT MAIN COLUMN -->
            <div class="main-column">
                <!-- TRENDING PRODUCTS -->
                <section id="trending">
                    <div class="section-header-row" style="margin-top:0;">
                        <h2 class="section-heading">🔥 Trending Products</h2>
                        <a href="#trending" class="section-view-all">View All ➔</a>
                    </div>
                    <div class="products-grid" id="mainProductsGrid">
                        {generate_product_cards(products[:6])}
                    </div>
                </section>
                
                <!-- PROMO 4-BOX ROW -->
                {promo_row_html}
                
                <!-- LATEST REVIEWS SECTION -->
                <section id="reviews" style="margin-top: 10px;">
                    <div class="section-header-row">
                        <h2 class="section-heading">📰 Latest In-Depth Reviews</h2>
                        <a href="#reviews" class="section-view-all">View All Reviews ➔</a>
                    </div>
                    <div class="reviews-mini-grid">
                        {latest_reviews_html}
                    </div>
                </section>
                
                <!-- CATEGORY BY CATEGORY SHOWCASE -->
                {category_sections_html}
            </div>
            
            <!-- RIGHT SIDEBAR -->
            <aside class="sidebar-column">
                <!-- TOP RATED WIDGET -->
                <div class="sidebar-widget" id="top-rated">
                    <div class="widget-title">
                        <span>⭐ Top Rated Products</span>
                        <a href="#top-rated">View All ➔</a>
                    </div>
                    <div class="top-rated-list">
                        {top_rated_sidebar_html}
                    </div>
                </div>
                
                <!-- PRICE COMPARISON WIDGET -->
                <div class="sidebar-widget">
                    <div class="widget-title">
                        <span>💰 Price Comparison</span>
                        <a href="#trending">Live Tracker</a>
                    </div>
                    <p style="font-size:11px; color:#64748B; margin-bottom:10px;">Find the best verified prices across top Indian stores.</p>
                    <table class="store-compare-table">
                        <thead>
                            <tr>
                                <th>Store</th>
                                <th>Price</th>
                                <th>Stock</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>🛒 Amazon</td>
                                <td style="font-weight:700;">Best Price</td>
                                <td class="stock-badge-green">In Stock</td>
                                <td><a href="#trending" class="store-buy-mini">Buy</a></td>
                            </tr>
                            <tr>
                                <td>⚡ Flipkart</td>
                                <td style="font-weight:700;">Best Price</td>
                                <td class="stock-badge-green">In Stock</td>
                                <td><a href="#trending" class="store-buy-mini">Buy</a></td>
                            </tr>
                            <tr>
                                <td>👗 Myntra</td>
                                <td style="font-weight:700;">Verified</td>
                                <td class="stock-badge-green">In Stock</td>
                                <td><a href="#trending" class="store-buy-mini">Buy</a></td>
                            </tr>
                            <tr>
                                <td>🛍️ Meesho</td>
                                <td style="font-weight:700;">Verified</td>
                                <td class="stock-badge-green">In Stock</td>
                                <td><a href="#trending" class="store-buy-mini">Buy</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- ADVISORY CARD -->
                <div class="advisory-cta-card" id="about">
                    <div style="font-size:26px; margin-bottom:6px;">⚖️</div>
                    <h5>सही प्रोडक्ट चुनना है मुश्किल?</h5>
                    <p>BG ProductCheck पर हम लाए हैं आपके लिए पर्सनलाइज्ड सुझाव और 100% अनबायस्ड एक्सपर्ट रिव्यू।</p>
                    <a href="#categories" class="advisory-btn">Get Recommendation ➔</a>
                </div>
            </aside>
        </div>
    </main>
    
    {get_footer("")}
    
    <script>
    function filterLiveProducts(query) {{
        const q = query.toLowerCase().trim();
        const cards = document.querySelectorAll('.product-card');
        let matchCount = 0;
        cards.forEach(card => {{
            const title = card.getAttribute('data-title') || '';
            const cat = card.getAttribute('data-category') || '';
            if (!q || title.includes(q) || cat.includes(q)) {{
                card.style.display = 'flex';
                matchCount++;
            }} else {{
                card.style.display = 'none';
            }}
        }});
    }}
    
    function applySearchTag(tag) {{
        const mainInput = document.getElementById('mainSearchInput');
        const heroInput = document.getElementById('heroSearchInput');
        if (mainInput) mainInput.value = tag;
        if (heroInput) heroInput.value = tag;
        filterLiveProducts(tag);
        const trendingSection = document.getElementById('trending');
        if (trendingSection) trendingSection.scrollIntoView({{ behavior: 'smooth' }});
    }}
    
    function triggerSearch() {{
        const heroInput = document.getElementById('heroSearchInput');
        const val = heroInput ? heroInput.value : '';
        filterLiveProducts(val);
        const trendingSection = document.getElementById('trending');
        if (trendingSection) trendingSection.scrollIntoView({{ behavior: 'smooth' }});
    }}
    </script>
</body>
</html>"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html_content)

    # ========== 3. SITEMAP GENERATION ==========
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

    print(f"[SUCCESS] BG ProductCheck Theme Built Successfully! ({len(products)} products processed)")

if __name__ == "__main__":
    build_site()
