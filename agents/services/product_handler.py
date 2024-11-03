import json
from pathlib import Path
from typing import List

import aiohttp
from ..prompts import product_search_prompt
from .llm_handler import LLMHandler

import pandas as pd

#TODO: decide a database. for now we will use padas dataframe
#TODO: implement product recommendation
#TODO: implement embedding search & rank


class ProductHandler:
    """Handles the product recommendation based on the user's demand."""

    # Function to process JSON query and filter the DataFrame
    @staticmethod
    def evaluate_condition(condition, row_text):
        if isinstance(condition, str):
            return condition in row_text
        elif isinstance(condition, dict):
            for key, value in condition.items():
                if key == "AND":
                    return all(ProductHandler.evaluate_condition(sub, row_text) for sub in value)
                elif key == "OR":
                    return any(ProductHandler.evaluate_condition(sub, row_text) for sub in value)
                elif key == "NOT":
                    return not any(ProductHandler.evaluate_condition(sub, row_text) for sub in value)
        return False

    @staticmethod
    def keyword_search_with_json(query_json, df, search_columns):
        results = []
        for _, row in df.iterrows():
            row_text = " ".join(str(row[col]).lower() for col in search_columns)
            if ProductHandler.evaluate_condition(query_json['query'], row_text):
                results.append(row)
        return pd.DataFrame(results)
    
    def embedding_search(self, query, df, search_columns):
        pass

    def rank_results(self, results, query):
        pass

    # Function to filter products by price range
    @staticmethod
    def filter_by_price_range(df, min_price=None, max_price=None):
        if min_price is not None:
            df = df[df['PRICE'] >= min_price]
        if max_price is not None:
            df = df[df['PRICE'] <= max_price]
        return df

    # Function to filter products by discount availability
    @staticmethod
    def filter_by_discount(df, has_discount=True):
        if has_discount:
            df = df[df['DISCOUNT'] > 0]
        else:
            df = df[df['DISCOUNT'] == 0]
        return df

    # Main product search function
    @staticmethod
    def product_search(query_json, df, search_columns):
        # Step 1: Apply price filters if provided
        filtered_df = df.copy()  # Ensure filtered_df starts as a copy of df
        if 'filters' in query_json:
            filters = query_json['filters']
            min_price = filters.get('min_price')
            max_price = filters.get('max_price')
            has_discount = filters.get('has_discount')
            
            if min_price is not None or max_price is not None:
                filtered_df = ProductHandler.filter_by_price_range(filtered_df, min_price, max_price)
            
            if has_discount is not None:
                filtered_df = ProductHandler.filter_by_discount(filtered_df, has_discount)

        # Step 2: Perform keyword-based search
        filtered_df = ProductHandler.keyword_search_with_json(query_json, filtered_df, search_columns)
        
        return filtered_df