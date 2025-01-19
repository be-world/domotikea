import os
import json
import asyncio
import aiohttp

# Load environment variables
DROPI_EMAIL = os.getenv("DROPI_EMAIL")
DROPI_PASSWORD = os.getenv("DROPI_PASSWORD")
DROPI_CLOUDFRONT = os.getenv("DROPI_CLOUDFRONT", "").rstrip("/")  # Ensure no trailing slash

LOGIN_URL = "https://api.dropi.co/api/login"
PRODUCT_URL = "https://api.dropi.co/api/products/productlist/v1/show/?id={}"

PRODUCTS_FILE = "data/products.json"

async def login(session):
    """Logs in and retrieves an authorization token asynchronously."""
    try:
        async with session.post(LOGIN_URL, json={
            "email": DROPI_EMAIL,
            "password": DROPI_PASSWORD,
            "white_brand_id": 1,
            "brand": "",
            "ipAddress": "190.28.6.43",
            "otp": None
        }) as response:
            login_data = await response.json()
            if response.status != 200:
                print(f"❌ Login failed: {response.status} - {login_data}")
                return None
            
            token = login_data.get("token")
            if not token:
                print(f"❌ Login response: {login_data}")
                print("❌ No token received!")
            else:
                print(f"✅ Login successful! Token: {token[:20]}... (truncated for security)")

            return token
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

async def fetch_product_data(session, token, product_id):
    """Fetches product details asynchronously."""
    headers = {"X-Authorization": f"Bearer {token}"}
    try:
        async with session.get(PRODUCT_URL.format(product_id), headers=headers) as response:
            product_data = await response.json()
            
            if response.status == 404:
                print(f"⚠️ Product {product_id} not found, skipping...")
                return None
            if response.status != 200:
                print(f"❌ Error fetching product {product_id}: {response.status} - {product_data}")
                return None
            
            print(f"✅ Fetched product {product_id} response: {json.dumps(product_data, indent=2)[:500]}... (truncated)")
            return product_data.get("objects", {})
    except Exception as e:
        print(f"❌ Error fetching product {product_id}: {e}")
        return None

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

async def main():
    # Load product IDs from existing JSON
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
            products_data = json.load(file)
    except FileNotFoundError:
        print(f"❌ Error: {PRODUCTS_FILE} not found.")
        return

    product_ids = list(products_data.keys())  # Extract IDs from keys
    print(f"📦 Fetching details for {len(product_ids)} products...")

    async with aiohttp.ClientSession() as session:
        token = await login(session)
        if not token:
            print("❌ Exiting: No valid token received.")
            return

        updated_data = {}

        # Fetch product data one by one, ensuring each request completes before moving to the next
        for product_id in product_ids:
            fetched_data = await fetch_product_data(session, token, product_id)
            if fetched_data:
                updated_data[product_id] = augment_product_data(products_data[product_id], fetched_data.objects)

    # Save updated JSON
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as file:
        json.dump(updated_data, file, indent=2, ensure_ascii=False)

    print("✅ Products updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
