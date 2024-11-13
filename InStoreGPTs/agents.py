import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# print(sys.path)
from swarm import Agent
from typing import Optional, List, Dict, Union
from InStoreGPTs.services.product_handler import ProductHandler
from InStoreGPTs.services.navigation_handler import NavigationHandler
import json

adidas_products_csv = 'example_data/adidas/adidas_products.csv'
ph = ProductHandler(adidas_products_csv)
def product_search(query_json):
    return ph.product_search(query_json, ["PRODUCT_NAME", "DESCRIPTION"])


store_map = json.load(open('example_data/adidas/adidas_map.json'))
nh = NavigationHandler(store_map)
# def in_store_navigation(query_json):
#     return nh.in_store_navigation(query_json)


def transfer_to_sales(summary):
    return Agent(
                name="Sales Agent",
                instructions=ph.system_prompt,
                functions=[product_search,transfer_to_navigation],
                functions_description = ph._tools,
            )

def transfer_to_navigation(summary):
    return Agent(
                name="Navigation Agent",
                instructions=nh.system_prompt,
                functions=[transfer_to_sales],
            )

sales_agent = Agent(
    name="Sales Agent",
    instructions=ph.system_prompt,
    functions=[product_search,transfer_to_navigation],
    functions_description = ph._tools,
)

navigation_agent = Agent(
    name="Navigation Agent",
    instructions=nh.system_prompt,
    functions=[transfer_to_sales],
)

