# UrbanThread Product Data Chatbot

A portfolio-ready product data chatbot built for a mock ecommerce clothing brand, **UrbanThread Outfitters**.

The chatbot reads a structured product CSV file and answers customer questions about product availability, SKU, article number, category, size, color, price, stock status, and alternatives.

---

## Project Purpose

UrbanThread's support team manually checks product spreadsheets to answer customer questions. This creates slow replies and inconsistent answers.

This project solves that problem by providing a simple product assistant that answers only from the provided product dataset.

The chatbot does **not** invent products, prices, stock quantities, colors, sizes, or checkout information.

---

## Demo Video

Watch the demo here: https://youtu.be/YjDFajiNMW8

This demo shows the AI product data chatbot answering ecommerce product questions using structured catalog data such as product name, size, color, price, stock status, and sale items. It also shows how the bot handles missing or unavailable product queries safely.

---

## Client / Business Type

**Client:** UrbanThread Outfitters  
**Business type:** Small online clothing brand  
**Market:** USA-based casual clothing shoppers aged 18-35  
**Sales model:** Ecommerce product catalog maintained in spreadsheet form  

---

## Tech Stack

- Python
- Streamlit
- pandas
- pytest
- CSV data source

No OpenAI API is used in the MVP. The assistant uses safe rule-based product lookup logic to reduce hallucination risk.

---

## Folder Structure

```text
urbanthread-product-chatbot/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── urbanthread_products.csv
│   └── manual_test_questions.csv
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── product_search.py
│   └── chatbot.py
│
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_product_search.py
│   └── test_chatbot.py
│
└── screenshots/
