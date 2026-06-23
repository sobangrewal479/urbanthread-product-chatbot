from src.config import REQUIRED_PRODUCT_COLUMNS, REQUIRED_TEST_COLUMNS
from src.data_loader import load_manual_tests, load_product_data


def test_product_csv_loads_successfully():
    products = load_product_data()

    assert len(products) == 84
    assert len(products.columns) == 11

    for column in REQUIRED_PRODUCT_COLUMNS:
        assert column in products.columns


def test_manual_test_csv_loads_successfully():
    manual_tests = load_manual_tests()

    assert len(manual_tests) == 35
    assert len(manual_tests.columns) == 4

    for column in REQUIRED_TEST_COLUMNS:
        assert column in manual_tests.columns


def test_product_price_and_stock_are_clean_numbers():
    products = load_product_data()

    assert products["price_usd"].isna().sum() == 0
    assert products["stock_quantity"].isna().sum() == 0
    assert products["stock_quantity"].min() >= 0