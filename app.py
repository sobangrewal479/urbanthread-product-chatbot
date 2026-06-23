import streamlit as st

from src.chatbot import get_chatbot_response
from src.data_loader import load_product_data


st.set_page_config(
    page_title="UrbanThread Product Assistant",
    page_icon="👕",
    layout="wide",
)


@st.cache_data
def get_products():
    """
    Loads product data once and caches it for the Streamlit app.
    """
    return load_product_data()


def show_sample_questions():
    """
    Shows sample questions customers can try.
    """
    st.sidebar.header("Sample Questions")

    sample_questions = [
        "Do you have Core Cotton Tee in black size M?",
        "Is SKU UT-1003 available?",
        "Show me hoodies under $55.",
        "Do you have jackets in size L?",
        "What categories do you have?",
        "Which products are low stock?",
        "Do you sell leather wallets?",
        "Where is my order?",
    ]

    for question in sample_questions:
        st.sidebar.write(f"- {question}")


def main():
    st.title("UrbanThread Product Assistant")
    st.write(
        "Ask about product availability, SKU, article number, category, size, color, price, and stock status."
    )

    try:
        products = get_products()
    except Exception as error:
        st.error("Product data could not be loaded.")
        st.exception(error)
        return

    show_sample_questions()

    with st.sidebar:
        st.header("Catalog Summary")
        st.write(f"Total product variants: {len(products)}")
        st.write(f"Categories: {products['category'].nunique()}")
        st.write(f"Products: {products['product_name'].nunique()}")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! I can help with UrbanThread product catalog questions. "
                    "Ask me about availability, price, size, color, SKU, article number, or stock status."
                ),
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    customer_question = st.chat_input("Ask a product question...")

    if customer_question:
        st.session_state.messages.append(
            {"role": "user", "content": customer_question}
        )

        with st.chat_message("user"):
            st.write(customer_question)

        answer = get_chatbot_response(customer_question, products)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

        with st.chat_message("assistant"):
            st.write(answer)

    with st.expander("View product catalog preview"):
        st.dataframe(products, width="stretch")


if __name__ == "__main__":
    main()