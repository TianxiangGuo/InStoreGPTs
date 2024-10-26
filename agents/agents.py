from swarm import Agent

def product_search(product_features):
    """Search for products."""
    print(f"[mock] Searching for product {product_features}...")
    return f"Found product {product_features}!"

def in_store_navigation(location):
    """Help the user navigate the store."""
    print("[mock] Navigating the store...")
    return "Navigating the store..."

sales_agent = Agent(
    name="Sales Agent",
    instructions="Be enthusiastic about selling adidas.",
    functions=[product_search],
)

navigation_agent = Agent(
    name="Navigation Agent",
    instructions="Help the user navigate the website.",
    functions=[in_store_navigation],
)


def transfer_to_sales():
    return sales_agent

def transfer_to_navigation():
    return navigation_agent

sales_agent.functions.append(transfer_to_navigation)
navigation_agent.functions.append(transfer_to_sales)