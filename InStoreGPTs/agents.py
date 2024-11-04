import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# print(sys.path)
from swarm import Agent
from typing import Optional, List, Dict, Union
from InStoreGPTs.prompts import sales_system_prompt
from InStoreGPTs.services.product_handler import ProductHandler
from InStoreGPTs.services.navigation_handler import NavigationHandler

adidas_csv = 'example_data/adidas.csv'
ph = ProductHandler(adidas_csv)
def product_search(query_json):
    return ph.product_search(query_json, ["PRODUCT_NAME", "DESCRIPTION"])

store_map = {
    "Aisle 1": {
        "Shelf 1": ["Adidas Aeroready Gym Shorts", "Adidas Climacool Workout Pants"],
        "Shelf 2": ["Adidas Ultraboost Running Shoes", "Adidas NMD_R1 Sneakers"]
    },
    "Aisle 2": {
        "Shelf 1": ["Adidas Essential Track Jacket", "Adidas ZNE Hoodie"],
        "Shelf 2": ["Adidas Alphaskin Sports Bra", "Adidas Techfit Leggings"]
    }
}
nh = NavigationHandler(store_map)
def in_store_navigation(query_json):
    return nh.in_store_navigation(query_json)

sales_agent_tools = [
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
            'parameters': {'type': 'object', 'properties': {}, 'required': []}
        }
    }
]


def transfer_to_sales():
    return sales_agent

def transfer_to_navigation():
    return navigation_agent

sales_agent = Agent(
    name="Sales Agent",
    # instructions="Be enthusiastic about selling adidas.",
    instructions=sales_system_prompt,
    functions=[product_search,transfer_to_navigation],
    functions_description = sales_agent_tools,
)

navigation_agent = Agent(
    name="Navigation Agent",
    instructions="Help the user navigate the store.",
    functions=[in_store_navigation, transfer_to_sales],
)

