import sys
import os

# Adjust this path based on the directory structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swarm.repl.repl import run_demo_loop
from InStoreGPTs.agents import sales_agent, navigation_agent

from dotenv import load_dotenv

load_dotenv()  # Load variables from .env
openai_api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    run_demo_loop(sales_agent, debug=True)
