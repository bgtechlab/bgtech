import asyncio
from collections import OrderedDict
from datetime import datetime, timezone
import json
import logging
import os
import re
import subprocess
import time
import urllib.parse
import warnings
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from g4f.client import Client
import requests
from telegram import Bot

warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

try:
    from google import genai as google_genai
    GENAI_NEW_SDK = True
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GENAI_NEW_SDK = False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import google.generativeai as genai
        GEMINI_SDK_AVAILABLE = True
    except ImportError:
        GEMINI_SDK_AVAILABLE = False

load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ================= 1. CONFIGURATION & CATEGORIES =================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SITE_BASE_URL = os.getenv("SITE_BASE_URL", "https://bgtechlab.github.io/bgtech")
DEFAULT_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop"

PRODUCTS_JSON_PATH = os.path.join("data", "products.json")

# Category Configuration Dictionary
CATEGORY_CONFIG = OrderedDict([
    ("Mobiles",                {"title": "📱 Latest Smartphones",      "id": "mobiles"}),
    ("TV",                     {"title": "📺 Smart TVs & Displays",    "id": "tvs"}),
    ("Smart TV",               {"title": "📺 Smart TVs & Displays",    "id": "tvs"}),
    ("Audio",                  {"title": "🎧 Audio & Sound",           "id": "headphones"}),
    ("Headphones",             {"title": "🎧 Audio & Sound",           "id": "headphones"}),
    ("Laptops",                {"title": "💻 Laptops",                 "id": "laptops"}),
    ("Printers",               {"title": "🖨️ Printers",                "id": "printers"}),
    ("Smartwatches",           {"title": "⌚ Smartwatches",            "id": "smartwatches"}),
    ("Gadgets",                {"title": "⚙️ Gadgets & Accessories",   "id": "gadgets"}),
    
    # ---- Naye Categories ----
    ("Kitchen",                {"title": "🍳 Kitchen",                 "id": "kitchen"}),
    ("Home & Kitchen",         {"title": "🏠 Home & Kitchen",          "id": "home-kitchen"}),
    ("Accessories",            {"title": "👜 Accessories",             "id": "accessories"}),
    ("For Women",              {"title": "👩 For Women",               "id": "for-women"}),
    ("Women Western",          {"title": "👗 Women Western",           "id": "women-western"}),
    ("Kurti, Saree & Lehenga", {"title": "🥻 Kurti, Saree & Lehenga",  "id": "ethnic-wear"}),
    ("Lingerie",               {"title": "👙 Lingerie",                "id": "lingerie"}),
    ("For Men",                {"title": "👨 For Men",                 "id": "for-men"}),
    ("Men",                    {"title": "👨 Men",                     "id": "men"}),
    ("Travel",                 {"title": "✈️ Travel",                  "id": "travel"}),
    ("Car & Motorbike",        {"title": "🚗 Car & Motorbike",         "id": "car-motorbike"}),
    ("Books",                  {"title": "📚 Books",                   "id": "books"}),
])

client = Client()  # g4f fallback client

if GEMINI_SDK_AVAILABLE and GEMINI_API_KEY:
    if not GENAI_NEW_SDK:
        genai.configure(api_key=GEMINI_API_KEY)
elif not GEMINI_SDK_AVAILABLE:
    logging.warning("⚠️ Gemini SDK installed nahi hai. Run: pip install google-genai")
elif not GEMINI_API_KEY:
    logging.warning("⚠️ GEMINI_API_KEY .env mein nahi mili — Gemini skip hoga, g4f fallback use hoga.")

# ================= 2. ADVANCED SCRAPER & HELPERS =================
def unshorten_and_resolve_url(url, session):
    """
    Traces short links (fktr.in, amzn.to, earnkaro, linkredirect.in, etc.)
    and unpacks hidden target query parameters (dl=, url=) until the real store page is reached.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    }
    session.headers.update(headers)

    current_url = url.strip()
    for _ in range(6):
        # 1. Query parameter dl= ya url= decode karo
        if "dl=" in current_url or "url=" in current_url:
            parsed = urllib.parse.urlparse(current_url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "dl" in qs and qs["dl"][0]:
                current_url = urllib.parse.unquote(qs["dl"][0])
            elif "url" in qs and qs["url"][0]:
                current_url = urllib.parse.unquote(qs["url"][0])

        if any(d in current_url for d in ["flipkart.com", "amazon.in", "amazon.com"]):
            if not any(wrap in current_url for wrap in ["linkredirect.in", "fktr.in", "earnkaro"]):
                break

        try:
            logging.info(f"🔍 Tracing redirect for: {current_url[:60]}...")
            res = session.get(current_url, allow_redirects=True, timeout=15)
            current_url = res.url

            if "dl=" in current_url or "url=" in current_url:
                continue

            soup = BeautifulSoup(res.content, "html.parser")
            
            meta_refresh = soup.find("meta", attrs={"http-equiv": re.compile(r"refresh", re.I)})
            if meta_refresh and meta_refresh.get("content"):
                match = re.search(r"url=['\"]?(.*?)['\"]?$", meta_refresh.get("content"), re.I)
                if match:
                    current_url = urllib.parse.unquote(match.group(1).strip())
                    continue

            target_match = re.search(r"['\"](https://(?:www\.|dl\.)?(?:flipkart\.com|amazon\.in|amazon\.com)[^'\"]+)['\"]", res.text)
            if target_match:
                current_url = target_match.group(1).strip()
                break

        except Exception as e:
            logging.warning(f"⚠️ Redirect resolution failed: {e}")
            break

    asin_match = re.search(r'([B0-9][A-Z0-9]{9})', current_url, re.IGNORECASE)
    if "amazon" in current_url and asin_match and "/dp/" not in current_url:
        return f"https://www.amazon.in/dp/{asin_match.group(1)}"

    return current_url

def clean_product_name(raw_title):
    if not raw_title:
        return raw_title

    name = raw_title.strip()

    # Flipkart artifact jaise (P...more) ya (...more)
    name = re.sub(r"\s*\(?\s*p?\.\.\.more\)?", "", name, flags=re.IGNORECASE)

    # Amazon-style suffix: " : Amazon.in : Electronics" ya " - Amazon.in"
    name = re.sub(r"\s*[:\-]\s*Amazon\..*$", "", name, flags=re.IGNORECASE)

    # Flipkart-style suffix: " Online From Flipkart.com", " Online At Best Price..."
    name = re.sub(r"\s+Online\s+(from|at)\s+.*$", "", name, flags=re.IGNORECASE)

    # Leading "Buy " word hatao
    name = re.sub(r"^\s*Buy\s+", "", name, flags=re.IGNORECASE)

    # Comma ya pipe ke baad ka extra detail hatao
    name = re.split(r"[|,]", name)[0].strip()

    # Word-boundary par trim karo SEO title ke liye
    max_len = 70
    if len(name) > max_len:
        trimmed = name[:max_len].rsplit(" ", 1)[0].strip()
        name = trimmed if trimmed else name[:max_len].strip()

    return name.strip()

def clean_image_url(src):
    if not src:
        return ""
    clean_src = re.sub(r"\._SX\d+_|\._SY\d+_|\._AC_UL\d+_|\._UX\d+_|\._.*_.", ".", src)
    clean_src = re.sub(r"/image/\d+/\d+/", "/image/832/832/", clean_src)
    return clean_src

def detect_product_category(title_text):
    """Title aur keywords ke hisaab se sahi category detect karta hai."""
    t = title_text.lower()

    # Tech & Electronics
    if any(w in t for w in ["laptop", "macbook", "notebook", "thinkpad"]):
        return "Laptops"
    elif any(w in t for w in ["phone", "mobile", "5g", "smartphone", "iphone", "samsung galaxy", "redmi", "realme", "oneplus"]):
        return "Mobiles"
    elif any(w in t for w in ["smartwatch", "smart watch", "fitness band", "smart band"]):
        return "Smartwatches"
    elif any(w in t for w in ["earbuds", "headphone", "earphone", "airpods", "tws", "neckband", "headset"]):
        return "Headphones"
    elif any(w in t for w in ["soundbar", "speaker", "bluetooth speaker", "home theatre", "subwoofer", "audio"]):
        return "Audio"
    elif any(w in t for w in [" tv", "television", "smart tv", "led tv", "qled", "oled", "android tv"]):
        return "TV"
    elif any(w in t for w in ["printer", "ink cartridge", "toner"]):
        return "Printers"

    # Books
    elif any(w in t for w in ["paperback", "hardcover", "novel", "book", "edition", "author", "guidebook"]):
        return "Books"

    # Women Fashion & Ethnic Wear
    elif any(w in t for w in ["saree", "kurti", "kurta set", "lehenga", "anarkali", "dupatta", "ethnic"]):
        return "Kurti, Saree & Lehenga"
    elif any(w in t for w in ["bra ", "panty", "lingerie", "nightwear", "nightdress", "sleepwear", "bikini"]):
        return "Lingerie"
    elif any(w in t for w in ["dress", "gown", "top for women", "jeans for women", "skirt", "jumpsuit"]):
        return "Women Western"
    elif any(w in t for w in ["women", "ladies", "girl"]):
        return "For Women"

    # Men Fashion
    elif any(w in t for w in ["men t-shirt", "men shirt", "men jeans", "men trousers", "men blazer", "kurta for men"]):
        return "For Men"
    elif any(w in t for w in [" men", "man", "gents"]):
        return "Men"

    # Kitchen & Home
    elif any(w in t for w in ["mixer grinder", "blender", "cooker", "frypan", "kettle", "gas stove", "chimney", "toaster", "air fryer", "cookware"]):
        return "Kitchen"
    elif any(w in t for w in ["bedsheet", "curtain", "vacuum cleaner", "mop", "home decor", "cushion", "pillow", "mattress", "water purifier"]):
        return "Home & Kitchen"

    # Automotive & Travel
    elif any(w in t for w in ["car ", "motorbike", "helmet", "bike cover", "car vacuum", "dash cam", "car charger", "tyre inflator"]):
        return "Car & Motorbike"
    elif any(w in t for w in ["trolley bag", "luggage", "suitcase", "travel backpack", "duffle bag", "travel organizer"]):
        return "Travel"

    # Accessories & General Gadgets
    elif any(w in t for w in ["handbag", "wallet", "belt", "sunglasses", "backpack", "purse"]):
        return "Accessories"
    elif any(w in t for w in ["charger", "power bank", "cable", "mouse", "keyboard", "usb", "adapter", "stand"]):
        return "Gadgets"

    return "Gadgets"

def scrape_product_details(url):
    logging.info(f"🔄 Scraping Product: {url[:60]}...")
    data = {
        "title": "",
        "price": "Check Best Price",
        "rating": "4.2 out of 5 stars",
        "images": [],
        "bullets": "",
        "category": "Gadgets"
    }

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    })

    res_url = unshorten_and_resolve_url(url, session)

    try:
        res = session.get(res_url, allow_redirects=True, timeout=20)
        soup = BeautifulSoup(res.content, "html.parser")

        # 1. Title
        title_elem = (
            soup.find("meta", {"property": "og:title"})
            or soup.find("h1")
            or soup.find("span", {"id": "productTitle"}) 
            or soup.find("span", {"class": "VU-Tz5"})
            or soup.find("meta", {"name": "twitter:title"})
        )
        if title_elem:
            raw_title = title_elem.get("content") if title_elem.name == "meta" else title_elem.get_text()
            clean_title = raw_title.strip().replace("\n", " ")
            clean_title = re.sub(r"\s*:\s*Amazon\..*$", "", clean_title, flags=re.IGNORECASE)
            data["title"] = clean_title

        # Title URL Slug fallback if blocked
        if (not data["title"] or data["title"] in ["Flipkart store 2", "Amazon.in", "Online Shopping"]) and "/p/" in res_url:
            slug_match = re.search(r"flipkart\.com/([^/]+)/p/", res_url)
            if slug_match:
                slug_words = slug_match.group(1).replace("-", " ").title()
                data["title"] = slug_words

        # 2. Images
        images = []
        og_img = soup.find("meta", {"property": "og:image"})
        if og_img and og_img.get("content"):
            img_c = clean_image_url(og_img.get("content"))
            if img_c and "ckassets" not in img_c:
                images.append(img_c)

        script_imgs = re.findall(r'"hiRes":"(https://m.media-amazon.com/images/I/[^"]+)"', res.text)
        if not script_imgs:
            script_imgs = re.findall(r'"large":"(https://m.media-amazon.com/images/I/[^"]+)"', res.text)
            
        for img_url in script_imgs:
            cleaned = clean_image_url(img_url)
            if cleaned and cleaned not in images:
                images.append(cleaned)

        fk_imgs = soup.find_all("img", {"class": ["_0D5CY0", "q6D3P8", "_2r_T1I", "_396cs4", "v1zwn21u"]})
        for fk in fk_imgs:
            src = fk.get("src", "")
            cleaned = clean_image_url(src)
            if cleaned and cleaned not in images and "placeholder" not in cleaned and "ckassets" not in cleaned:
                images.append(cleaned)

        if len(images) < 2:
            all_imgs = soup.find_all("img")
            for i in all_imgs:
                src = i.get("src", "")
                if ("media-amazon.com/images/I/" in src or "flixcart.com/image/" in src) and not any(x in src for x in ["icon", "logo", "sprite", "GIF", "ckassets"]):
                    cleaned = clean_image_url(src)
                    if cleaned and cleaned not in images:
                        images.append(cleaned)

        valid_images = [img for img in images if img.startswith("http")][:5]
        if not valid_images:
            valid_images = [DEFAULT_FALLBACK_IMAGE]

        data["images"] = valid_images

        # 3. Price
        price_selectors = [
            ("span", {"class": "a-price-whole"}),
            ("div", {"class": "Nx9bqj CxhGGd"}),
            ("div", {"class": "Nx9bqj"}),
            ("div", {"class": "_30jeq3"}),
            ("div", {"class": "_30jeq3 _16Jk6d"}),
            ("div", {"class": "_25bWKC"}),
            ("div", {"class": "HLT-1-"}),
        ]
        for tag, attrs in price_selectors:
            price_elem = soup.find(tag, attrs)
            if price_elem:
                clean_price = re.sub(r"[^\d]", "", price_elem.get_text())
                if clean_price and len(clean_price) >= 2:
                    try:
                        data["price"] = f"₹{int(clean_price):,}"
                    except ValueError:
                        data["price"] = f"₹{clean_price}"
                    break

        # Fallback 1: meta price
        if data["price"] == "Check Best Price":
            meta_price = soup.find("meta", {"itemprop": "price"}) or soup.find("meta", {"property": "product:price:amount"})
            if meta_price and meta_price.get("content"):
                clean_price = re.sub(r"[^\d]", "", meta_price.get("content"))
                if clean_price and len(clean_price) >= 2:
                    try:
                        data["price"] = f"₹{int(clean_price):,}"
                    except ValueError:
                        data["price"] = f"₹{clean_price}"

        # Fallback 2: Regex scanning
        if data["price"] == "Check Best Price":
            price_matches = re.findall(r"₹\s?([0-9]{1,3}(?:,[0-9]{2,3})+|[0-9]{2,6})", res.text)
            for pm in price_matches:
                clean_num = re.sub(r"[^\d]", "", pm)
                if clean_num and 50 <= int(clean_num) <= 1000000:
                    data["price"] = f"₹{int(clean_num):,}"
                    break

        # 4. Bullets
        bullet_elems = soup.find(id="feature-bullets")
        if bullet_elems:
            bullets_list = [li.get_text().strip() for li in bullet_elems.find_all("li") if li.get_text().strip()]
            data["bullets"] = " | ".join(bullets_list[:5])

    except Exception as e:
        logging.error(f"⚠️ Scraping Error: {e}")

    if not data["title"]:
        data["title"] = "Best Deal Online"

    # Category Detection
    data["category"] = detect_product_category(data["title"])

    return data

# ================= 3. AI CONTENT GENERATOR =================
def get_ai_response(prompt):
    if GEMINI_SDK_AVAILABLE and GEMINI_API_KEY:
        try:
            if GENAI_NEW_SDK:
                client_genai = google_genai.Client(api_key=GEMINI_API_KEY)
                res = client_genai.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
                text = getattr(res, "text", "") or ""
            else:
                model = genai.GenerativeModel(GEMINI_MODEL)
                res = model.generate_content(prompt)
                text = getattr(res, "text", "") or ""

            if text and len(text.strip()) > 20:
                return text
            logging.warning("⚠️ Gemini se response chhota mila, g4f fallback try kar rahe hain.")
        except Exception as e:
            logging.warning(f"⚠️ Gemini call error ({e}), g4f fallback try kar rahe hain.")

    models = ["gpt-4o-mini", "gpt-3.5-turbo"]
    for model_name in models:
        try:
            res = client.chat.completions.create(
                model=model_name, 
                messages=[{"role": "user", "content": prompt}]
            )
            content = res.choices[0].message.content
            if content and len(content.strip()) > 20:
                return content
        except Exception:
            continue
    return ""

CATEGORY_FALLBACKS = {
    "Laptops": {
        "specs": {
            "Display": "Full HD / High Resolution Display",
            "Performance": "Latest Gen Processor & High Speed RAM",
            "Storage": "SSD Storage for Fast Boot & App Load",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "laptop",
    },
    "Mobiles": {
        "specs": {
            "Display": "High Refresh Rate AMOLED/LCD Display",
            "Performance": "Latest Gen Processor & Fast RAM",
            "Camera": "Multi-Lens Rear Camera Setup",
            "Battery": "Large Battery with Fast Charging",
        },
        "noun": "smartphone",
    },
    "Headphones": {
        "specs": {
            "Driver": "Dynamic Drivers with Crisp Audio",
            "Battery Life": "Long Playback Time on Single Charge",
            "Connectivity": "Bluetooth with Low Latency",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "earphones",
    },
    "Audio": {
        "specs": {
            "Output Power": "Powerful Audio Output with Deep Bass",
            "Connectivity": "Bluetooth, AUX, USB & Optical",
            "Sound Modes": "Multiple Equalizer & Bass Modes",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "sound system",
    },
    "TV": {
        "specs": {
            "Display": "4K / Full HD Panel with Wide Viewing Angle",
            "Smart OS": "Built-in Popular Streaming Apps",
            "Audio": "Built-in Speakers with Surround Sound",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "TV",
    },
    "Smartwatches": {
        "specs": {
            "Display": "Vibrant HD Touch Screen Display",
            "Health Tracking": "Heart Rate, SpO2 & Activity Tracker",
            "Battery Life": "Multi-day Battery Backup",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "smartwatch",
    },
    "Printers": {
        "specs": {
            "Print Type": "High Quality Printing Output",
            "Functions": "Print, Scan & Copy Support",
            "Connectivity": "USB & Wireless Connectivity",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "printer",
    },
    "Kitchen": {
        "specs": {
            "Material": "Food Grade Durable Material",
            "Efficiency": "Energy & Time Efficient Operation",
            "Safety": "Overload & Heat Protection",
            "Warranty": "Brand Warranty Included",
        },
        "noun": "kitchen appliance",
    },
    "Home & Kitchen": {
        "specs": {
            "Quality": "Premium & Durable Build Quality",
            "Utility": "Designed for Daily Home Convenience",
            "Maintenance": "Easy to Clean & Maintain",
            "Warranty": "Standard Brand Warranty",
        },
        "noun": "home utility product",
    },
    "Accessories": {
        "specs": {
            "Material": "Premium Quality Long Lasting Material",
            "Design": "Modern, Sleek & Ergonomic Design",
            "Usability": "Daily Essential Companion",
            "Durability": "Wear & Tear Resistant",
        },
        "noun": "accessory",
    },
    "Women Western": {
        "specs": {
            "Fabric": "Soft, Breathable & Comfortable Fabric",
            "Fit Type": "Modern Regular / Slim Fit",
            "Occasion": "Casual, Office & Party Wear",
            "Care": "Easy Machine / Hand Wash",
        },
        "noun": "western outfit",
    },
    "Kurti, Saree & Lehenga": {
        "specs": {
            "Fabric": "Rich Traditional Quality Fabric",
            "Work/Pattern": "Elegant Print & Embroidery Work",
            "Occasion": "Festive, Wedding & Party Wear",
            "Care": "Dry Clean / Gentle Wash Recommended",
        },
        "noun": "ethnic wear",
    },
    "Lingerie": {
        "specs": {
            "Fabric": "Ultra Soft & Skin-Friendly Fabric",
            "Comfort": "All-Day Breathable Comfort",
            "Support": "Optimal Fit and Shape",
            "Care": "Gentle Hand Wash",
        },
        "noun": "innerwear",
    },
    "For Women": {
        "specs": {
            "Quality": "High Quality Craftsmanship",
            "Design": "Trendy & Modern Aesthetic",
            "Comfort": "Designed for Maximum Comfort",
            "Versatility": "Suitable for Multiple Occasions",
        },
        "noun": "women's product",
    },
    "For Men": {
        "specs": {
            "Quality": "Durable & Premium Material",
            "Style": "Classic & Contemporary Look",
            "Comfort": "Easy All-Day Wear",
            "Fit": "Perfect Everyday Fit",
        },
        "noun": "men's product",
    },
    "Men": {
        "specs": {
            "Quality": "Premium Quality Finish",
            "Style": "Modern & Smart Fit",
            "Comfort": "Breathable & Comfortable",
            "Care": "Easy Care & Washable",
        },
        "noun": "men's item",
    },
    "Travel": {
        "specs": {
            "Material": "Durable & Scratch Resistant Material",
            "Compartments": "Spacious Multi-Compartment Storage",
            "Portability": "Lightweight & Smooth Mobility",
            "Security": "Sturdy Zippers & Lock Support",
        },
        "noun": "travel gear",
    },
    "Car & Motorbike": {
        "specs": {
            "Compatibility": "Universal / Vehicle Specific Fit",
            "Build": "Heavy Duty Weather Resistant Material",
            "Installation": "Quick & Easy Setup",
            "Safety": "Certified Safe for Vehicles",
        },
        "noun": "auto accessory",
    },
    "Books": {
        "specs": {
            "Format": "Paperback / Hardcover",
            "Language": "English / Hindi",
            "Genre": "Informative & Engaging Content",
            "Print Quality": "Clear Typography & Quality Paper",
        },
        "noun": "book",
    },
    "Gadgets": {
        "specs": {
            "Build Quality": "Durable, Premium Build",
            "Performance": "Reliable Everyday Performance",
            "Connectivity": "Multiple Connectivity Options",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "gadget",
    },
}

def build_generic_fallback(short_name, product_data):
    category = product_data.get("category", "Gadgets")
    fallback = CATEGORY_FALLBACKS.get(category, CATEGORY_FALLBACKS["Gadgets"])
    noun = fallback["noun"]

    price = product_data.get("price", "Check Best Price")
    price_phrase = price if price != "Check Best Price" else "iske price range"

    return {
        "pros": [
            f"Solid build and value for money {noun}",
            "Reliable performance & quality finish",
            "Stylish, modern and practical design",
            "Easy to use in day-to-day life",
        ],
        "cons": [
            "Stock limited during sale periods",
            "Delivery might take extra time in remote areas",
        ],
        "specs": fallback["specs"],
        "review_html": (
            f"<h3>Overview</h3><p>Agar aap {price_phrase} mein ek behtareen {noun} "
            f"dhoondh rahe hain, toh {short_name} ek strong option hai. Isme aapko "
            f"quality aur value for money ka accha balance milta hai.</p>"
            f"<h3>Key Features & Performance</h3><p>Is {noun} mein practical features "
            f"aur high durability milti hai jo daily use ke liye kaafi behtar hai.</p>"
            f"<h3>Final Verdict</h3><p>Apne price segment ke hisaab se ye {noun} ek "
            f"worth-buying deal sabit hoti hai.</p>"
        ),
    }

def generate_product_json_content(short_name, product_data):
    category = product_data.get("category", "Gadgets")
    prompt = f"""
    Act as a professional Indian product reviewer & SEO content writer. 
    Write a detailed, engaging, and SEO-optimized review in natural Hinglish for:
    
    Product Name: {short_name}
    Category: {category}
    Full Title: {product_data['title']}
    Price: {product_data['price']}
    Features: {product_data['bullets']}

    REQUIREMENTS:
    1. 'review_html' MUST be at least 350-450 words with rich headings (<h3>), <p>, <ul>, <li>, <strong> tags.
    2. Write in conversational Hinglish style relevant to {category} (e.g. build quality, design, value for money, performance).
    3. Breakdown specs into 4 relevant key categories for {category}.
    4. Provide 4 solid Pros and 2 realistic Cons.

    OUTPUT ONLY VALID JSON (NO MARKDOWN CODE WRAPPERS):
    {{
        "pros": ["Point 1", "Point 2", "Point 3", "Point 4"],
        "cons": ["Point 1", "Point 2"],
        "specs": {{
            "Key Feature 1": "Details",
            "Key Feature 2": "Details",
            "Key Feature 3": "Details",
            "Key Feature 4": "Details"
        }},
        "review_html": "<h3>Overview & First Impressions</h3><p>Analysis...</p><h3>Key Features & Usage Experience</h3><p>Details...</p><h3>Value for Money & Verdict</h3><p>Verdict...</p>"
    }}
    """
    raw_ai = get_ai_response(prompt)

    if not raw_ai:
        logging.warning("⚠️ AI se response nahi mila — category fallback use ho raha hai.")
        return build_generic_fallback(short_name, product_data)

    json_match = re.search(r"\{.*\}", raw_ai, re.DOTALL)
    clean_json_str = json_match.group(0) if json_match else ""

    try:
        parsed = json.loads(clean_json_str)
        if not parsed.get("review_html") or not parsed.get("specs"):
            raise ValueError("Incomplete AI JSON")
        return parsed
    except Exception as e:
        logging.error(f"⚠️ Failed to parse AI JSON: {e}")
        return build_generic_fallback(short_name, product_data)

# ================= 4. JSON DATA MANAGER =================
def save_to_products_json(product_entry):
    os.makedirs("data", exist_ok=True)
    products = []
    
    if os.path.exists(PRODUCTS_JSON_PATH):
        try:
            with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception:
            products = []

    existing_index = next((i for i, p in enumerate(products) if p["id"] == product_entry["id"]), None)
    if existing_index is not None:
        products[existing_index] = product_entry
    else:
        products.insert(0, product_entry)

    with open(PRODUCTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
        
    logging.info(f"✅ Product saved to {PRODUCTS_JSON_PATH}")

# ================= 5. MAIN PROCESS =================
async def process_and_publish(buy_url):
    product = scrape_product_details(buy_url)
    if not product or not product.get("title"):
        logging.error("❌ Product scraping failed.")
        return

    short_name = clean_product_name(product['title'])
    slug = re.sub(r'[^a-z0-9]+', '-', short_name.lower()).strip('-')

    ai_data = generate_product_json_content(short_name, product)

    page_url = f"{SITE_BASE_URL}/products/{slug}/"

    main_image = product["images"][0] if product.get("images") else DEFAULT_FALLBACK_IMAGE

    current_year = datetime.now(timezone.utc).year

    product_entry = {
        "id": slug,
        "title": f"{short_name} Review ({current_year})",
        "short_name": short_name,
        "category": product["category"],
        "price": product["price"],
        "rating": product["rating"],
        "image": main_image,
        "images": product["images"],
        "buy_url": buy_url,
        "pros": ai_data.get("pros", []),
        "cons": ai_data.get("cons", []),
        "specs": ai_data.get("specs", {}),
        "review_html": ai_data.get("review_html", ""),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }

    # 1. Save JSON
    save_to_products_json(product_entry)

    # 2. Build HTML Pages Automatically
    if os.path.exists("build.py"):
        try:
            logging.info("🔨 Generating Static HTML Pages (Running build.py)...")
            subprocess.run(["python", "build.py"], check=True)
            logging.info("✅ Static Pages Built!")
        except Exception as e:
            logging.error(f"⚠️ build.py execution failed: {e}")

    # 3. AUTO-PUSH TO GITHUB (WITH REBASE PULL)
    try:
        logging.info("🚀 Pushing changes to GitHub automatically...")
        git_executable = r'"C:\Program Files\Git\cmd\git.exe"' if os.path.exists(r"C:\Program Files\Git\cmd\git.exe") else "git"

        subprocess.run(f"{git_executable} add .", shell=True, check=True)
        subprocess.run(f'{git_executable} commit -m "Auto-add product: {short_name}"', shell=True, check=False)

        pull_result = subprocess.run(f"{git_executable} pull origin main --rebase", shell=True)
        if pull_result.returncode != 0:
            logging.warning("⚠️ git pull --rebase mein conflict/issue aaya — manually check karein.")

        subprocess.run(f"{git_executable} push origin main", shell=True, check=True)
        logging.info("✅ GitHub Push Successful!")
    except Exception as e:
        logging.error(f"⚠️ Auto Git Push Failed: {e}")

    # 4. Telegram Post
    tg_caption = (
        f"🔥 <b>New Review Alert!</b>\n\n"
        f"📦 <b>{short_name}</b>\n"
        f"🏷️ <b>Category:</b> {product['category']}\n"
        f"⭐️ <b>Rating:</b> {product['rating']}\n"
        f"💰 <b>Price:</b> {product['price']}\n\n"
        f"📖 <b>Read Review:</b>\n{page_url}\n\n"
        f"🛒 <b>Buy on Store:</b>\n{buy_url}"
    )
    try:
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            async with Bot(token=TELEGRAM_BOT_TOKEN) as tg_bot:
                await tg_bot.send_photo(
                    chat_id=TELEGRAM_CHAT_ID,
                    photo=main_image,
                    caption=tg_caption,
                    parse_mode="HTML"
                )
                logging.info("🎉 Telegram Notification Sent!")
    except Exception as e:
        logging.error(f"⚠️ Telegram Error: {e}")

    # 5. Make.com Webhook & Social Caption
    category_tag = product["category"].replace(" ", "").replace("&", "")
    social_prompt = f"""
    Write an attractive social media caption for Instagram, Facebook & Pinterest for:
    Product: {short_name}
    Category: {product['category']}
    Price: {product['price']}

    Keep it engaging with relevant emojis, clear value point, and hashtags.
    """
    
    social_caption = get_ai_response(social_prompt)
    if not social_caption or len(social_caption.strip()) < 20:
        clean_tag = re.sub(r'[^a-zA-Z0-9]', '', short_name)
        social_caption = f"Check out the best deal on {short_name}! ✨ Get yours at the best price of {product['price']} today!\n\n#BestDeals #{category_tag} #{clean_tag} #OnlineShopping"

    try:
        payload = {
            "title": short_name,
            "category": product["category"],
            "image_url": main_image,
            "caption": social_caption,
            "message": social_caption,
            "social_caption": social_caption,
            "deal_url": page_url,
            "amazon_url": buy_url,
            "price": product["price"]
        }
        if MAKE_WEBHOOK_URL:
            response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                logging.info(f"🎉 Make.com Webhook Triggered! Status: {response.status_code}")
            else:
                logging.warning(f"⚠️ Make.com Webhook returned status code {response.status_code}")
        else:
            logging.info("ℹ️ MAKE_WEBHOOK_URL .env mein missing hai — Webhook skip ho gaya.")
    except Exception as e:
        logging.error(f"⚠️ Webhook Error: {e}")

# ================= 6. EXECUTION =================
async def main():
    input_urls_raw = input("\nProduct Links (Space/Comma se alag karein): ").strip()
    urls_list = [
        url.strip()
        for url in re.split(r"[\s,]+", input_urls_raw)
        if url.strip().startswith("http")
    ]

    if not urls_list:
        logging.error("❌ Koi valid link nahi mila!")
        return

    for index, url in enumerate(urls_list):
        logging.info(f"\n--- [Processing Link {index+1}/{len(urls_list)}] ---")
        await process_and_publish(url)
        time.sleep(2)

    logging.info("\n✨ Process Complete! Sub kuch automatic GitHub par push ho chuka hai.")

if __name__ == "__main__":
    asyncio.run(main())