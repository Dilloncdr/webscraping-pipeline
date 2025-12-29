import os
import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------- CONFIG ----------
input_excel = r"C:\Users\Curve System\Desktop\Code dump\Web_Scraping\Nardeban\Nardeban_links.xlsx"
output_excel = "Nardeban_books.xlsx"
images_folder = "Nardeban_images"
os.makedirs(images_folder, exist_ok=True)

# ---------- LOAD LINKS ----------
df_links = pd.read_excel(input_excel)
urls = df_links.iloc[:, 0].dropna().tolist()

# ---------- RESUME CHECK ----------
if os.path.exists(output_excel):
    try:
        df_existing = pd.read_excel(output_excel)
        scraped_urls = set(df_existing["URL"].dropna().tolist())
        print(f"📂 Found existing data: {len(scraped_urls)} books already scraped.")
    except Exception:
        scraped_urls = set()
        print("⚠️ Existing Excel file found but could not read URLs, starting fresh.")
else:
    scraped_urls = set()
    print("🆕 No previous data found, starting from scratch.")

# ---------- FUNCTIONS ----------
def sanitize_filename(name: str) -> str:
    """Keep Persian filename but remove forbidden Windows characters."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.replace("\n", "").replace("\r", "").strip()
    return name[:100]

def get_soup(url: str):
    """Fetch page and return BeautifulSoup object."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/127.0.0.1 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        else:
            print(f"⚠️ Failed to load {url} (status {response.status_code})")
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
    return None

# ---------- SCRAPING ----------
books_data = []

for i, url in enumerate(urls, 1):
    if url in scraped_urls:
        print(f"⏭️ Skipping already scraped: {url}")
        continue

    print(f"\n[{i}/{len(urls)}] 🔍 Scraping: {url}")
    soup = get_soup(url)
    if not soup:
        continue

    # ---- Title ----
    title_tag = soup.select_one(".pro-detail-page__up_r__up_r h1")
    title = title_tag.text.strip() if title_tag else ""

    # ---- Details ----
    details = {
        "نویسنده": "",
        "مترجم": "",
        "تصویرگر": "",
        "رده سنی": "",
        "تعداد صفحه": "",
        "موضوع کتاب": "",
    }

    for li in soup.select(".pro-detail-center-r ul li"):
        try:
            label = li.find("label").get_text(strip=True).replace(":", "").replace("‌", "")
            value = li.find("span").get_text(strip=True)
            if label in details:
                details[label] = value
        except Exception:
            continue

    # ---- Image ----
    img_tag = soup.select_one(".pro-detail-image a")
    img_url = img_tag["href"] if (img_tag and img_tag.has_attr("href")) else ""

    img_path = ""
    if img_url and title:
        safe_title = sanitize_filename(title)
        img_path = os.path.join(images_folder, f"{safe_title}.png")
        if not os.path.exists(img_path):  # don't redownload if already saved
            try:
                img_data = requests.get(img_url, timeout=15).content
                with open(img_path, "wb") as f:
                    f.write(img_data)
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ Could not download image for {title}: {e}")
                img_path = ""

    # ---- Save info ----
    book_info = {
        "Title": title,
        "Author": details["نویسنده"],
        "Translator": details["مترجم"],
        "Artist": details["تصویرگر"],
        "Age Group": details["رده سنی"],
        "Pages": details["تعداد صفحه"],
        "Subject": details["موضوع کتاب"],
        "Image": img_path,
        "URL": url,
    }

    books_data.append(book_info)
    print(f"✅ Done: {title}")

    # Save progress after each book (so power-offs don’t erase work)
    df_partial = pd.DataFrame(books_data)
    if os.path.exists(output_excel):
        df_existing = pd.read_excel(output_excel)
        df_all = pd.concat([df_existing, df_partial], ignore_index=True)
    else:
        df_all = df_partial
    df_all.to_excel(output_excel, index=False)
    books_data.clear()  # reset after saving each batch

# ---------- DONE ----------
print(f"\n🎉 All available data saved to {output_excel}")
