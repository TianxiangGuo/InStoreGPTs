import json
from pathlib import Path
from typing import List

import aiohttp
from ..prompts import product_search_prompt
from .llm_handler import LLMHandler

import pandas as pd

#TODO: decide a database. for now we will use padas dataframe
#TODO: implement embedding search & rank
#TODO: implement product recommendation based alread bought products
#TODO: handle invalid JSON format: add retry logic
#TODO: add customized filter options. e.g. cpu specs for hardware store, color/size for clothing store
#TODO: add links to the product pages for more details


class ProductHandler:
    """Handles the product recommendation based on the user's demand."""
    
    _df = None
    def __init__(self, csv_file: Path):
        self._df = pd.read_csv(csv_file)
        self._tools = [
            {
                'type': 'function', 
                'function': {
                    'name': 'product_search', 
                    'description': 'Searches for products based on user query.',
                    'parameters': {'type': 'object', 'properties': {'query_json': {'type': 'string', 'description':'user query JSON using `AND`, `OR`, and `NOT`, and filters'}}, 'required': ['query_json']},
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'transfer_to_navigation',
                    'description': 'Transfer the user to the navigation agent.',
                    'parameters': {'type': 'object', 'properties': {'summary': {'type': 'string', 'description':'summary of the products and locations the user wants to navigate to'}}, 'required': ['summary']}
                }
            }
        ]
        self.system_prompt = """You are a friendly, informal virtual assistant for Adidas, helping customers find products using the `ProductHandler` class and its `product_search` function. Recommend only from the results of the `product_search` function, not your internal knowledge.

### Workflow:
1. **User Input**: Understand what products the user wants.
2. **Clarification**: Ask questions if more details are needed. Don't ask if the request is clear.
3. **Query Creation**: Convert the request into structured JSON using `AND`, `OR`, and `NOT` with clear operation precedence.
4. **Function Call**: Use the structured JSON to call `product_search` from `ProductHandler`.
5. **Response**: Summarize the results clearly, highlighting product name, price, discount, location, and relevant features.

### Example:
**User Query**: "I'm looking for comfortable gym shorts or workout pants, but not cotton"

**Clarification**: "Do you have any color or price preferences?"

**User Reply**: "Items under $40. better with a discount"

**JSON for Function Call**:
{
  "query": {
    "OR": [
        {
        "AND": ["comfortable", "gym", "shorts"]
        },
        {
        "AND": ["workout", "pants"]
        }
    ],
    "NOT": ["cotton"],
  },
  "filters": { "max_price": 40, "has_discount": true }
}

**Function Call Instruction**:
Call the `product_search` function useing the generated JSON as parameter.

**Results**:
[
  {
    "product_name": "Adidas Aeroready Gym Shorts",
    "price": 35,
    "discount": 5,
    "in_store_location": "Aisle 3, Shelf 1",
    "description": "Lightweight gym shorts with moisture-wicking fabric"
  }
]

**Response**:
"We have Adidas Aeroready Gym Shorts for $35 with a $5 discount. They're lightweight with moisture-wicking fabric, perfect for gym sessions."

**User Reply**: "Where is it?"

**Function Call Instruction**: call the `transfer_to_navigation` function with summary "The customer wants to navigate to Aisle 3 Shelf 1 to find Adidas Aeroready Gym Shorts. The current location of the customer is unknown".

### Guidelines:
- Ensure JSON accurately represents user requests with logical operators, including `AND`, `OR`, and `NOT`.
- Call the `product_search` function with the generated JSON.
- Do Not show function call process in the response.
- Keep responses concise and engaging.
- Highlight features that match the user's needs.
- Maintain a friendly and approachable tone."""

    # Function to process JSON query and filter the DataFrame
    def evaluate_condition(self, condition, row_text):
        # If condition is a string, convert to lowercase for case-insensitive matching
        if isinstance(condition, str):
            return condition.lower() in row_text
        elif isinstance(condition, dict):
            for key, value in condition.items():
                if key == "AND":
                    return all(self.evaluate_condition(sub, row_text) for sub in value)
                elif key == "OR":
                    return any(self.evaluate_condition(sub, row_text) for sub in value)
                elif key == "NOT":
                    return not any(self.evaluate_condition(sub, row_text) for sub in value)
        return False

    def keyword_search_with_json(self, query_json, df, search_columns):
        # Get a list of row indices that match the query
        matching_indices = []
        for idx, row in df.iterrows():
            row_text = " ".join(str(row[col]).lower() for col in search_columns)
            if self.evaluate_condition(query_json['query'], row_text):
                matching_indices.append(idx)
        
        # Return a DataFrame containing all columns from the original DataFrame for the matching rows
        return df.loc[matching_indices]
    
    def embedding_search(self, query, df, search_columns):
        pass

    def rank_results(self, results, query):
        pass

    # Function to filter products by price range
    def filter_by_price_range(self, df, min_price=None, max_price=None):
        if min_price is not None:
            df = df[df['PRICE'] >= min_price]
        if max_price is not None:
            df = df[df['PRICE'] <= max_price]
        return df

    # Function to filter products by discount availability
    def filter_by_discount(self, df, has_discount=True):
        if has_discount:
            df = df[df['DISCOUNT'] > 0]
        else:
            df = df[df['DISCOUNT'] == 0]
        return df

    # Main product search function
    def product_search(self, query_json, search_columns, max_results=5):
        # Step 1: Apply price filters if provided
        filtered_df = self._df.copy()  # Ensure filtered_df starts as a copy of df
        try:
            query_json = json.loads(query_json)
            if 'filters' in query_json:
                filters = query_json['filters']
                min_price = filters.get('min_price')
                max_price = filters.get('max_price')
                has_discount = filters.get('has_discount')
                
                if min_price is not None or max_price is not None:
                    filtered_df = self.filter_by_price_range(filtered_df, min_price, max_price)
                
                if has_discount is not None:
                    filtered_df = self.filter_by_discount(filtered_df, has_discount)

            # Step 2: Perform keyword-based search
            filtered_df = self.keyword_search_with_json(query_json, filtered_df, search_columns)
        
        except Exception as e:
            raise ValueError(f"Invalid JSON format: {e}")

        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.max_colwidth', None) # Show full content of each column
        print(filtered_df.head(max_results))
        return filtered_df.head(max_results)

