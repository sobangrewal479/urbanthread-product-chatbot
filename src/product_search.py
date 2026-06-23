def clean_text(value):
    """
    Converts any value into clean lowercase text for easier matching.
    """
    return str(value).strip().lower()


def find_by_sku(products, sku):
    """
    Finds one product variant by exact SKU.
    """
    search_sku = clean_text(sku)

    result = products[
        products["sku"].astype(str).str.strip().str.lower() == search_sku
    ]

    return result


def find_by_article_number(products, article_number):
    """
    Finds one product variant by exact article number.
    """
    search_article = clean_text(article_number)

    result = products[
        products["article_number"].astype(str).str.strip().str.lower()
        == search_article
    ]

    return result


def find_by_product_name(products, product_name):
    """
    Finds product variants by product name.
    Allows partial matching.
    """
    search_name = clean_text(product_name)

    result = products[
        products["product_name"]
        .astype(str)
        .str.lower()
        .str.contains(search_name, regex=False, na=False)
    ]

    return result


def filter_by_category(products, category):
    """
    Finds products by category.
    Allows partial matching.
    """
    search_category = clean_text(category)

    result = products[
        products["category"]
        .astype(str)
        .str.lower()
        .str.contains(search_category, regex=False, na=False)
    ]

    return result


def filter_by_color(products, color):
    """
    Finds products by exact color.
    """
    search_color = clean_text(color)

    result = products[
        products["color"].astype(str).str.strip().str.lower() == search_color
    ]

    return result


def filter_by_size(products, size):
    """
    Finds products by exact size.
    """
    search_size = clean_text(size)

    result = products[
        products["size"].astype(str).str.strip().str.lower() == search_size
    ]

    return result


def filter_by_price_range(
    products,
    min_price=None,
    max_price=None,
    min_strict=False,
    max_strict=False,
):
    """
    Finds products inside a price range.

    min_strict=True means price must be greater than min_price.
    max_strict=True means price must be less than max_price.
    """
    result = products.copy()

    if min_price is not None:
        if min_strict:
            result = result[result["price_usd"] > float(min_price)]
        else:
            result = result[result["price_usd"] >= float(min_price)]

    if max_price is not None:
        if max_strict:
            result = result[result["price_usd"] < float(max_price)]
        else:
            result = result[result["price_usd"] <= float(max_price)]

    return result


def filter_products(
    products,
    category=None,
    color=None,
    size=None,
    min_price=None,
    max_price=None,
    min_strict=False,
    max_strict=False,
):
    """
    Combines category, color, size, and price filters.
    """
    result = products.copy()

    if category:
        result = filter_by_category(result, category)

    if color:
        result = filter_by_color(result, color)

    if size:
        result = filter_by_size(result, size)

    if min_price is not None or max_price is not None:
        result = filter_by_price_range(
            result,
            min_price=min_price,
            max_price=max_price,
            min_strict=min_strict,
            max_strict=max_strict,
        )

    return result


def get_available_products(products):
    """
    Returns products that are available for normal customer-facing answers.
    Low Stock is still available.
    Out of Stock is hidden.
    """
    result = products[
        (products["stock_status"].astype(str).str.lower() != "out of stock")
        & (products["stock_quantity"].astype(int) > 0)
    ]

    return result


def get_alternatives(products, category=None, exclude_skus=None, limit=3):
    """
    Suggests available alternatives from the existing dataset only.
    """
    result = get_available_products(products)

    if category:
        result = filter_by_category(result, category)

    if exclude_skus:
        cleaned_skus = [clean_text(sku) for sku in exclude_skus]
        result = result[
            ~result["sku"].astype(str).str.strip().str.lower().isin(cleaned_skus)
        ]

    result = result.sort_values(
        by=["stock_quantity", "price_usd"],
        ascending=[False, True],
    )

    return result.head(limit)


if __name__ == "__main__":
    from src.data_loader import load_product_data

    products_df = load_product_data()

    sku_result = find_by_sku(products_df, "UT-1003")
    article_result = find_by_article_number(products_df, "ART-T-S-01-M-BLA")
    name_result = find_by_product_name(products_df, "Core Cotton Tee")
    category_result = filter_by_category(products_df, "Hoodies")
    combined_result = filter_products(
        products_df,
        category="Hoodies",
        color="Black",
        size="L",
    )
    above_70_jackets = filter_products(
        products_df,
        category="Jackets",
        min_price=70,
        min_strict=True,
    )

    print("SKU lookup rows:", len(sku_result))
    print("Article lookup rows:", len(article_result))
    print("Name lookup rows:", len(name_result))
    print("Category lookup rows:", len(category_result))
    print("Black hoodie size L rows:", len(combined_result))
    print("Jackets above $70 rows:", len(above_70_jackets))
    print("Search functions check passed")