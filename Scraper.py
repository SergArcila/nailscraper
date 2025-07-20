import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://ersanails.com"
COLLECTION_URL = f"{BASE_URL}/collections/all"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

PRODUCTS_FOLDER = "Products"
os.makedirs(PRODUCTS_FOLDER, exist_ok=True)

def download_image(url, path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def sanitize(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()

def scrape_ersa_nails():
    products = []
    page = 1

    while True:
        url = f"{COLLECTION_URL}?page={page}"
        print(f"Scraping page {page}: {url}")
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "lxml")

        product_cards = soup.select("div.product-grid-item")
        if not product_cards:
            break

        for card in product_cards:
            try:
                name_tag = card.select_one("a.product-grid-item__title")
                price_tag = card.select_one("a.product-grid-item__price")
                image_tag = card.select_one("img")

                name = name_tag.get_text(strip=True)
                price = price_tag.get_text(strip=True)
                product_url = BASE_URL + name_tag["href"]
                safe_name = sanitize(name)
                product_folder = os.path.join(PRODUCTS_FOLDER, safe_name)
                os.makedirs(product_folder, exist_ok=True)

                image_urls = []
                if image_tag and image_tag.has_attr("srcset"):
                    # Extract each image in srcset
                    srcset = image_tag["srcset"]
                    parts = srcset.split(',')
                    for idx, part in enumerate(parts):
                        url = part.split()[0]
                        if url.startswith("//"):
                            url = "https:" + url
                        elif url.startswith("/"):
                            url = BASE_URL + url
                        image_urls.append(url)
                        # Download each image
                        image_filename = os.path.join(product_folder, f"{safe_name}_{idx+1}.jpg")
                        download_image(url, image_filename)

                elif image_tag and image_tag.has_attr("src"):
                    url = "https:" + image_tag["src"].split("?")[0]
                    image_urls.append(url)
                    image_filename = os.path.join(product_folder, f"{safe_name}.jpg")
                    download_image(url, image_filename)

                products.append({
                    "Product Name": name,
                    "Price": price,
                    "Product Page": product_url,
                    "Image URLs": ", ".join(image_urls)
                })

            except Exception as e:
                print(f"❌ Error parsing a product: {e}")
                continue

        page += 1
        time.sleep(1)

    return pd.DataFrame(products)

if __name__ == "__main__":
    df = scrape_ersa_nails()
    df.to_csv("ersa_nails_products.csv", index=False)
    print(f"✅ Scraped {len(df)} products")
    print(f"📁 CSV saved as ersa_nails_products.csv")
    print(f"🖼 Images organized in ./{PRODUCTS_FOLDER}/")
