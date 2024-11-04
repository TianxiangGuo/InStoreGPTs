import pytest
import pandas as pd
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from InStoreGPTs.services.product_handler import ProductHandler  # Replace with your actual module name

# Sample DataFrame fixture using the adidas dataset
@pytest.fixture
def product_handler():
    # Load the full dataset as a fixture for testing
    # Load the uploaded CSV file
    file_path = 'example_data/adidas.csv'
    ph = ProductHandler(file_path)
    return ph

# Test: Keyword-based search for "shorts"
def test_keyword_search_shorts(product_handler):
    query_json = """{
        "query": {
            "AND": ["shorts"]
        }
    }"""
    result = product_handler.product_search(query_json, search_columns=["PRODUCT_NAME", "DESCRIPTION"])
    # Print the result DataFrame for debugging
    print("\nResult DataFrame for 'shorts' query:")
    print(result)
    assert not result.empty, "Expected products with 'shorts' in the name or description, but none were found."
    assert all(
        "shorts" in (row['PRODUCT_NAME'].lower() + " " + row['DESCRIPTION'].lower())
        for _, row in result.iterrows()
    ), "All results should mention 'shorts' in either PRODUCT_NAME or DESCRIPTION."

# Test: Price filter with a keyword ("climbing") and max price $100
def test_price_filter_climbing(product_handler):
    query_json = """{
        "query": {
            "AND": ["climbing"]
        },
        "filters": {
            "max_price": 100
        }
    }"""
    result = product_handler.product_search(query_json, search_columns=["DESCRIPTION"])
    assert result.empty, "Expected no results for 'climbing' with max price $100, but found some."

# Test: Price filter with a keyword ("climbing") and max price $100
def test_discount_filter(product_handler):
    query_json = """{
        "query": {
            "AND": ["climbing"]
        },
        "filters": {
            "has_discount": true
        }
    }"""
    result = product_handler.product_search(query_json, search_columns=["DESCRIPTION"])
    assert result.empty, "Expected no results for 'climbing' with max price $100, but found some."

# Test: Keyword search "polo" with min price $60 and no discount
def test_keyword_search_polo_min_price(product_handler):
    query_json = """{
        "query": {
            "AND": ["polo"]
        },
        "filters": {
            "min_price": 60,
            "has_discount": false
        }
    }"""
    result = product_handler.product_search(query_json, search_columns=["PRODUCT_NAME", "DESCRIPTION"])
    assert not result.empty, "Expected products with 'polo' priced above $60 and no discount, but none were found."
    assert all("polo" in name for name in result['PRODUCT_NAME'].str.lower().values), "All results should mention 'polo'."
    assert all(result['PRICE'] >= 60), "All results should have a price of at least $60."
    assert all(result['DISCOUNT'] == 0), "All results should have no discount."