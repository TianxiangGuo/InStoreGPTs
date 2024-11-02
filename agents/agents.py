from swarm import Agent
from typing import Optional, List, Dict, Union

def product_search(
    product_name: str = None,
    category_name: str = None,
    description: str = None,
    price: List[float] = None,
    discount: bool = None,
    in_store_location: str = None
) -> List[Dict[str, Union[str, int, float, bool]]]:
    """
    Searches for products based on given criteria.
    """
    print(f"[mock] Searching for product {product_name}...")
    return f"Found product {product_name}!"

def in_store_navigation(location):
    """Help the user navigate the store."""
    print("[mock] Navigating the store...")
    return "Navigating the store..."

sales_agent_tools = [
    {
        'type': 'function', 
        'function': {
            'name': 'product_search', 
            'description': 'Searches for products based on given criteria.', 
            'parameters': {
                'type': 'object', 
                'properties': {
                    'product_name': {'type': 'string'}, 
                    'category_name': {'type': 'string'}, 
                    'description': {'type': 'string'}, 
                    'price': {'type': 'string'}, 
                    'discount': {'type': 'boolean'}, 
                    'in_store_location': {'type': 'string'}
                }, 
            'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'transfer_to_navigation',
            'description': 'Help the user navigate the store.',
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
    instructions="Be enthusiastic about selling adidas.",
    functions=[product_search,transfer_to_navigation],
    functions_description = sales_agent_tools,
)

navigation_agent = Agent(
    name="Navigation Agent",
    instructions="Help the user navigate the store.",
    functions=[in_store_navigation, transfer_to_sales],
)

