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

load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ================= 1. CONFIGURATION =================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8861999778:AAGWmE_Qg-mdWfUXsa9_ckPomrjKp3kpq4I")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@bglarenup")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL", "https://hook.eu1.make.com/i69enjkwljyuyt1tina0p6lsmh0oooi7")

SITE_BASE_URL = os.getenv("SITE_BASE_URL", "https://bgtechlab.github.io/bgtech")
DEFAULT_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop"

PRODUCTS_JSON_PATH = os.path.join("data", "products.json")

client = Client()

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

def scrape_product_details(url):
    logging.info(f"🔄 Scraping Product: {url[:60]}...")
    data = {
        "title": "",
        "price": "Check Best Price",
        "rating": "4.2 out of 5 stars",
        "image": "",
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

        img_elem = soup.find("img", {"id": "landingImage"}) or soup.find("meta", {"property": "og:image"})
        if img_elem:
            src = img_elem.get("content") if img_elem.name == "meta" else img_elem.get("src", "")
            src = re.sub(r"\._SX\d+_|\._SY\d+_|\._AC_UL\d+_|\._UX\d+_|\._.*_.", ".", src)
            data["image"] = src
        else:
            data["image"] = DEFAULT_FALLBACK_IMAGE

        price_elem = soup.find("span", {"class": "a-price-whole"}) or soup.find("div", {"class": "Nx9bqj CxhGGd"})
        if price_elem:
            clean_price = re.sub(r"[^\d]", "", price_elem.get_text())
            if clean_price:
                data["price"] = f"₹{clean_price}"

        bullet_elems = soup.find(id="feature-bullets")
        if bullet_elems:
            bullets_list = [li.get_text().strip() for li in bullet_elems.find_all("li") if li.get_text().strip()]
            data["bullets"] = " | ".join(bullets_list[:5])

    except Exception as e:
        logging.error(f"⚠️ Scraping Error: {e}")

    if not data["title"]:
        data["title"] = "Best Tech Gadget Deal"

    title_lower = data["title"].lower()
    if any(w in title_lower for w in ["laptop", "macbook"]):
        data["category"] = "Laptops"
    elif any(w in title_lower for w in ["phone", "mobile", "5g", "smartphone", "iphone", "samsung"]):
        data["category"] = "Mobiles"
    elif any(w in title_lower for w in ["watch", "smartwatch"]):
        data["category"] = "Smartwatches"
    elif any(w in title_lower for w in ["earbuds", "headphone", "earphone", "airpods"]):
        data["category"] = "Headphones"

    return data

# ================= 3. AI CONTENT GENERATOR =================
def get_ai_response(prompt):
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

def generate_product_json_content(short_name, product_data):
    prompt = f"""
    Act as a tech review expert. Create a detailed structured review for the product below in JSON format.
    
    PRODUCT DETAILS:
    - Name: {short_name}
    - Full Title: {product_data['title']}
    - Price: {product_data['price']}
    - Features: {product_data['bullets']}

    OUTPUT STRICTLY VALID JSON ONLY (NO Markdown, NO code blocks, NO standard text).
    
    Expected JSON Structure:
    {{
        "pros": ["Pro 1", "Pro 2", "Pro 3"],
        "cons": ["Con 1", "Con 2"],
        "specs": {{
            "Performance": "Brief details",
            "Display/Build": "Brief details",
            "Battery/Features": "Brief details"
        }},
        "review_html": "<h3>Overview</h3><p>Detailed review paragraph in Hinglish...</p><h3>Why Buy This?</h3><p>Verdict paragraph...</p>"
    }}
    """
    raw_ai = get_ai_response(prompt)
    clean_json_str = re.sub(r"^```json\s*|```$", "", raw_ai.strip(), flags=re.MULTILINE)
    
    try:
        return json.loads(clean_json_str)
    except Exception as e:
        logging.error(f"⚠️ Failed to parse AI JSON response: {e}")
        return {
            "pros": ["High Build Quality", "Great Performance"],
            "cons": ["Average Battery Life"],
            "specs": {"General": "Standard Specifications"},
            "review_html": f"<p>{short_name} offers great value for money in its segment.</p>"
        }

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

    clean_raw_title = re.sub(r"\s*:\s*Amazon\..*$", "", product['title'], flags=re.IGNORECASE)
    short_name = re.split(r'[,|(-]', clean_raw_title)[0].strip()
    slug = re.sub(r'[^a-z0-9]+', '-', short_name.lower()).strip('-')

    ai_data = generate_product_json_content(short_name, product)

    page_url = f"{SITE_BASE_URL}/products/{slug}/"

    product_entry = {
        "id": slug,
        "title": f"{short_name} Review (2026)",
        "short_name": short_name,
        "category": product["category"],
        "price": product["price"],
        "rating": product["rating"],
        "image": product["image"],
        "buy_url": buy_url,
        "pros": ai_data.get("pros", []),
        "cons": ai_data.get("cons", []),
        "specs": ai_data.get("specs", {}),
        "review_html": ai_data.get("review_html", ""),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }

    # 1. Save JSON
    save_to_products_json(product_entry)

    # 2. Build HTML Pages Automatically (If build.py exists)
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
                photo=product["image"],
                caption=tg_caption,
                parse_mode="HTML"
            )
            logging.info("🎉 Telegram Notification Sent!")
    except Exception as e:
        logging.error(f"⚠️ Telegram Error: {e}")

    # 5. Make.com Webhook & Social Caption
    # --- SOCIAL CAPTION GENERATOR ---
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

    # --- MAKE.COM WEBHOOK PAYLOAD ---
    try:
        final_image_url = product.get("image")
        if not final_image_url or not final_image_url.startswith("http"):
            final_image_url = DEFAULT_FALLBACK_IMAGE

        payload = {
            "title": short_name,
            "image_url": final_image_url,
            "caption": social_caption,          # Exact caption string
            "message": social_caption,          # FB Text Field Format
            "social_caption": social_caption,   # Alternative Mapping Key
            "deal_url": page_url,
            "amazon_url": buy_url,
            "price": product["price"]
        }
        response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=10)
        logging.info(f"🎉 Make.com Webhook Triggered! Status: {response.status_code}")
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