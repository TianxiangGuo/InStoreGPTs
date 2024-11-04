# InStoreGPTs

InStoreGPTs is a prototype for an LLM-based in-store assistant designed to help users navigate, discover, and interact with in-store products seamlessly. This project leverages multi-agent systems for handling product recommendations, navigation, and user queries in a dynamic retail environment.

## Overview

The main objective of InStoreGPTs is to bridge the gap between physical and digital retail experiences by providing an AI-driven, conversational in-store assistant. Unlike typical e-commerce solutions, InStoreGPTs focuses on enhancing in-person shopping with advanced machine learning and NLP capabilities.

## Features

- **Multi-agent Architecture**: InStoreGPTs uses multiple agents to handle different tasks, including product recommendations and navigation.
- **Customizable Interactions**: The assistant can be tailored by store owners to match different interaction styles.
- **Data Handling**: Supports integration with product data from various formats (e.g., CSV files).
- **Guardrails for Safety**: Includes content filtering to ensure a safe and reliable user experience.

## Project Structure

```
├─example_data 
│      adidas.csv
│      grocery.csv
│      hardware.csv
│
├─InStoreGPTs
│  │  agents.py            # Main file containing agent logic
│  │  prompts.py           # Predefined prompts used by the agents
│  │  README.md            # Project documentation
│  │  run.py               # Script to run the main application
│  │  __init__.py
│  │
│  ├─services
│  │  │  llm_handler.py        # Handles interactions with the LLMs
│  │  │  navigation_handler.py # Manages navigation-related tasks
│  │  │  product_handler.py    # Deals with product recommendation logic
│  │  │  __init__.py
│  │  │
│  │  ├─guardrails
│  │  │      guardrails.py         # Ensures safety and content standards
│  │  │      words_to_be_filtered.py # Contains words to filter out
│  │  │      __init__.py
│
├─local_scripts
│      test.py              # Local script for testing
│
├─swarm
│  │  core.py               # Core functionalities of the multi-agent system
│  │  types.py              # Data type definitions
│  │  util.py               # Utility functions
│  │  __init__.py
│  │
│  ├─repl
│  │  │  repl.py            # REPL for interacting with agents
│  │  │  __init__.py
│  │
└─tests
    │  evals_util.py        # Utility functions for testing
    │  test_product_handler.py # Unit tests for product handler
    │  test_sales_agent.py  # Unit tests for sales agent
    │  __init__.py
```

## Progress and To-Do List

### 1. Backend

#### 1.1 Sales Agent
- **Product Search**:
   [x] Keyword search
   [x] Price filtering & discount filtering
   [ ] Embeddings search & ranking
   [ ] Add image search: use an LLM to caption the image, extract key information, then use the existing product search logic.

#### 1.2 Navigation Agent
   [ ] Implement image store map + user text description for localization. Use a multi-modal LLM to guide the user.

#### 1.3 Transfer
   [x] Agents handoff to each other.

#### 1.4 Database
   [x] Currently reads CSV files into a pandas DataFrame. 
   [ ] Consider databases improvements for scalability.

### 2. Frontend
   [ ] Implement either a mobile app or web app, whichever is easier.

## Getting Started

### Prerequisites

- Python 3.11+
- Required Python packages (specified in `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/TianxiangGuo/InStoreGPTs.git
   cd InStoreGPTs
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Project

To start the application, run:
```bash
python InStoreGPTs/run.py
```

### Example Data

The `example_data` directory contains sample CSV files:
- **adidas.csv**: Product data for Adidas items.
- **grocery.csv**: Data for grocery items.
- **hardware.csv**: Data for computer hardware.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- **OpenAI** for their open-sourced `Swarm` framework.
- **RetailGPT** for inspiring the direction and design of this project.