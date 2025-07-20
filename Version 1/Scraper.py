import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

BASE_URL = "https://ersanails.com"
COLLECTION_URL = f"{BASE_URL}/collections/all"
IMAGE_FOLDER = "product_images"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Create folder for images
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def download_image(url, filename):
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        else:
            print(f"Failed to download image: {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

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
            break  # No more products

        for card in product_cards:
            try:
                name_tag = card.select_one("a.product-grid-item__title")
                price_tag = card.select_one("a.product-grid-item__price")
                img_tag = card.select_one("img")

                name = name_tag.get_text(strip=True) if name_tag else "N/A"
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                image_url = "https:" + img_tag["data-src"].split("?")[0] if img_tag and img_tag.has_attr("data-src") else ""
                product_url = BASE_URL + name_tag["href"] if name_tag and name_tag.has_attr("href") else ""

                # Save image locally
                safe_name = "".join(x for x in name if x.isalnum() or x in " _-")
                image_filename = os.path.join(IMAGE_FOLDER, safe_name.replace(" ", "_") + ".jpg")
                if image_url:
                    download_image(image_url, image_filename)

                products.append({
                    "Product Name": name,
                    "Price": price,
                    "Image URL": image_url,
                    "Local Image Path": image_filename,
                    "Product Page": product_url
                })
            except Exception as e:
                print("❌ Error parsing product:", e)
                continue

        page += 1
        time.sleep(1)

    return pd.DataFrame(products)



if __name__ == "__main__":
    df = scrape_ersa_nails()
    df.to_csv("ersa_nails_products_with_images.csv", index=False)
    print(f"✅ Scraped {len(df)} products.")
    print("📁 CSV saved as ersa_nails_products_with_images.csv")
    print(f"🖼 Images saved in ./{IMAGE_FOLDER}/")
