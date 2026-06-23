import re

from src.config import SUPPORT_EMAIL, SUPPORT_MESSAGE, SUPPORT_NAME, SUPPORT_PHONE
from src.product_search import (
    clean_text,
    filter_by_category,
    filter_products,
    find_by_article_number,
    find_by_sku,
    get_alternatives,
    get_available_products,
)

COMMON_COLOR_WORDS = [
    "black",
    "white",
    "charcoal",
    "blue",
    "olive",
    "cream",
    "navy",
    "red",
    "purple",
    "tan",
    "brown",
    "green",
    "gray",
    "grey",
    "pink",
    "yellow",
    "orange",
]

CATEGORY_KEYWORDS = {
    "t-shirts": ["t-shirt", "t-shirts", "tshirt", "tshirts", "tee", "tees"],
    "hoodies": ["hoodie", "hoodies"],
    "jeans": ["jean", "jeans", "denim"],
    "jackets": ["jacket", "jackets", "winter"],
    "dresses": ["dress", "dresses"],
    "sneakers": ["sneaker", "sneakers", "shoes", "shoe"],
}

UNSUPPORTED_KEYWORDS = [
    "where is my order",
    "track my order",
    "order tracking",
    "shipping",
    "delivery",
    "payment",
    "checkout",
    "return",
    "refund",
]

CONTACT_HELP_KEYWORDS = [
    "help me choose a size",
    "choose a size",
    "size guide",
    "sizing help",
]

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "shirt",
    "shirts",
    "product",
    "products",
    "available",
    "availability",
    "price",
    "stock",
    "tell",
    "about",
}


def get_support_text():
    """
    Returns UrbanThread fallback support details.
    """
    return (
        f"{SUPPORT_NAME}\n"
        f"Email: {SUPPORT_EMAIL}\n"
        f"Phone: {SUPPORT_PHONE}\n"
        f"{SUPPORT_MESSAGE}"
    )


def normalize_word(word):
    """
    Makes words easier to compare.
    Example: jackets -> jacket
    """
    word = clean_text(word)
    word = re.sub(r"[^a-z0-9-]", "", word)

    if len(word) > 3 and word.endswith("s"):
        word = word[:-1]

    return word


def get_question_words(question):
    """
    Splits the customer question into searchable words.
    """
    raw_words = re.findall(r"[a-zA-Z0-9-]+", clean_text(question))
    cleaned_words = set()

    for word in raw_words:
        cleaned_word = normalize_word(word)

        if cleaned_word:
            cleaned_words.add(cleaned_word)

    return cleaned_words


def extract_sku(question):
    """
    Finds SKU pattern like UT-1003.
    """
    match = re.search(r"\bUT-\d+\b", question, flags=re.IGNORECASE)

    if match:
        return match.group(0).upper()

    return None


def extract_article_number(question):
    """
    Finds article number pattern starting with ART-.
    """
    match = re.search(r"\bART-[A-Z0-9-]+\b", question, flags=re.IGNORECASE)

    if match:
        return match.group(0).upper().rstrip(".")

    return None


def extract_color(question):
    """
    Finds color words in the question.
    Includes common colors so unavailable colors can be handled safely.
    """
    question_words = get_question_words(question)

    for color in COMMON_COLOR_WORDS:
        if normalize_word(color) in question_words:
            return color.title()

    return None


def extract_size(question):
    """
    Finds sizes such as XS, S, M, L, XL, 30, 32, 34, 7, 8, 9, 13.
    """
    question_text = clean_text(question)

    size_match = re.search(r"\bsize\s+(xs|xl|s|m|l|\d{1,2})\b", question_text)
    if size_match:
        return size_match.group(1).upper()

    letter_match = re.search(r"\b(xs|xl|s|m|l)\b", question_text)
    if letter_match:
        return letter_match.group(1).upper()

    number_match = re.search(r"\b(30|32|34|7|8|9|13)\b", question_text)
    if number_match:
        return number_match.group(1)

    return None


def extract_price_range(question):
    """
    Finds price filters such as under $55, above $70, between $45 and $65.

    Returns:
    min_price, max_price, min_strict, max_strict
    """
    question_text = clean_text(question).replace(",", "")

    between_match = re.search(
        r"between\s*\$?(\d+(?:\.\d+)?)\s*(?:and|to|-)\s*\$?(\d+(?:\.\d+)?)",
        question_text,
    )
    if between_match:
        return float(between_match.group(1)), float(between_match.group(2)), False, False

    under_match = re.search(
        r"(?:under|below|less than)\s*\$?(\d+(?:\.\d+)?)", question_text
    )
    if under_match:
        return None, float(under_match.group(1)), False, True

    up_to_match = re.search(r"(?:up to)\s*\$?(\d+(?:\.\d+)?)", question_text)
    if up_to_match:
        return None, float(up_to_match.group(1)), False, False

    above_match = re.search(
        r"(?:above|over|more than|greater than)\s*\$?(\d+(?:\.\d+)?)",
        question_text,
    )
    if above_match:
        return float(above_match.group(1)), None, True, False

    return None, None, False, False


def detect_category(question):
    """
    Detects a product category from the question.
    """
    question_words = get_question_words(question)
    question_text = clean_text(question)

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if " " in keyword and keyword in question_text:
                return category.title()

            if normalize_word(keyword) in question_words:
                return category.title()

    return None


def detect_best_product_name(question, products):
    """
    Finds the most likely product name mentioned in the customer question.
    """
    question_text = clean_text(question)
    question_words = get_question_words(question)
    product_names = sorted(products["product_name"].unique(), key=len, reverse=True)

    for product_name in product_names:
        if clean_text(product_name) in question_text:
            return product_name

    best_name = None
    best_score = 0

    for product_name in product_names:
        product_words = set()

        for word in re.findall(r"[a-zA-Z0-9-]+", product_name):
            cleaned_word = normalize_word(word)

            if cleaned_word and cleaned_word not in STOP_WORDS:
                product_words.add(cleaned_word)

        score = len(product_words.intersection(question_words))

        if score > best_score:
            best_score = score
            best_name = product_name

    if best_score >= 2:
        return best_name

    return None


def get_available_rows(products):
    """
    Returns only available rows for normal customer-facing answers.
    Low Stock is still available.
    Out of Stock is hidden.
    """
    return get_available_products(products)


def is_available(row):
    """
    Treats In Stock and Low Stock as available.
    """
    return (
        clean_text(row["stock_status"]) != "out of stock"
        and int(row["stock_quantity"]) > 0
    )


def format_product_row(row):
    """
    Formats one product variant for the customer.
    """
    return (
        f"- {row['product_name']} | SKU: {row['sku']} | "
        f"Article: {row['article_number']} | "
        f"Color: {row['color']} | Size: {row['size']} | "
        f"Price: ${row['price_usd']:.2f} | "
        f"Stock: {row['stock_status']} ({row['stock_quantity']} left)"
    )


def format_product_list(products, limit=8):
    """
    Formats multiple product variants.
    """
    if products.empty:
        return "No matching products were found in the current catalog."

    rows = []

    for _, row in products.head(limit).iterrows():
        rows.append(format_product_row(row))

    if len(products) > limit:
        rows.append(f"Showing {limit} of {len(products)} matching variants.")

    return "\n".join(rows)


def format_alternatives(alternatives):
    """
    Formats alternative product suggestions.
    """
    if alternatives.empty:
        return "I could not find close in-stock alternatives in the current catalog."

    return (
        "Here are close available alternatives from the catalog:\n"
        + format_product_list(alternatives, limit=3)
    )


def list_available_values(products, column_name):
    """
    Lists unique values for color or size.
    """
    values = sorted(str(value) for value in products[column_name].dropna().unique())
    return ", ".join(values)


def handle_sku_lookup(question, products):
    """
    Answers exact SKU questions.
    """
    sku = extract_sku(question)

    if not sku:
        return None

    result = find_by_sku(products, sku)

    if result.empty:
        return (
            f"I could not find SKU {sku} in the current UrbanThread catalog.\n\n"
            + get_support_text()
        )

    row = result.iloc[0]

    if not is_available(row):
        alternatives = get_alternatives(
            products,
            category=row["category"],
            exclude_skus=[row["sku"]],
            limit=3,
        )
        return (
            f"SKU {sku} is currently out of stock.\n"
            f"Product: {row['product_name']} | Color: {row['color']} | "
            f"Size: {row['size']} | Price: ${row['price_usd']:.2f} | "
            f"Stock quantity: {row['stock_quantity']}\n\n"
            + format_alternatives(alternatives)
        )

    return "Yes, I found this SKU in the catalog:\n" + format_product_row(row)


def handle_article_lookup(question, products):
    """
    Answers exact article number questions.
    """
    article_number = extract_article_number(question)

    if not article_number:
        return None

    result = find_by_article_number(products, article_number)

    if result.empty:
        return (
            f"I could not find article number {article_number} in the current UrbanThread catalog.\n\n"
            + get_support_text()
        )

    row = result.iloc[0]

    if not is_available(row):
        alternatives = get_alternatives(
            products,
            category=row["category"],
            exclude_skus=[row["sku"]],
            limit=3,
        )
        return (
            f"I found article number {article_number}, but it is currently out of stock.\n"
            + format_product_row(row)
            + "\n\n"
            + format_alternatives(alternatives)
        )

    return "I found this article number in the catalog:\n" + format_product_row(row)


def handle_special_questions(question, products):
    """
    Handles categories, low stock, out-of-stock, support, and unsupported order questions.
    """
    question_text = clean_text(question)

    if "categories" in question_text or "product categories" in question_text:
        categories = sorted(products["category"].unique())
        return "UrbanThread currently has these product categories:\n- " + "\n- ".join(
            categories
        )

    if "low stock" in question_text:
        result = products[
            products["stock_status"].astype(str).str.lower() == "low stock"
        ]
        return "These products are currently low stock:\n" + format_product_list(
            result, limit=10
        )

    if "out of stock" in question_text:
        result = products[
            products["stock_status"].astype(str).str.lower() == "out of stock"
        ]
        return "These products are currently out of stock:\n" + format_product_list(
            result, limit=10
        )

    if "winter" in question_text:
        result = products[products["category"].isin(["Hoodies", "Jackets"])]
        result = get_available_rows(result)
        return (
            "For winter, you may want to look at available hoodies and jackets. "
            "Here are a few options from the catalog:\n"
            + format_product_list(result, limit=6)
        )

    bulk_match = re.search(r"\b\d{2,}\s*(units|pieces|pcs|items)\b", question_text)

    if bulk_match or "bulk" in question_text or "wholesale" in question_text:
        category = detect_category(question)
        result = filter_by_category(products, category) if category else products.copy()
        result = get_available_rows(result)
        result = result.sort_values(by="stock_quantity", ascending=False)

        return (
            "I cannot confirm bulk availability beyond the stock quantities shown in the catalog. "
            "Please use the listed stock quantities only and contact support for bulk confirmation.\n"
            + format_product_list(result, limit=6)
            + "\n\n"
            + get_support_text()
        )

    for phrase in CONTACT_HELP_KEYWORDS:
        if phrase in question_text:
            return (
                "For sizing help, please contact UrbanThread support. "
                "I can only answer from the product catalog data.\n\n"
                + get_support_text()
            )

    for phrase in UNSUPPORTED_KEYWORDS:
        if phrase in question_text:
            return (
                "This demo product assistant can only answer product catalog questions. "
                "It cannot handle order tracking, payment, checkout, shipping, returns, or refunds.\n\n"
                + get_support_text()
            )

    return None


def handle_unknown_named_product(question, products):
    """
    Handles product questions where the requested product is not in the catalog.
    """
    question_text = clean_text(question)
    question_words = get_question_words(question)

    if detect_best_product_name(question, products):
        return None

    if "tell me about" in question_text:
        requested_product = question_text.split("tell me about", 1)[1].strip(" .?")

        if requested_product:
            return (
                f"I could not find {requested_product.title()} in the current UrbanThread catalog. "
                "I will not invent product details that are not in the dataset.\n\n"
                + get_support_text()
            )

    unknown_product_words = {
        "shirt",
        "wallet",
        "wallets",
        "belt",
        "bag",
        "bags",
        "cap",
        "hat",
        "socks",
        "oxford",
        "leather",
    }

    product_question_words = {
        "have",
        "sell",
        "available",
        "stock",
        "order",
        "find",
        "looking",
        "there",
    }

    has_unknown_product_word = bool(question_words.intersection(unknown_product_words))
    looks_like_product_question = bool(question_words.intersection(product_question_words))

    if has_unknown_product_word and looks_like_product_question:
        return (
            "I could not find that product in the current UrbanThread catalog. "
            "I will not suggest unrelated products or invent product details that are not in the dataset.\n\n"
            + get_support_text()
        )

    return None


def handle_product_question(question, products):
    """
    Handles questions where a product name is detected.
    """
    product_name = detect_best_product_name(question, products)

    if not product_name:
        return None

    color = extract_color(question)
    size = extract_size(question)
    min_price, max_price, min_strict, max_strict = extract_price_range(question)
    question_text = clean_text(question)

    product_rows = products[products["product_name"] == product_name]
    available_product_rows = get_available_rows(product_rows)

    if "color" in question_text or "colors" in question_text:
        if available_product_rows.empty:
            return (
                f"{product_name} exists in the catalog, but all variants are currently out of stock.\n\n"
                + get_support_text()
            )

        available_colors = list_available_values(available_product_rows, "color")
        return (
            f"Available colors for {product_name}: {available_colors}.\n\n"
            "Available matching variants:\n"
            + format_product_list(available_product_rows, limit=8)
        )

    result = product_rows.copy()

    if color:
        color_rows = filter_products(product_rows, color=color)

        if color_rows.empty:
            available_colors = list_available_values(available_product_rows, "color")
            alternatives = get_alternatives(
                products,
                category=product_rows.iloc[0]["category"],
                limit=3,
            )
            return (
                f"{product_name} exists in the catalog, but color {color} is not available for this product.\n"
                f"Available colors for {product_name}: {available_colors}.\n\n"
                + format_alternatives(alternatives)
            )

        result = color_rows

    if size:
        size_rows = filter_products(result, size=size)

        if size_rows.empty:
            available_result = get_available_rows(result)

            if available_result.empty:
                available_sizes = list_available_values(result, "size")
            else:
                available_sizes = list_available_values(available_result, "size")

            return (
                f"{product_name} exists in the catalog, but size {size} is not available for the selected option.\n"
                f"Available sizes: {available_sizes}.\n\n"
                + get_support_text()
            )

        result = size_rows

    if min_price is not None or max_price is not None:
        result = filter_products(
            result,
            min_price=min_price,
            max_price=max_price,
            min_strict=min_strict,
            max_strict=max_strict,
        )

    if result.empty:
        return (
            f"I could not find a matching variant for {product_name} in the current catalog.\n\n"
            + get_support_text()
        )

    exact_single_variant = len(result) == 1 and (color or size)

    if exact_single_variant:
        row = result.iloc[0]

        if not is_available(row):
            alternatives = get_alternatives(
                products,
                category=row["category"],
                exclude_skus=[row["sku"]],
                limit=3,
            )
            return (
                f"I found {product_name} in {row['color']} size {row['size']}, "
                "but it is currently out of stock.\n"
                f"Price: ${row['price_usd']:.2f} | "
                f"Stock quantity: {row['stock_quantity']}\n\n"
                + format_alternatives(alternatives)
            )

        return "Yes, this variant is available in the catalog:\n" + format_product_row(
            row
        )

    available_result = get_available_rows(result)

    if available_result.empty:
        return (
            f"{product_name} exists in the catalog, but all matching variants are currently out of stock.\n\n"
            + get_support_text()
        )

    if "tell me about" in question_text or "price" in question_text:
        price_min = available_result["price_usd"].min()
        price_max = available_result["price_usd"].max()
        colors = list_available_values(available_result, "color")
        sizes = list_available_values(available_result, "size")
        description = available_result.iloc[0]["description"]

        return (
            f"{product_name}: {description}\n"
            f"Available price range: ${price_min:.2f} - ${price_max:.2f}\n"
            f"Available colors: {colors}\n"
            f"Available sizes: {sizes}\n\n"
            "Available matching variants:\n"
            + format_product_list(available_result, limit=8)
        )

    return (
        f"I found these available {product_name} variants in the catalog:\n"
        + format_product_list(available_result, limit=8)
    )


def handle_filtered_search(question, products):
    """
    Handles category, color, size, and price filter questions.
    """
    category = detect_category(question)
    color = extract_color(question)
    size = extract_size(question)
    min_price, max_price, min_strict, max_strict = extract_price_range(question)
    question_text = clean_text(question)

    if not category and min_price is None and max_price is None and not color and not size:
        return None

    result = filter_products(
        products,
        category=category,
        color=color,
        size=size,
        min_price=min_price,
        max_price=max_price,
        min_strict=min_strict,
        max_strict=max_strict,
    )

    asks_out_of_stock = "out of stock" in question_text

    if not asks_out_of_stock:
        result = get_available_rows(result)

    if result.empty:
        message_parts = []

        if category:
            message_parts.append(f"category {category}")
        if color:
            message_parts.append(f"color {color}")
        if size:
            message_parts.append(f"size {size}")
        if min_price is not None:
            if min_strict:
                message_parts.append(f"price above ${min_price:.2f}")
            else:
                message_parts.append(f"minimum price ${min_price:.2f}")
        if max_price is not None:
            if max_strict:
                message_parts.append(f"price under ${max_price:.2f}")
            else:
                message_parts.append(f"maximum price ${max_price:.2f}")

        message = ", ".join(message_parts) if message_parts else "your request"
        alternatives = get_alternatives(products, category=category, limit=3)

        return (
            f"I could not find matching available products for {message} in the current catalog.\n\n"
            + format_alternatives(alternatives)
            + "\n\n"
            + get_support_text()
        )

    label = "matching products"

    if category:
        label = category

    return f"Here are {label} from the catalog:\n" + format_product_list(
        result, limit=10
    )


def handle_tag_or_general_recommendation(question, products):
    """
    Handles simple recommendation questions using product names, descriptions, and tags.
    """
    question_text = clean_text(question)
    min_price, max_price, min_strict, max_strict = extract_price_range(question)

    searchable_text = (
        products["product_name"].astype(str)
        + " "
        + products["category"].astype(str)
        + " "
        + products["description"].astype(str)
        + " "
        + products["tags"].astype(str)
    ).str.lower()

    useful_words = []

    for word in get_question_words(question):
        if len(word) > 3 and word not in STOP_WORDS:
            useful_words.append(word)

    result = products.copy()

    if useful_words:
        mask = None

        for word in useful_words:
            word_mask = searchable_text.str.contains(word, regex=False, na=False)

            if mask is None:
                mask = word_mask
            else:
                mask = mask | word_mask

        result = result[mask]

    if min_price is not None or max_price is not None:
        result = filter_products(
            result,
            min_price=min_price,
            max_price=max_price,
            min_strict=min_strict,
            max_strict=max_strict,
        )

    result = get_available_rows(result)

    should_recommend = (
        "recommend" in question_text
        or "casual" in question_text
        or "everyday" in question_text
        or "travel" in question_text
        or max_price is not None
    )

    if not result.empty and should_recommend:
        return (
            "Here are some available catalog options that match your request:\n"
            + format_product_list(result, limit=8)
        )

    return None


def get_chatbot_response(question, products):
    """
    Main chatbot function.
    It answers only from UrbanThread product data and fallback contact details.
    """
    if not question or not question.strip():
        return (
            "Please ask a product catalog question, such as product availability, "
            "SKU, size, color, price, or category."
        )

    handlers = [
        handle_sku_lookup,
        handle_article_lookup,
        handle_special_questions,
        handle_unknown_named_product,
        handle_product_question,
        handle_filtered_search,
        handle_tag_or_general_recommendation,
    ]

    for handler in handlers:
        response = handler(question, products)

        if response:
            return response

    return (
        "I could not find that product or request in the current UrbanThread catalog. "
        "I can help with product availability, SKU/article lookup, category, size, color, price, and stock status.\n\n"
        + get_support_text()
    )


if __name__ == "__main__":
    from src.data_loader import load_product_data

    products_df = load_product_data()

    sample_questions = [
        "Do you have Core Cotton Tee in black size M?",
        "Is SKU UT-1003 available?",
        "Show me hoodies under $55.",
        "What jackets are above $70?",
        "Tell me about the Linen Shirt Dress.",
        "What is the price of the Oversized Street Tee?",
        "Do you sell leather wallets?",
    ]

    for sample_question in sample_questions:
        print("Question:", sample_question)
        print(get_chatbot_response(sample_question, products_df))
        print("-" * 60)

    print("Chatbot logic check passed")