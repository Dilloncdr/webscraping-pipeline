# Publisher Web Scraping & Image Processing Pipeline

This repository contains a collection of real-world web scraping and image processing scripts
developed to collect missing product metadata and images for a bookstore website.

The project demonstrates scraping **dynamic and static websites**, handling Persian/Unicode data,
and post-processing images to meet e-commerce presentation standards.

---

## Use Case
Several publishers did not provide structured APIs for accessing product information.
To complete the bookstore’s product archive, this pipeline was built to:

- Collect product links
- Scrape metadata and images
- Normalize and clean scraped data
- Standardize images for website use

---

## Scraping Components

### Selenium-based scraping
Used for publishers with dynamically rendered (React) pages.

- `scrapers/ghadyani_selenium.py`
- `scrapers/ghadyani_metadata.py`

Features:
- Headless Chrome
- Explicit waits
- Multiple selector fallbacks
- Unicode-safe image saving
- Excel export

---

### Requests + BeautifulSoup scraping
Used for static or semi-static publisher websites.

- `scrapers/nardeban_link_collector.py`
- `scrapers/nardeban_scraper.py`

Features:
- Polite crawling with delays
- Resume-safe scraping
- Incremental Excel saving
- Image downloading

---

## Image Processing Components

### Image normalization
- `image_processing/image_editor.py`

Features:
- Aspect-ratio based resizing
- Template-based background compositing
- Unicode-safe OpenCV I/O
- Conversion to website-ready JPEGs

---

### Transparency cleanup
- `image_processing/transparency_remover.py`

Features:
- Alpha-channel analysis
- Cropping transparent borders
- Prepares images for further processing

---

## Project Structure
