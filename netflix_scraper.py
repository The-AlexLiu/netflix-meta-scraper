import os
import time
import csv
import re
import requests
from playwright.sync_api import sync_playwright

# Configuration
URL = "https://about.netflix.com/zh_cn/new-to-watch"
OUTPUT_DIR = "images"
CSV_FILE = "netflix_records.csv"
TARGET_WIDTH = 450
HEADLESS = False # Hover often works better in non-headless or with specific UA

def download_image(url, filename):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(url, stream=True, headers=headers, timeout=15)
        if res.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in res.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def get_high_res_url(url):
    if not url: return None
    if '?' in url:
        base, params = url.split('?', 1)
        new_params = [p for p in params.split('&') if not (p.startswith('w=') or p.startswith('h='))]
        new_params.append(f"w={TARGET_WIDTH}")
        return f"{base}?{'&'.join(new_params)}"
    return f"{url}?w={TARGET_WIDTH}"

def get_description(browser_context, detail_url):
    if not detail_url or "netflix.com" not in detail_url:
        return "N/A"
    
    page = browser_context.new_page()
    try:
        page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        selectors = [
            'div[data-uia="video-title-synopsis"]',
            'div[data-uia="title-info-synopsis"]',
            'div[data-uia="video-description"]',
            '.p-b-1.p-t-1',
            '.synopsis',
            'meta[name="description"]'
        ]
        
        for selector in selectors:
            if selector.startswith("meta"):
                element = page.query_selector(selector)
                if element:
                    content = element.get_attribute("content")
                    if content: return content.strip()
            else:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text()
                    if text: return text.strip()
                    
        return "Description not found."
    except Exception as e:
        return f"Error: {str(e)[:50]}"
    finally:
        page.close()

def save_records(records):
    if not records: return
    keys = ["Title", "Release Date", "Description", "Poster Filename", "Watch URL"]
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(records)

def scrape_netflix_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_records = []
    processed_titles = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()
        
        print(f"Opening: {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)

        page_num = 1
        while True:
            print(f"\n--- Scraping Page {page_num} ---")
            
            # Scroll to load and ensure cards are interactable
            for i in range(5):
                page.mouse.wheel(0, 1000)
                time.sleep(1)
            time.sleep(2)
            
            # Find and process containers
            containers = page.query_selector_all("div[class*='TitleContainer']")
            print(f"Found {len(containers)} containers.")
            
            new_items_on_page = 0
            
            for container in containers:
                try:
                    # 1. Hover to reveal metadata (Crucial for date)
                    container.hover()
                    time.sleep(1) # Wait for overlay
                    
                    # 2. Extract Data from Card
                    link_el = container.query_selector("a[href*='/watch/']")
                    if not link_el: continue
                    
                    raw_title = link_el.get_attribute("aria-label") or link_el.inner_text()
                    title = raw_title.replace("在 Netflix 上观看", "").strip(" ()→").split("202")[0].strip()
                    
                    if not title or title in processed_titles: continue
                    
                    watch_url = link_el.get_attribute("href")
                    
                    # Date extraction with broader search in inner HTML
                    html = container.inner_html()
                    date_match = re.search(r'\d{4}/\d{1,2}/\d{1,2}', html)
                    release_date = date_match.group() if date_match else "Unknown"
                    
                    img_el = container.query_selector("img")
                    src = img_el.get_attribute("src") if img_el else None
                    
                    print(f"  [{len(all_records)+1}] {title} ({release_date})")
                    
                    # 3. Process image
                    poster_filename = "N/A"
                    if src:
                        high_res_url = get_high_res_url(src)
                        clean_title = "".join(x for x in title if x.isalnum() or x in " -_").strip()[:50]
                        poster_filename = f"{clean_title}.jpg"
                        target_path = os.path.join(OUTPUT_DIR, poster_filename)
                        if not os.path.exists(target_path):
                            download_image(high_res_url, target_path)
                    
                    # 4. Fetch Synopsis
                    description = get_description(context, watch_url)
                    
                    all_records.append({
                        "Title": title,
                        "Release Date": release_date,
                        "Description": description,
                        "Poster Filename": poster_filename,
                        "Watch URL": watch_url
                    })
                    processed_titles.add(title)
                    new_items_on_page += 1
                    save_records(all_records)

                except Exception as e:
                    pass

            print(f"Page {page_num} completed. Collected {new_items_on_page} items.")

            # Next Page logic
            next_page_num = page_num + 1
            next_btn = page.query_selector(f'button:has-text("{next_page_num}")')
            if not next_btn:
                next_btn = page.query_selector('button[aria-label="Next"], button[aria-label*="下一页"]')

            if next_btn and new_items_on_page > 0:
                print(f"Moving to Page {next_page_num}...")
                next_btn.click()
                page_num += 1
                time.sleep(10)
            else:
                break

        print(f"\nFinal Records: {len(all_records)}")
        browser.close()

if __name__ == "__main__":
    scrape_netflix_data()
