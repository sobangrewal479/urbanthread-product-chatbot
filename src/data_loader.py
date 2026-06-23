import pandas as pd

from src.config import (
    PRODUCT_CSV_PATH,
    MANUAL_TEST_CSV_PATH,
    REQUIRED_PRODUCT_COLUMNS,
    REQUIRED_TEST_COLUMNS,
)


def validate_columns(dataframe, required_columns, file_name):
    """
    Checks that the CSV file has all required columns.
    """
    missing_columns = []

    for column in required_columns:
        if column not in dataframe.columns:
            missing_columns.append(column)

    if missing_columns:
        raise ValueError(
            f"{file_name} is missing these required columns: {missing_columns}"
        )


def load_product_data():
    """
    Loads UrbanThread product data from CSV.
    """
    if not PRODUCT_CSV_PATH.exists():
        raise FileNotFoundError(f"Product CSV not found at: {PRODUCT_CSV_PATH}")

    products = pd.read_csv(PRODUCT_CSV_PATH)

    validate_columns(
        dataframe=products,
        required_columns=REQUIRED_PRODUCT_COLUMNS,
        file_name="urbanthread_products.csv",
    )

    products["price_usd"] = pd.to_numeric(products["price_usd"], errors="coerce")
    products["stock_quantity"] = pd.to_numeric(
        products["stock_quantity"], errors="coerce"
    ).fillna(0).astype(int)

    products = products.fillna("")

    return products


def load_manual_tests():
    """
    Loads manual test questions from CSV.
    """
    if not MANUAL_TEST_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Manual test CSV not found at: {MANUAL_TEST_CSV_PATH}"
        )

    manual_tests = pd.read_csv(MANUAL_TEST_CSV_PATH)

    validate_columns(
        dataframe=manual_tests,
        required_columns=REQUIRED_TEST_COLUMNS,
        file_name="manual_test_questions.csv",
    )

    manual_tests = manual_tests.fillna("")

    return manual_tests


if __name__ == "__main__":
    products_df = load_product_data()
    manual_tests_df = load_manual_tests()

    print("Product data loaded successfully")
    print("Manual test data loaded successfully")
    print(f"Product rows: {len(products_df)}")
    print(f"Product columns: {len(products_df.columns)}")
    print(f"Manual test rows: {len(manual_tests_df)}")
    print(f"Manual test columns: {len(manual_tests_df.columns)}")