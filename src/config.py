from pathlib import Path

# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PRODUCT_CSV_PATH = DATA_DIR / "urbanthread_products.csv"
MANUAL_TEST_CSV_PATH = DATA_DIR / "manual_test_questions.csv"

# Required product CSV columns
REQUIRED_PRODUCT_COLUMNS = [
    "sku",
    "article_number",
    "product_name",
    "category",
    "price_usd",
    "color",
    "size",
    "stock_quantity",
    "stock_status",
    "description",
    "tags",
]

# Required manual test CSV columns
REQUIRED_TEST_COLUMNS = [
    "test_id",
    "test_type",
    "customer_question",
    "expected_behavior",
]

# Fallback support details
SUPPORT_NAME = "UrbanThread Support"
SUPPORT_EMAIL = "support@urbanthreaddemo.com"
SUPPORT_PHONE = "+1-555-0187"
SUPPORT_MESSAGE = "Please contact UrbanThread support for confirmation before placing an order."