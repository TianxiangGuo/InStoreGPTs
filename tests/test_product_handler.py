import pytest
import pandas as pd
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.services.product_handler import ProductHandler  # Replace with your actual module name

# Sample DataFrame fixture using the adidas dataset
@pytest.fixture
def complete_products_df():
    # Load the full dataset as a fixture for testing
    # Load the uploaded CSV file
    file_path = 'example_data/adidas.csv'
    products_df = pd.read_csv(file_path)
    return products_df

# Test: Keyword-based search for "shorts"
def test_keyword_search_shorts(complete_products_df):
    query_json = {
        "query": {
            "AND": ["shorts"]
        }
    }
    result = ProductHandler.product_search(query_json, complete_products_df, search_columns=["PRODUCT_NAME", "DESCRIPTION"])
    # Print the result DataFrame for debugging
    print("\nResult DataFrame for 'shorts' query:")
    print(result)
    assert not result.empty, "Expected products with 'shorts' in the name or description, but none were found."
    assert all(
        "shorts" in (row['PRODUCT_NAME'].lower() + " " + row['DESCRIPTION'].lower())
        for _, row in result.iterrows()
    ), "All results should mention 'shorts' in either PRODUCT_NAME or DESCRIPTION."

# Test: Price filter with a keyword ("climbing") and max price $100
def test_price_filter_climbing(complete_products_df):
    query_json = {
        "query": {
            "AND": ["climbing"]
        },
        "filters": {
            "max_price": 100
        }
    }
    result = ProductHandler.product_search(query_json, complete_products_df, search_columns=["DESCRIPTION"])
    assert result.empty, "Expected no results for 'climbing' with max price $100, but found some."

# Test: Category filter for "Shoes"
def test_category_filter_shoes(complete_products_df):
    query_json = {
        "query": {
            "AND": ["shoes"]
        }
    }
    result = ProductHandler.product_search(query_json, complete_products_df[complete_products_df['CATEGORY_NAME'] == "Shoes"], search_columns=["PRODUCT_NAME", "DESCRIPTION"])
    assert not result.empty, "Expected products in the 'Shoes' category, but none were found."
    assert all(result['CATEGORY_NAME'] == "Shoes"), "All results should belong to the 'Shoes' category."

# Test: Keyword search "polo" with min price $60 and no discount
def test_keyword_search_polo_min_price(complete_products_df):
    query_json = {
        "query": {
            "AND": ["polo"]
        },
        "filters": {
            "min_price": 60,
            "has_discount": False
        }
    }
    result = ProductHandler.product_search(query_json, complete_products_df[(complete_products_df['PRICE'] >= 60) & (complete_products_df['DISCOUNT'] == 0)], search_columns=["PRODUCT_NAME"])
    assert not result.empty, "Expected products with 'polo' priced above $60 and no discount, but none were found."
    assert all("polo" in name for name in result['PRODUCT_NAME'].str.lower().values), "All results should mention 'polo'."
    assert all(result['PRICE'] >= 60), "All results should have a price of at least $60."
    assert all(result['DISCOUNT'] == 0), "All results should have no discount."