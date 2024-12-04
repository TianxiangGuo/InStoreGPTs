from openai import OpenAI
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from swarm import Swarm
from dotenv import load_dotenv
# from swarm.repl.repl import process_and_print_streaming_response, pretty_print_messages
import json
load_dotenv()
customer_client = OpenAI()

from InStoreGPTs.agents import sales_agent

# Mock Customer Function: Generates input based on the current system state
def generate_mock_customer_query(chat_history):

    # Use OpenAI API to generate the next query
    response = customer_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_history,
    )
    return response.choices[0].message.content

def get_system_prompt(query):
    return f"""
    You are a customer testing an adidas in-store assistant system.
    Your goal is to evaluate its response in a multi-step interaction.

    ### Query:
    {query}

    Continue the conversation naturally based on the system's responses.
    If you acheive the goal, you can say "End Conversation" to end.
    Start the conversation by greeting asking for help.
    """

def get_evaluation_prompt(query, chat_history):
    return f"""
You are a customer testing an in-store assistant system. Evaluate its response to your query and navigation guidance.

### Query:
{query}

### Chat History:
{chat_history}

### Feedback Instructions:
1. Rate the following on a scale of 1 to 5:
    - **Clarity:** Was the response clear and easy to understand?
    - **Effort:** Was the interaction efficient and required minimal effort?
    - **Navigation:** If navigation was involved, was the guidance easy to follow and accurate?
2. Provide an overall satisfaction rating (1 = Very Dissatisfied, 5 = Very Satisfied).
3. Suggest improvements if the response was unclear, inaccurate, or inefficient.

### Respond in this format:
### Customer Feedback:
- **Clarity:** [1-5]
- **Effort:** [1-5]
- **Navigation:** [1-5]

### Overall Satisfaction:
[1-5]

### Suggestions for Improvement:
[Your feedback here]
    """

# Test Scenario: Multi-Round Interaction Test
def test_mock_customer_with_system_multi_round(query):
    # Define the initial query
    system_prompt = get_system_prompt(query)

    # Initialize the mock customer and system conversation
    user_chat_history = [
                    {"role": "system", "content": system_prompt},
                ]

    def run_demo_loop_with_mock(starting_agent, max_rounds=10, context_variables=None, stream=False, debug=False):
        client = Swarm()
        print("Starting Test:", query)

        agent = starting_agent
        messages = []

        # Begin multi-round conversation loop
        for round_num in range(max_rounds):
            # Generate the customer query
            user_input = generate_mock_customer_query(user_chat_history)

            print(f"\033[93m[Mock Customer - Round {round_num + 1}]\033[0m: {user_input}")

            # Add the user input to the  chat history
            messages.append({"role": "user", "content": user_input})
            user_chat_history.append({"role": "assistant", "content": user_input})

            if "End Conversation" in user_input:
                print("\033[94m[Conversation Ended]\033[0m")
                return user_chat_history, (round_num + 1)
            
            # Run the system with the mock input
            response = client.run(
                agent=agent,
                messages=messages,
                context_variables=context_variables or {},
                stream=stream,
                debug=debug,
            )

            # Log the system response for analysis
            messages.extend(response.messages)
            system_response = response.messages[-1]["content"]
            user_chat_history.append({"role": "user", "content": system_response})
            print(f"\033[92m[System Response - Round {round_num + 1}]\033[0m: {system_response}")
        
        return user_chat_history, max_rounds


    # Start the test
    return run_demo_loop_with_mock(sales_agent)


# Directory to store user chat history files
output_dir = "tests/mock_customer_output"
os.makedirs(output_dir, exist_ok=True)

# Function to evaluate mock customer tests
def evaluate_mock_customer_test(query, test_run, scenario_name):
    user_chat_history, rounds = test_mock_customer_with_system_multi_round(query)
    evaluation_prompt = get_evaluation_prompt(query, user_chat_history[1:])
    response = customer_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": evaluation_prompt},
        ],
    )
    evaluation_result = response.choices[0].message.content
    # Save user chat history to a file
    chat_history_filename = os.path.join(output_dir, f"{scenario_name}_run_{test_run}.json")
    with open(chat_history_filename, "w") as chat_file:
        json.dump({"user_chat_history": user_chat_history, "rounds": rounds, "result":evaluation_result}, chat_file, indent=4)
    
    return evaluation_result, chat_history_filename

def read_mock_customer_test(chat_history_file):
    """
    Reads user_chat_history and rounds from a saved JSON file.
    """
    try:
        with open(chat_history_file, "r") as file:
            data = json.load(file)
            user_chat_history = data.get("user_chat_history", [])
            rounds = data.get("rounds", 0)
            return user_chat_history, rounds
    except FileNotFoundError:
        print(f"Error: File not found - {chat_history_file}")
        return None, None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON file - {chat_history_file}")
        return None, None

def generate_evaluation_results(chat_history_file, query):
    """
    Generates evaluation results using saved user_chat_history
    """
    # Read user_chat_history and rounds from file
    user_chat_history, rounds = read_mock_customer_test(chat_history_file)
    
    if user_chat_history is None or rounds is None:
        print(f"Skipping evaluation for {chat_history_file} due to missing data.")
        return None

    # Generate evaluation prompt
    evaluation_prompt = get_evaluation_prompt(query, user_chat_history[1:])

    # Call customer_client to generate evaluation result
    response = customer_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": evaluation_prompt},
        ],
    )
    evaluation_result = response.choices[0].message.content

    return evaluation_result

# Run the test
if __name__ == "__main__":
    # query = "Find an Adidas Ultraboost 21 running shoe in black, size 10."
    scenarios = [
        {
            "name": "Highly Specific Need",
            "query": "Find an Adidas Ultraboost 22 running shoe in black, size 10."
        },
        {
            "name": "Specific with Variability",
            "query": "Show me Adidas hoodies in medium size, any color."
        },
        {
            "name": "Functional Requirement",
            "query": "I need shoes for basketball under $100."
        },
        {
            "name": "General Product Search",
            "query": "What are the best-selling Adidas T-shirts?"
        },
        {
            "name": "Category Navigation",
            "query": "Take me to the Adidas shoe section."
        }
    ]
    ## ==========Running all tests================
    # results = []
    # for scenario in scenarios:
    #     for i in range(3):  # Test each scenario 3 times
    #         try:
    #             response, chat_history_file = evaluate_mock_customer_test(scenario["query"], i + 1, scenario["name"])
    #             results.append({
    #                 "scenario": scenario["name"],
    #                 "query": scenario["query"],
    #                 "test_run": i + 1,
    #                 "evaluation": response,
    #                 "chat_history_file": chat_history_file
    #             })
    #             print(f"Test {i+1} for {scenario['name']} completed. Chat history saved to {chat_history_file}.")
    #         except Exception as e:
    #             print(f"Error during test {i+1} for {scenario['name']}: {e}")

    ## ==========Rerun one scenerio================
    # scenario = scenarios[2]
    # for i in range(3):  # Test each scenario 3 times
    #     try:
    #         response, chat_history_file = evaluate_mock_customer_test(scenario["query"], i + 1, scenario["name"])
    #         print(f"Test {i+1} for {scenario['name']} completed. Chat history saved to {chat_history_file}.")
    #     except Exception as e:
    #         print(f"Error during test {i+1} for {scenario['name']}: {e}")

    ## ==========Run evaluation based on mock chat histories================
    input_dir = "example_test_runs/mock_customer_output"
    output_file = "example_test_runs/mock_customer_evaluation_results.json"
    # Ensure the output file starts clean
    with open(output_file, "w") as f:
        f.write("[\n")  # Start of JSON array

    # Process files
    for scenario in scenarios:
        scenario_name = scenario["name"]
        for test_run in range(1, 4):  # Assuming 3 test runs per scenario
            chat_history_file = os.path.join(input_dir, f"{scenario_name}_run_{test_run}.json")
            
            if not os.path.exists(chat_history_file):
                print(f"File not found: {chat_history_file}. Skipping.")
                continue  # Skip if the file doesn't exist
            
            try:
                # Generate evaluation result
                evaluation_result = generate_evaluation_results(chat_history_file, scenario["query"])
                
                # Append the result to the output file
                if evaluation_result:
                    result_data = {
                        "scenario": scenario_name,
                        "test_run": test_run,
                        "chat_history_file": chat_history_file,
                        "evaluation_result": evaluation_result
                    }
                    with open(output_file, "a") as f:
                        f.write(json.dumps(result_data, indent=4) + ",\n")
                    print(f"Evaluation for {scenario_name} run {test_run} completed.")
            except Exception as e:
                print(f"Error processing {scenario_name} run {test_run}: {e}")

    # Finalize JSON array in the output file
    with open(output_file, "a") as f:
        f.write("\n]")
