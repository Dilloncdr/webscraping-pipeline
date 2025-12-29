import os
import re
import time
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from unidecode import unidecode

# -------- CONFIG --------
input_excel = r"C:\Users\Curve System\Desktop\Code dump\Web_Scraping\Ghadyani\ghadyani_links.xlsx"     # Your Excel file containing links
output_excel = "books_data.xlsx"    # Output Excel
images_folder = "Ghadyani_images"       # Folder for downloaded images
os.makedirs(images_folder, exist_ok=True)

# -------- SETUP SELENIUM --------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 15)

# -------- LOAD LINKS --------
df_links = pd.read_excel(input_excel)
urls = df_links.iloc[:, 0].tolist()

books_data = []

for url in urls:
    try:
        driver.get(url)
        print(f"\nVisiting: {url}")
        time.sleep(4)  # wait a bit longer for React to render fully

        # Debug: save page HTML snapshot
        html_snapshot = driver.page_source
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html_snapshot)
        print("🧠 Saved debug_page.html")

        # Try more reliable selectors
        possible_selectors = [
            ".public-list li",  # primary
            "ul.public-list li.flex-start",
            "div.product-detail-up_left_bottom_right li"
        ]

        found = False
        details = {}
        for selector in possible_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                found = True
                for li in elements:
                    try:
                        label = li.find_element(By.TAG_NAME, "label").text.strip()
                        value = li.find_element(By.TAG_NAME, "span").text.strip()
                        details[label] = value
                    except:
                        pass
                break

        if not found:
            print("⚠️ Could not find details section!")

        # Extract title using multiple fallbacks
        title_selectors = [".hl-section", "h1", "h2", "title"]
        title = ""
        for sel in title_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                title = el.text.strip()
                if title:
                    break
            except:
                continue

        # Image extraction
        img_url = ""
        try:
            img_el = driver.find_element(By.CSS_SELECTOR, ".gallery-slider-item img")
            img_url = img_el.get_attribute("src")
        except:
            pass

        print(f"Title found: {title}")
        print(f"Details found: {details}")
        print(f"Image URL: {img_url}")

        # Save image
        def sanitize_filename(name):
            """Keep Persian title but remove forbidden characters for Windows filenames."""
            name = re.sub(r'[\\/*?:"<>|]', "_", name)  # replace forbidden characters
            name = name.replace("\n", "").replace("\r", "")  # remove line breaks if any
            name = name.strip()
            return name[:100]  # limit to 100 chars just to be safe


        if img_url and title:
            safe_title = sanitize_filename(title)
            img_path = os.path.join(images_folder, f"{safe_title}.jpg")
            try:
                img_data = requests.get(img_url).content
                with open(img_path, "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print(f"⚠️ Failed to download image for {title}: {e}")
        else:
            img_path = ""


    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")

# -------- SAVE DATA --------
df_books = pd.DataFrame(books_data)
...


# -------- SAVE DATA --------
df_books = pd.DataFrame(books_data)
df_books.to_excel(output_excel, index=False)
print(f"\n✅ All data saved to {output_excel}")
