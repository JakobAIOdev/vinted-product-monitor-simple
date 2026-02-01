import os
import re
import json
import time
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException, Timeout
from bs4 import BeautifulSoup
from proxy_manager import ProxyManager

# --- CONFIGURATION & SETUP ---
load_dotenv()
SEEN_FILE = Path("seen_items.json")

# Load Environment Variables
URL = os.getenv("VINTED_URL")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "15"))

pm = ProxyManager("proxies.txt") 

# ANSI Colors for console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def validate_config():
    missing = []
    if not URL: missing.append("VINTED_URL")
    
    if missing:
        print(f"{Colors.RED}[ERROR] Missing required environment variables:{Colors.END}")
        for var in missing:
            print(f"   - {var}")
        print(f"\n{Colors.YELLOW}[TIP] Create a .env file based on .env.example{Colors.END}")
        return False
    return True

# --- HELPER FUNCTIONS ---

def load_seen_items():
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except: return set()
    return set()

def save_seen_items(seen_ids: set):
    recent_ids = sorted(list(seen_ids))[-1000:]
    SEEN_FILE.write_text(json.dumps(recent_ids), encoding="utf-8")

def send_discord_webhook(item):
    if not WEBHOOK_URL: return
    
    brand = item.get('brand') or "Unknown"
    size = item.get('size') or "N/A"
    price = item.get('price') or "N/A"
    status = item.get('status') or "N/A"
    title = item.get('title') or "No Title"
    
    image_url = item.get('image_url', '')
    if image_url.startswith('//'): image_url = "https:" + image_url
    
    thumbnail_obj = {"url": image_url} if (image_url and image_url.startswith('http')) else {}

    embed = {
        "title": f"{brand} - {size}",
        "url": item['url'],
        "color": 0x09B1BA,
        "description": title[:100], 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "thumbnail": thumbnail_obj,
        "fields": [
            {"name": "Price", "value": f"**{price}**", "inline": True},
            {"name": "Condition", "value": status, "inline": True},
            {"name": "Size", "value": size, "inline": True}
        ],
        "footer": {"text": f"Vinted Monitor • ID: {item['id']}"}
    }
    
    try:
        r = requests.post(WEBHOOK_URL, json={"username": "Vinted Sniper", "embeds": [embed]}, timeout=5)
        if r.status_code not in [200, 204]:
            print(f"{Colors.YELLOW}[WARN] Discord Error: {r.text}{Colors.END}")
    except Exception as e:
        print(f"{Colors.YELLOW}[WARN] Webhook Exception: {e}{Colors.END}")


# --- PARSING LOGIC ---

def parse_vinted_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    items = []
    overlay_links = soup.find_all('a', class_=lambda c: c and 'new-item-box__overlay' in c)

    for link in overlay_links:
        try:
            raw_href = link.get('href', '')
            full_url = raw_href if raw_href.startswith('http') else f"https://www.vinted.de{raw_href}"
            
            id_match = re.search(r'/items/([\d\.]+)-', raw_href)
            if not id_match: continue
            item_id = id_match.group(1)

            image_container = link.parent
            summary_div = image_container.find_next_sibling('div', class_='new-item-box__summary')
            
            brand, price, size, status = "Unknown", "?? €", "N/A", "N/A"

            if summary_div:
                brand_el = summary_div.find('p', {'data-testid': re.compile(r'--description-title$')})
                if brand_el: brand = brand_el.get_text(strip=True)
                
                price_el = summary_div.find('p', {'data-testid': re.compile(r'--price-text$')})
                if price_el: price = price_el.get_text(strip=True)
                
                subtitle_el = summary_div.find('p', {'data-testid': re.compile(r'--description-subtitle$')})
                if subtitle_el:
                    parts = subtitle_el.get_text(strip=True).split('·')
                    if len(parts) >= 1: size = parts[0].strip()
                    if len(parts) >= 2: status = parts[1].strip()

            image_url = ""
            img_tag = image_container.find('img')
            if img_tag:
                image_url = img_tag.get('data-src') or img_tag.get('src') or ""
            
            items.append({
                "id": item_id, "url": full_url, "title": link.get('title', 'No Title'),
                "brand": brand, "price": price, "size": size, "status": status, "image_url": image_url
            })
        except: continue
    return items


# --- INITIALIZATION & MAIN LOOP ---

def initial_scan(seen_items):
    print(f"{Colors.CYAN}[INIT] Syncing current listings...{Colors.END}")
    
    while True:
        proxies = pm.get_proxy()
        if not proxies:
            print(f"{Colors.RED}[ERR] No proxies in proxies.txt! Please add some.{Colors.END}")
            time.sleep(10)
            continue
            
        try:
            r = requests.get(URL, impersonate="chrome", proxies=proxies, timeout=20)
            if r.status_code == 200:
                items = parse_vinted_html(r.text)
                if not items:
                    print(f"{Colors.YELLOW}[WARN] Initial scan found 0 items. Retrying...{Colors.END}")
                    time.sleep(2)
                    continue

                new_count = 0
                for item in items:
                    if item['id'] not in seen_items:
                        seen_items.add(item['id'])
                        new_count += 1
                
                save_seen_items(seen_items)
                print(f"{Colors.GREEN}[OK] Synced {len(items)} items ({new_count} new). Monitor ready.{Colors.END}")
                return 
            else:
                print(f"{Colors.YELLOW}[WARN] Initial scan failed ({r.status_code}). Retrying...{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}[WARN] Initial scan error: {e}{Colors.END}")
        
        time.sleep(2)


def main():
    print(f"\n{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}║          VINTED MONITOR              ║{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}╚══════════════════════════════════════╝{Colors.END}\n")
    
    if not validate_config():
        return
    
    seen_items = load_seen_items()
    
    print(f"{Colors.BLUE}[CONFIG]{Colors.END}")
    print(f"   Polling Interval: {POLL_SECONDS}s")
    print(f"   Discord Webhook:  {Colors.GREEN + 'Enabled' + Colors.END if WEBHOOK_URL else Colors.RED + 'Disabled' + Colors.END}")
    print(f"   Known Items:      {len(seen_items)}")
    print(f"   Search URL:       {URL[:50]}...\n")
    
    if WEBHOOK_URL:
        try: requests.post(WEBHOOK_URL, json={"content": "**Monitor Online**"}) 
        except: pass

    initial_scan(seen_items)
    
    while True:
        proxies = pm.get_proxy()
        if not proxies:
            print(f"{Colors.RED}[ERR] No proxies loaded! Check proxies.txt{Colors.END}")
            time.sleep(10)
            continue
        
        try:
            r = requests.get(URL, impersonate="chrome", proxies=proxies, timeout=20)
            
            if r.status_code == 200:
                current_items = parse_vinted_html(r.text)
                
                if not current_items:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"{Colors.YELLOW}[{timestamp}] Parser returned 0 items{Colors.END}")
                    time.sleep(POLL_SECONDS)
                    continue

                new_items_found = []
                for item in current_items:
                    if item['id'] in seen_items:
                        break
                    new_items_found.append(item)

                if new_items_found:
                    print(f"{Colors.GREEN}{Colors.BOLD}[NEW] {len(new_items_found)} DROP(S) FOUND!{Colors.END}")
                    for item in new_items_found:
                        print(f"{Colors.GREEN}   > {item['brand']} | {item['price']} | {item['size']}{Colors.END}")
                        send_discord_webhook(item)
                        seen_items.add(item['id'])
                        time.sleep(0.5)
                    
                    save_seen_items(seen_items)
                else:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"{Colors.BLUE}[{timestamp}]{Colors.END} No new drops (Scanned: {len(current_items)} items)")

            elif r.status_code in [401, 403, 429]:
                print(f"{Colors.YELLOW}[BLOCKED] Status {r.status_code} - Rotating proxy...{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}[ERROR] {e}{Colors.END}")
            
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
