import asyncio
from datetime import datetime, timezone
import json
import logging
import os
import re
import subprocess
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from g4f.client import Client
import requests
from telegram import Bot

import warnings
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

# ================= 1. CONFIGURATION =================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SITE_BASE_URL = os.getenv("SITE_BASE_URL", "https://bgtechlab.github.io/bgtech")
DEFAULT_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop"

PRODUCTS_JSON_PATH = os.path.join("data", "products.json")

client = Client()  # g4f fallback client

if GEMINI_SDK_AVAILABLE and GEMINI_API_KEY:
    if not GENAI_NEW_SDK:
        genai.configure(api_key=GEMINI_API_KEY)
elif not GEMINI_SDK_AVAILABLE:
    logging.warning("⚠️ Gemini SDK installed nahi hai. Run: pip install google-genai")
elif not GEMINI_API_KEY:
    logging.warning("⚠️ GEMINI_API_KEY .env mein nahi mili — Gemini skip hoga, g4f fallback use hoga.")

# ================= 2. ADVANCED SCRAPER =================
def unshorten_amazon_url(url, session):
    if not any(domain in url for domain in ["amzn.to", "link.amazon", "earnkaro", "fktr.in", "linkredirect.in"]):
        return url

    try:
        logging.info(f"🔍 Tracing redirect for: {url}")
        res = session.get(url, allow_redirects=True, timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        
        meta_refresh = soup.find("meta", attrs={"http-equiv": re.compile(r"refresh", re.I)})
        if meta_refresh:
            content = meta_refresh.get("content", "")
            match = re.search(r"url=['\"]?(.*?)['\"]?$", content, re.I)
            if match:
                redirect_url = match.group(1).strip()
                res = session.get(redirect_url, allow_redirects=True, timeout=15)
                soup = BeautifulSoup(res.content, "html.parser")

        scripts = soup.find_all("script")
        for script in scripts:
            if script.string:
                target_match = re.search(r"['\"](https://(?:www\.|dl\.)?(?:flipkart\.com|amazon\.in)[^'\"]+)['\"]", script.string)
                if target_match:
                    redirect_url = target_match.group(1).strip()
                    res = session.get(redirect_url, allow_redirects=True, timeout=15)
                    soup = BeautifulSoup(res.content, "html.parser")
                    break

        if "amazon." in res.url or "flipkart." in res.url:
            return res.url

    except Exception as e:
        logging.warning(f"⚠️ Redirect resolution failed: {e}")

    asin_match = re.search(r'([B0-9][A-Z0-9]{9})', url, re.IGNORECASE)
    if asin_match:
        return f"https://www.amazon.in/dp/{asin_match.group(1)}"

    return url

def clean_product_name(raw_title):
    """
    Raw scraped title se saaf, SEO-friendly short product name banata hai.
    - "Buy " prefix hataata hai
    - "Online from Flipkart.com" / "Online at ..." jaisa junk suffix hataata hai
    - " : Amazon.in : ..." jaisa Amazon suffix hataata hai
    - Comma/pipe par split karta hai, LEKIN hyphen (-) par split NAHI karta,
      taaki "HT-S20R" jaise model numbers beech mein na kate
    - Zaroorat padne par word-boundary par hi lambaai limit karta hai
    """
    if not raw_title:
        return raw_title

    name = raw_title.strip()

    # Amazon-style suffix: " : Amazon.in : Electronics" ya " - Amazon.in"
    name = re.sub(r"\s*[:\-]\s*Amazon\..*$", "", name, flags=re.IGNORECASE)

    # Flipkart-style suffix: " Online From Flipkart.com", " Online At Best Price..."
    name = re.sub(r"\s+Online\s+(from|at)\s+.*$", "", name, flags=re.IGNORECASE)

    # Leading "Buy " word hatao
    name = re.sub(r"^\s*Buy\s+", "", name, flags=re.IGNORECASE)

    # Comma ya pipe ke baad ka extra detail hatao (hyphen ko chhoड़ do - model numbers ke liye)
    name = re.split(r"[|,]", name)[0].strip()

    # Agar phir bhi bahut lamba hai, word-boundary par trim karo (SEO title length ke liye)
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    })

    res_url = unshorten_amazon_url(url, session)

    try:
        res = session.get(res_url, allow_redirects=True, timeout=20)
        soup = BeautifulSoup(res.content, "html.parser")

        # 1. Title
        title_elem = (
            soup.find("span", {"id": "productTitle"}) 
            or soup.find("span", {"class": "VU-Tz5"}) 
            or soup.find("meta", {"property": "og:title"})
        )
        if title_elem:
            raw_title = title_elem.get("content") if title_elem.name == "meta" else title_elem.get_text()
            clean_title = raw_title.strip().replace("\n", " ")
            clean_title = re.sub(r"\s*:\s*Amazon\..*$", "", clean_title, flags=re.IGNORECASE)
            data["title"] = clean_title

        # 2. Images
        images = []
        og_img = soup.find("meta", {"property": "og:image"})
        if og_img and og_img.get("content"):
            images.append(clean_image_url(og_img.get("content")))

        script_imgs = re.findall(r'"hiRes":"(https://m.media-amazon.com/images/I/[^"]+)"', res.text)
        if not script_imgs:
            script_imgs = re.findall(r'"large":"(https://m.media-amazon.com/images/I/[^"]+)"', res.text)
            
        for img_url in script_imgs:
            cleaned = clean_image_url(img_url)
            if cleaned and cleaned not in images:
                images.append(cleaned)

        fk_imgs = soup.find_all("img", {"class": ["_0D5CY0", "q6D3P8", "_2r_T1I"]})
        for fk in fk_imgs:
            src = fk.get("src", "")
            cleaned = clean_image_url(src)
            if cleaned and cleaned not in images and "placeholder" not in cleaned:
                images.append(cleaned)

        if len(images) < 2:
            all_imgs = soup.find_all("img")
            for i in all_imgs:
                src = i.get("src", "")
                if ("media-amazon.com/images/I/" in src or "flixcart.com/image/" in src) and not any(x in src for x in ["icon", "logo", "sprite", "GIF"]):
                    cleaned = clean_image_url(src)
                    if cleaned and cleaned not in images:
                        images.append(cleaned)

        valid_images = [img for img in images if img.startswith("http")][:5]
        if not valid_images:
            valid_images = [DEFAULT_FALLBACK_IMAGE]

        data["images"] = valid_images

        # 3. Price
        price_selectors = [
            ("span", {"class": "a-price-whole"}),          # Amazon
            ("div", {"class": "Nx9bqj CxhGGd"}),            # Flipkart
            ("div", {"class": "Nx9bqj"}),                    # Flipkart
            ("div", {"class": "_30jeq3"}),                   # Flipkart
            ("div", {"class": "_30jeq3 _16Jk6d"}),           # Flipkart
            ("div", {"class": "_25bWKC"}),                   # Flipkart variant
            ("div", {"class": "HLT-1-"}),                    # Flipkart variant
        ]
        price_elem = None
        for tag, attrs in price_selectors:
            price_elem = soup.find(tag, attrs)
            if price_elem:
                clean_price = re.sub(r"[^\d]", "", price_elem.get_text())
                if clean_price and len(clean_price) >= 3:
                    try:
                        data["price"] = f"₹{int(clean_price):,}"
                    except ValueError:
                        data["price"] = f"₹{clean_price}"
                    break

        # Fallback 1: meta tag jisme price hota hai
        if data["price"] == "Check Best Price":
            meta_price = soup.find("meta", {"itemprop": "price"}) or soup.find("meta", {"property": "product:price:amount"})
            if meta_price and meta_price.get("content"):
                clean_price = re.sub(r"[^\d]", "", meta_price.get("content"))
                if clean_price and len(clean_price) >= 3:
                    try:
                        data["price"] = f"₹{int(clean_price):,}"
                    except ValueError:
                        data["price"] = f"₹{clean_price}"

        # Fallback 2: Regex scanning on page text for ₹ prices (e.g. ₹12,990)
        if data["price"] == "Check Best Price":
            price_matches = re.findall(r"₹\s?([0-9]{1,3}(?:,[0-9]{2,3})+|[0-9]{3,6})", res.text)
            for pm in price_matches:
                clean_num = re.sub(r"[^\d]", "", pm)
                if clean_num and 100 <= int(clean_num) <= 1000000:
                    data["price"] = f"₹{int(clean_num):,}"
                    break

        if data["price"] == "Check Best Price":
            logging.warning("⚠️ Price scrape fail hui — 'Check Best Price' placeholder use ho raha hai.")

        # 4. Bullets
        bullet_elems = soup.find(id="feature-bullets")
        if bullet_elems:
            bullets_list = [li.get_text().strip() for li in bullet_elems.find_all("li") if li.get_text().strip()]
            data["bullets"] = " | ".join(bullets_list[:5])

    except Exception as e:
        logging.error(f"⚠️ Scraping Error: {e}")

    if not data["title"]:
        data["title"] = "Best Tech Gadget Deal"

    title_lower = data["title"].lower()
    if any(w in title_lower for w in ["laptop", "macbook", "notebook"]):
        data["category"] = "Laptops"
    elif any(w in title_lower for w in ["phone", "mobile", "5g", "smartphone", "iphone", "samsung"]):
        data["category"] = "Mobiles"
    elif any(w in title_lower for w in ["watch", "smartwatch"]):
        data["category"] = "Smartwatches"
    elif any(w in title_lower for w in ["soundbar", "speaker", "bluetooth speaker"]):
        data["category"] = "Audio"
    elif any(w in title_lower for w in ["earbuds", "headphone", "earphone", "airpods", "tws"]):
        data["category"] = "Headphones"
    elif any(w in title_lower for w in [" tv", "television", "smart tv", "led tv"]):
        data["category"] = "TV"
    elif any(w in title_lower for w in ["printer"]):
        data["category"] = "Printers"

    return data

# ================= 3. AI CONTENT GENERATOR =================
def get_ai_response(prompt):
    # 1) Pehle Gemini try karo (zyada reliable, official API)
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
            logging.warning("⚠️ Gemini se khaali/chhota response mila, g4f fallback try kar rahe hain.")
        except Exception as e:
            logging.warning(f"⚠️ Gemini call fail hui ({e}), g4f fallback try kar rahe hain.")

    # 2) Gemini na ho ya fail ho jaye, to g4f (unofficial, less reliable) try karo
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

# Category-wise generic fallback content — jab AI response fail ho jaye tab bhi
# kam se kam category ke hisaab se relevant text/specs dikhein, "laptop" nahi.
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
            "Performance": "Latest Gen Processor & Ample RAM",
            "Camera": "Multi-Lens Rear Camera Setup",
            "Battery": "Large Battery with Fast Charging",
        },
        "noun": "smartphone",
    },
    "Headphones": {
        "specs": {
            "Driver": "Dynamic Driver for Balanced Sound",
            "Battery Life": "Long Playback on Single Charge",
            "Connectivity": "Bluetooth with Low Latency Mode",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "earphones",
    },
    "Audio": {
        "specs": {
            "Output Power": "High RMS Output for Loud, Clear Sound",
            "Connectivity": "Bluetooth, AUX & USB Support",
            "Sound Modes": "Multiple EQ / Bass Boost Modes",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "soundbar",
    },
    "TV": {
        "specs": {
            "Display": "4K / Full HD Panel with Wide Viewing Angle",
            "Smart Features": "Smart OS with Built-in Streaming Apps",
            "Audio": "Built-in Speakers with Dolby Support",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "TV",
    },
    "Smartwatches": {
        "specs": {
            "Display": "AMOLED / HD Touch Display",
            "Health Tracking": "Heart Rate, SpO2 & Sleep Monitoring",
            "Battery Life": "Multi-Day Battery Backup",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "smartwatch",
    },
    "Printers": {
        "specs": {
            "Print Type": "Inkjet / Laser Printing",
            "Functions": "Print, Scan & Copy",
            "Connectivity": "USB & Wireless Printing",
            "Warranty": "1 Year Brand Warranty",
        },
        "noun": "printer",
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
    """AI fail hone par category ke hisaab se generic (lekin sahi) content banata hai."""
    category = product_data.get("category", "Gadgets")
    fallback = CATEGORY_FALLBACKS.get(category, CATEGORY_FALLBACKS["Gadgets"])
    noun = fallback["noun"]

    # Price sirf tab dikhate hain jab actually scrape hui ho, warna generic wording.
    price = product_data.get("price", "Check Best Price")
    price_phrase = price if price != "Check Best Price" else "iske price range"

    return {
        "pros": [
            f"Solid build quality for a {noun} in this segment",
            "Reliable day-to-day performance",
            "Multiple connectivity options",
            "Sleek and modern design",
        ],
        "cons": [
            "Battery backup average under heavy load",
            "Stock limited during sale periods",
        ],
        "specs": fallback["specs"],
        "review_html": (
            f"<h3>Overview</h3><p>Agar aap {price_phrase} mein ek behtareen {noun} "
            f"dhoondh rahe hain, toh {short_name} ek strong contender hai. Isme aapko "
            f"build quality aur performance ka accha balance milta hai.</p>"
            f"<h3>Key Features & Performance</h3><p>Is {noun} mein aapko reliable "
            f"everyday performance milti hai jo daily use ke liye kaafi hai.</p>"
            f"<h3>Final Verdict</h3><p>Value for money ke hisaab se ye {noun} apne "
            f"price range mein ek solid buy hai.</p>"
        ),
    }


# Updated Section 3: AI JSON Cleaning Improvement
def generate_product_json_content(short_name, product_data):
    prompt = f"""
    Act as a professional Indian tech journalist & SEO content writer. 
    Write a detailed, engaging, and SEO-optimized product review in Hinglish for:
    
    Product Name: {short_name}
    Full Title: {product_data['title']}
    Price: {product_data['price']}
    Features: {product_data['bullets']}

    REQUIREMENTS:
    1. 'review_html' MUST be at least 400-500 words with rich headings (<h3>), <p>, <ul>, <li>, <strong> tags.
    2. Write in natural Hinglish style (e.g., "Kya aapko ye laptop kharidna chahiye?", "Performance aur Display Quality").
    3. Breakdown specs into key categories: Display, Performance, Audio, Connectivity, Verdict.
    4. Provide 4-5 solid Pros and 2-3 realistic Cons.

    OUTPUT ONLY VALID JSON (NO MARKDOWN WRAPPERS):
    {{
        "pros": ["Point 1", "Point 2", "Point 3", "Point 4"],
        "cons": ["Point 1", "Point 2"],
        "specs": {{
            "Display & Picture": "Detailed info",
            "Performance & Processor": "Detailed info",
            "Audio & Sound": "Detailed info",
            "Connectivity": "Ports & Wireless"
        }},
        "review_html": "<h3>Overview & First Impressions</h3><p>Detailed analysis...</p><h3>Display & Sound Performance</h3><p>Detailed breakdown...</p><h3>Value for Money & Final Verdict</h3><p>Final opinion...</p>"
    }}
    """
    raw_ai = get_ai_response(prompt)

    if not raw_ai:
        logging.warning("⚠️ AI se koi response nahi mila (g4f fail/blocked ho sakta hai) — category-wise fallback use ho raha hai.")
        return build_generic_fallback(short_name, product_data)

    # Extract JSON robustly using regex
    json_match = re.search(r"\{.*\}", raw_ai, re.DOTALL)
    clean_json_str = json_match.group(0) if json_match else ""

    try:
        parsed = json.loads(clean_json_str)
        # Sanity check: agar AI ne khaali/adhoora JSON diya to bhi fallback pe jao
        if not parsed.get("review_html") or not parsed.get("specs"):
            raise ValueError("AI JSON incomplete (missing review_html/specs)")
        return parsed
    except Exception as e:
        logging.error(f"⚠️ Failed to parse AI JSON response: {e}")
        logging.error(f"↳ Raw AI output (debug ke liye): {raw_ai[:500]}")
        return build_generic_fallback(short_name, product_data)

# Updated Section 5 Step 3: Git Auto Pull & Push
    # 3. AUTO-PUSH TO GITHUB (WITH REBASE PULL)
    try:
        logging.info("🚀 Pushing changes to GitHub automatically...")
        git_executable = r'"C:\Program Files\Git\cmd\git.exe"' if os.path.exists(r"C:\Program Files\Git\cmd\git.exe") else "git"
        
        # Pull remote changes first to prevent push rejection
        subprocess.run(f"{git_executable} pull origin main --rebase", shell=True, check=False)
        subprocess.run(f"{git_executable} add .", shell=True, check=True)
        subprocess.run(f'{git_executable} commit -m "Auto-add product: {short_name}"', shell=True, check=True)
        subprocess.run(f"{git_executable} push origin main", shell=True, check=True)
        logging.info("✅ GitHub Push Successful!")
    except Exception as e:
        logging.error(f"⚠️ Auto Git Push Failed: {e}")

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

    product_entry = {
        "id": slug,
        "title": f"{short_name} Review (2026)",
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

    # 3. AUTO-PUSH TO GITHUB
    try:
        logging.info("🚀 Pushing changes to GitHub automatically...")
        git_executable = r'"C:\Program Files\Git\cmd\git.exe"' if os.path.exists(r"C:\Program Files\Git\cmd\git.exe") else "git"
        
        subprocess.run(f"{git_executable} add .", shell=True, check=True)
        subprocess.run(f'{git_executable} commit -m "Auto-add product: {short_name}"', shell=True, check=True)
        subprocess.run(f"{git_executable} push origin main", shell=True, check=True)
        logging.info("✅ GitHub Push Successful!")
    except Exception as e:
        logging.error(f"⚠️ Auto Git Push Failed: {e}")

    # 4. Telegram Post
    tg_caption = f"🔥 <b>New Review Alert!</b>\n\n📱 <b>{short_name}</b>\n⭐️ <b>Rating:</b> {product['rating']}\n💰 <b>Price:</b> {product['price']}\n\n📖 <b>Read Review:</b>\n{page_url}\n\n🛒 <b>Buy on Store:</b>\n{buy_url}"
    try:
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
    social_prompt = f"""
    Write an attractive social media caption for Facebook, Pinterest, and Instagram for this product:
    Title: {short_name}
    Price: {product['price']}
    
    Format EXACTLY like this:
    Unleash the power of performance with the {short_name}! 🚀 With top-tier features and sleek design, it's built to keep up with your lifestyle. Get yours online at the best price today!
    
    #TechDeals #{short_name.replace(' ', '')} #BestDeals #Gadgets #AmazonDeals
    """
    
    social_caption = get_ai_response(social_prompt)
    if not social_caption or len(social_caption.strip()) < 20:
        social_caption = f"Unleash the power of performance with the {short_name}! 🚀 Get yours online at the best price {product['price']} today!\n\n#TechDeals #BestDeals #AmazonFinds"

    try:
        payload = {
            "title": short_name,
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
                logging.warning(f"⚠️ Make.com Webhook returned status code {response.status_code} (Please check MAKE_WEBHOOK_URL in .env)")
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