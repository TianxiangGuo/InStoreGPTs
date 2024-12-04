from flask import Flask, request, jsonify, render_template
import sys
import os

# Adjust this path based on the directory structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from swarm.repl.repl import run_demo_loop
from InStoreGPTs.agents import sales_agent, navigation_agent
from werkzeug.utils import secure_filename

from swarm import Swarm  
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize Swarm client
swarm_client = Swarm()
current_agent = sales_agent  # Default starting agent
chat_history = []  # List to store chat messages for session
welcome_message = "Hello! How can I help you today?"
chat_history.append({"role": "assistant", "content": welcome_message})

def process_message(user_input):
    """
    Process user input using the current Swarm agent.
    """
    global current_agent, chat_history

    # Add the user message to chat history
    chat_history.append({"role": "user", "content": user_input})

    # Run the Swarm agent
    response = swarm_client.run(
        agent=current_agent,
        messages=chat_history,
        context_variables={},
        stream=False,  # Adjust based on your backend
        debug=True,
    )

    # Update chat history and agent if changed
    chat_history.extend(response.messages)
    current_agent = response.agent

    current_agent = response.agent  # Update current agent based on the response

    # Extract and return the last response along with the active agent
    return {
        "response": response.messages[-1]["content"],
        "agent": "sales" if current_agent == sales_agent else "navigation"
    }

# Directory to save uploaded images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload_image():
    """
    Handle image uploads from the frontend.
    """
    if "image" not in request.files:
        return "No image uploaded", 400

    file = request.files["image"]
    if file.filename == "":
        return "No selected file", 400

    # Save the file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Return a success message or process the image further
    return f"Image uploaded successfully: {filename}", 200

@app.route("/")
def index():
    """
    Render the chatbot interface.
    """
    return render_template("index.html")

@app.route("/get", methods=["GET"])
def get_bot_response():
    """
    Handle the bot response for user input.
    """
    user_input = request.args.get('msg')
    if user_input:
        bot_response = process_message(user_input)
        return jsonify(bot_response)
    return jsonify("I didn't catch that. Can you try again?")

if __name__ == "__main__":
    app.run(debug=True)
