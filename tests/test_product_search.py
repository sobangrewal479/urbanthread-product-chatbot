from src.data_loader import load_product_data
from src.product_search import (
    filter_by_category,
    filter_products,
    find_by_article_number,
    find_by_product_name,
    find_by_sku,
    get_available_products,
)


def test_find_by_sku_returns_exact_product_variant():
    products = load_product_data()

    result = find_by_sku(products, "UT-1003")

    assert len(result) == 1

    row = result.iloc[0]

    assert row["sku"] == "UT-1003"
    assert row["product_name"] == "Core Cotton Tee"
    assert row["color"] == "Black"
    assert row["size"] == "M"


def test_find_by_unknown_sku_returns_empty_result():
    products = load_product_data()

    result = find_by_sku(products, "UT-9999")

    assert result.empty


def test_find_by_article_number_returns_exact_product_variant():
    products = load_product_data()

    result = find_by_article_number(products, "ART-T-S-01-M-BLA")

    assert len(result) == 1

    row = result.iloc[0]

    assert row["sku"] == "UT-1003"
    assert row["article_number"] == "ART-T-S-01-M-BLA"


def test_find_by_product_name_returns_all_core_cotton_tee_variants():
    products = load_product_data()

    result = find_by_product_name(products, "Core Cotton Tee")

    assert len(result) == 6
    assert set(result["product_name"]) == {"Core Cotton Tee"}


def test_filter_by_category_returns_hoodies():
    products = load_product_data()

    result = filter_by_category(products, "Hoodies")

    assert len(result) == 14
    assert set(result["category"]) == {"Hoodies"}


def test_combined_filter_returns_black_sneakers_size_8():
    products = load_product_data()

    result = filter_products(
        products,
        category="Sneakers",
        color="Black",
        size="8",
    )

    assert not result.empty
    assert set(result["category"]) == {"Sneakers"}
    assert set(result["color"]) == {"Black"}
    assert set(result["size"].astype(str)) == {"8"}


def test_strict_price_filter_above_70_excludes_70_dollar_jackets():
    products = load_product_data()

    result = filter_products(
        products,
        category="Jackets",
        min_price=70,
        min_strict=True,
    )

    assert not result.empty
    assert result["price_usd"].min() > 70
    assert 70 not in set(result["price_usd"])


def test_get_available_products_excludes_out_of_stock_rows():
    products = load_product_data()

    result = get_available_products(products)

    assert not result.empty
    assert "Out of Stock" not in set(result["stock_status"])
    assert result["stock_quantity"].min() > 0