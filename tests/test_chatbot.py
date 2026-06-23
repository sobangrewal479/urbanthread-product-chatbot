from src.chatbot import get_chatbot_response
from src.data_loader import load_product_data


def test_chatbot_answers_exact_available_product_variant():
    products = load_product_data()

    response = get_chatbot_response(
        "Do you have Core Cotton Tee in black size M?",
        products,
    )

    assert "Core Cotton Tee" in response
    assert "SKU: UT-1003" in response
    assert "Color: Black" in response
    assert "Size: M" in response
    assert "Price:" in response
    assert "Stock:" in response


def test_chatbot_answers_exact_sku_lookup():
    products = load_product_data()

    response = get_chatbot_response("Is SKU UT-1003 available?", products)

    assert "UT-1003" in response
    assert "Core Cotton Tee" in response
    assert "Black" in response
    assert "Size: M" in response


def test_chatbot_handles_out_of_stock_sku_safely():
    products = load_product_data()

    response = get_chatbot_response("Can I order SKU UT-1001 today?", products)

    assert "UT-1001" in response
    assert "out of stock" in response.lower()
    assert "alternatives" in response.lower()


def test_chatbot_handles_unknown_sku_with_fallback():
    products = load_product_data()

    response = get_chatbot_response("Is UT-9999 available?", products)

    assert "could not find" in response.lower()
    assert "UT-9999" in response
    assert "support@urbanthreaddemo.com" in response


def test_chatbot_answers_article_number_lookup():
    products = load_product_data()

    response = get_chatbot_response("Find article ART-T-S-01-M-BLA.", products)

    assert "ART-T-S-01-M-BLA" in response
    assert "UT-1003" in response
    assert "Core Cotton Tee" in response


def test_chatbot_handles_unavailable_color_without_inventing():
    products = load_product_data()

    response = get_chatbot_response("Do you have Core Cotton Tee in Red?", products)

    assert "Core Cotton Tee" in response
    assert "Red" in response
    assert "not available" in response.lower()
    assert "Color: Red" not in response


def test_chatbot_handles_unknown_product_without_showing_unrelated_products():
    products = load_product_data()

    response = get_chatbot_response("Tell me about the Linen Shirt Dress.", products)

    assert "could not find" in response.lower()
    assert "Linen Shirt Dress" in response
    assert "support@urbanthreaddemo.com" in response
    assert "Everyday Midi Dress" not in response
    assert "Ribbed Knit Dress" not in response


def test_chatbot_filters_jackets_above_70_correctly():
    products = load_product_data()

    response = get_chatbot_response("What jackets are above $70?", products)

    assert "Jackets" in response
    assert "Price: $70.00" not in response
    assert "Out of Stock (0 left)" not in response
    assert "Price: $72.00" in response or "Price: $74.00" in response or "Price: $90.00" in response


def test_chatbot_price_answer_hides_out_of_stock_variants():
    products = load_product_data()

    response = get_chatbot_response(
        "What is the price of the Oversized Street Tee?",
        products,
    )

    assert "Oversized Street Tee" in response
    assert "Available price range" in response
    assert "Out of Stock (0 left)" not in response


def test_chatbot_handles_unsupported_order_tracking_question():
    products = load_product_data()

    response = get_chatbot_response("Where is my order?", products)

    assert "only answer product catalog questions" in response.lower()
    assert "order tracking" in response.lower()
    assert "support@urbanthreaddemo.com" in response


def test_chatbot_handles_unavailable_navy_hoodie_variant():
    products = load_product_data()

    response = get_chatbot_response("Show navy hoodies size L.", products)

    assert "Navy" in response
    assert "could not find" in response.lower() or "not available" in response.lower()
    assert "Color: Navy" not in response
    assert "support@urbanthreaddemo.com" in response