import os
import json
import asyncio
import aiohttp
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

APP_EMAIL = os.getenv("APP_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
APP_IP = os.getenv("APP_IP")
APP_CLOUDFRONT = os.getenv("APP_CLOUDFRONT", "").rstrip("/")

LOGIN_URL = os.getenv("LOGIN_API_URL")
PRODUCT_URL = os.getenv("PRODUCT_API_URL") + "?id={}"

GOOGLE_SHEET_ID = os.getenv("G_SHEET_ID")
RANGE = "Definitivos!D2:I"

PRODUCTS_FILE = "data/products.json"

def get_google_sheets_data():
    """Fetches product IDs, names, and prices from Google Sheets."""
    g_key_json = os.getenv("G_KEY")
    
    if not g_key_json:
        raise ValueError("G_KEY is missing or not set correctly in GitHub secrets.")
    
    creds = Credentials.from_service_account_info(json.loads(g_key_json))
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets().values().get(spreadsheetId=GOOGLE_SHEET_ID, range=RANGE).execute()
    
    values = sheet.get("values", [])
    products = {}

    for row in values:
        print(f"Row data: {row}")  # Debugging line
        if len(row) < 9:
            continue
        name = row[3]
        product_id = row[4]
        price = row[6]
        categories = row[8]
        print(f"Product ID: {product_id}, Name: {name}, Price: {price}, Categories: {categories}")

        products[product_id] = {
            "name": name, 
            "price": price.strip(),
            "categories": categories.split(",")
        }
    
    return products

async def login(session):
    """Logs in and retrieves an authorization token asynchronously."""
    try:
        async with session.post(LOGIN_URL, json={
            "email": APP_EMAIL,
            "password": APP_PASSWORD,
            "white_brand_id": 1,
            "brand": "",
            "ipAddress": APP_IP,
            "otp": None
        }) as response:
            login_data = await response.json()
            return login_data.get("token")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

async def fetch_product_data(session, token, product_id):
    """Fetches product details asynchronously."""
    headers = {"X-Authorization": f"Bearer {token}"}
    try:
        async with session.get(PRODUCT_URL.format(product_id), headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("objects", {}) 
            else:
                return None
    except Exception as e:
        print(f"❌ Error fetching product {product_id}: {e}")
        return None

async def main():
    products_data = get_google_sheets_data()
    print(f"📦 Fetching details for {len(products_data)} products...")

    async with aiohttp.ClientSession() as session:
        token = await login(session)
        if not token:
            print("❌ Exiting: No valid token received.")
            return

        updated_data = {}

        for product_id, details in products_data.items():
            fetched_data = await fetch_product_data(session, token, product_id)
            if fetched_data:
                updated_data[product_id] = {
                    **details,
                    "stock": fetched_data.get("stock", ""),
                    "sku": fetched_data.get("sku", ""),
                    "variations": [
                        {
                            "attribute_values": [
                                {
                                    "attribute_name": variation.get("attribute_name", ""),
                                    "value": variation.get("value", ""),
                                    "id": variation.get("id", "")
                                } for variation in fetched_data.get("variations", [])
                            ],
                            "id": variation.get("id", ""),
                            "stock": variation.get("stock", "")
                        } for variation in fetched_data.get("attribute_values", [])
                    ],
                    "description": fetched_data.get("description", ""),
                    "active": fetched_data.get("active", ""),
                    "gallery": [
                        {
                            "id": img.get("id", ""),
                            "url": f"{APP_CLOUDFRONT}/{img.get('url', '')}" if img.get("url") else "",
                            "urlS3": f"{APP_CLOUDFRONT}/{img.get('urlS3', '')}" if img.get("urlS3") else "",
                            "variation_id": img.get("variation_id", "")
                        } for img in fetched_data.get("gallery", [])
                    ]
                }

    with open(PRODUCTS_FILE, "w", encoding="utf-8") as file:
        json.dump(updated_data, file, indent=2, ensure_ascii=False)

    print("✅ Products updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
