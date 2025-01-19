import os
import json
import requests

# Load environment variables
DROPI_EMAIL = os.getenv("DROPI_EMAIL")
DROPI_PASSWORD = os.getenv("DROPI_PASSWORD")
DROPI_CLOUDFRONT = os.getenv("DROPI_CLOUDFRONT", "").rstrip("/")  # Ensure no trailing slash

LOGIN_URL = "https://api.dropi.co/api/login"
PRODUCT_URL = "https://api.dropi.co/api/products/productlist/v1/show/?id={}"

PRODUCTS_FILE = "data/products.json"

def login():
    """Logs in and retrieves an authorization token."""
    response = requests.post(LOGIN_URL, json={
        "email": DROPI_EMAIL,
        "password": DROPI_PASSWORD,
        "white_brand_id": 1,
        "brand": "",
        "ipAddress": "190.28.6.43",
        "otp": None
    })
    response.raise_for_status()
    return response.json().get("token")

def fetch_product_data(token, product_id):
    """Fetches product details from the API."""
    headers = {"X-Authorization": f"Bearer {token}"}
    response = requests.get(PRODUCT_URL.format(product_id), headers=headers)
    
    if response.status_code == 404:
        print(f"Product {product_id} not found, skipping...")
        return None

    response.raise_for_status()
    return response.json()

def augment_product_data(existing_data, fetched_data):
    """Merges fetched product data with existing data."""
    return {
        "price": existing_data["price"],
        "categories": existing_data["categories"],
        "id": fetched_data.get("id", ""),
        "stock": fetched_data.get("stock", ""),
        "sku": fetched_data.get("sku", ""),
        "variations": [
            {
                "attribute_values": [
                    {
                        "attribute_name": attr.get("attribute_name", ""),
                        "value": attr.get("value", ""),
                        "id": attr.get("id", "")
                    } for attr in variation.get("attribute_values", [])
                ],
                "id": variation.get("id", ""),
                "stock": variation.get("stock", "")
            } for variation in fetched_data.get("variations", [])
        ],
        "name": fetched_data.get("name", ""),
        "description": fetched_data.get("description", ""),
        "active": fetched_data.get("active", ""),
        "gallery": [
            {
                "id": img.get("id", ""),
                "url": f"{DROPI_CLOUDFRONT}/{img.get('url', '')}" if img.get("url") else "",
                "urlS3": f"{DROPI_CLOUDFRONT}/{img.get('urlS3', '')}" if img.get("urlS3") else "",
                "variation_id": img.get("variation_id", "")
            } for img in fetched_data.get("gallery", [])
        ]
    }

def main():
    # Load product IDs from existing JSON
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
        products_data = json.load(file)

    product_ids = list(products_data.keys())  # Extract IDs from keys
    print(f"Fetching details for {len(product_ids)} products...")

    token = login()

    updated_data = {}
    for product_id in product_ids:
        fetched_data = fetch_product_data(token, product_id)
        if fetched_data:
            updated_data[product_id] = augment_product_data(products_data[product_id], fetched_data)

    # Save updated JSON
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as file:
        json.dump(updated_data, file, indent=2, ensure_ascii=False)

    print("✅ Products updated successfully!")

if __name__ == "__main__":
    main()
