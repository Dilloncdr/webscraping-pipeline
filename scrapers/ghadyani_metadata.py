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

# -------- CONFIG --------
input_excel = r"C:\Users\Curve System\Desktop\Code dump\Web_Scraping\Ghadyani\ghadyani_links.xlsx"
output_excel = "ghadyani_books_data.xlsx"
# images_folder = "Ghadyani_images"  # Images already downloaded

# -------- SELENIUM SETUP --------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(), options=chrome_options)
wait = WebDriverWait(driver, 10)

# -------- LOAD LINKS --------
df_links = pd.read_excel(input_excel)
urls = df_links.iloc[:, 0].tolist()

books_data = []

# -------- SCRAPE EACH PAGE --------
for i, url in enumerate(urls, start=1):
    try:
        print(f"\n[{i}/{len(urls)}] Visiting: {url}")
        driver.get(url)

        # Wait for the details section to load (React delay)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".public-list li")))
        except:
            time.sleep(2)  # fallback delay

        # ---- TITLE ----
        title = ""
        for sel in [".hl-section", ".product-detail-up_left_bottom_right h1", "h1", "title"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.text.strip():
                    title = el.text.strip()
                    break
            except:
                continue

        # ---- DETAILS (author, translator, etc.) ----
        details = {}
        li_elements = driver.find_elements(By.CSS_SELECTOR, ".public-list li")
        for li in li_elements:
            try:
                label = li.find_element(By.TAG_NAME, "label").text.strip().replace(":", "")
                value = li.find_element(By.TAG_NAME, "span").text.strip()
                details[label] = value
            except:
                continue

        # ---- IMAGE (commented out since already downloaded) ----
        # img_url = ""
        # try:
        #     img_el = driver.find_element(By.CSS_SELECTOR, ".gallery-slider-item img")
        #     img_url = img_el.get_attribute("src")
        # except:
        #     pass

        # if img_url and title:
        #     safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        #     img_path = os.path.join(images_folder, f"{safe_title}.jpg")
        #     if not os.path.exists(img_path):
        #         img_data = requests.get(img_url).content
        #         with open(img_path, "wb") as f:
        #             f.write(img_data)

        # ---- ADD TO LIST ----
        book_info = {"Title": title, "URL": url}
        book_info.update(details)
        books_data.append(book_info)

        print(f"✅ Extracted: {title if title else 'No title found'} | {len(details)} fields")

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")

# -------- SAVE TO EXCEL --------
driver.quit()
df_books = pd.DataFrame(books_data)
df_books.to_excel(output_excel, index=False)
print(f"\n✅ All data saved to {output_excel}")
