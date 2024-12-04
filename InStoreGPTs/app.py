from flask import Flask, request, jsonify, render_template
import sys
import os

# Adjust this path based on the directory structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from swarm.repl.repl import run_demo_loop
from InStoreGPTs.agents import sales_agent, navigation_agent
from werkzeug.utils import secure_filename
from InStoreGPTs.services.image_handler import ImageHandler

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

def process_message(user_input, additional_messages=None):
    """
    Process user input using the current Swarm agent, optionally including additional messages.
    """
    global current_agent, chat_history

    # Add the user message to chat history
    chat_history.append({"role": "user", "content": user_input})

    # Include additional messages (e.g., from image processing) if provided
    if additional_messages:
        chat_history.extend(additional_messages)

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

    # Extract and return the last response along with the active agent
    return {
        "response": response.messages[-1]["content"],
        "agent": "sales" if current_agent == sales_agent else "navigation"
    }


# Directory to save uploaded images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
image_handler = ImageHandler(csv_file=r'example_data\adidas\adidas_products.csv',upload_folder=UPLOAD_FOLDER)

#TODO: display image on chat
#TODO: add recmoondations to chat
@app.route("/upload", methods=["POST"])
def upload_image():
    """
    Handle image uploads, generate captions, perform reverse search, and integrate results with sales agent.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    filepath, error = image_handler.save_image(image_file)
    if error:
        return jsonify({"error": error}), 400

    # Generate caption for the image
    caption, error = image_handler.generate_caption(filepath)
    if error:
        return jsonify({"error": error}), 500

    # Perform reverse image search using the caption
    search_results, error = image_handler.reverse_image_search(caption)
    if error:
        return jsonify({"error": error}), 500

    # Format search results for chat history
    recommendations = []
    for _, row in search_results.iterrows():
        recommendations.append(f"Product: {row['PRODUCT_NAME']}, Details: {row.get('DETAILS', '')}")

    # Add results to chat history for sales agent
    additional_messages = [
        {"role": "assistant", "content": f"Image processed. Caption: {caption}"},
        {"role": "assistant", "content": "Here are some recommended products:\n" + "\n".join(recommendations)},
    ]

    # Pass the caption and recommendations to the sales agent
    response = process_message("Image uploaded", additional_messages)

    return jsonify({
        "caption": caption,
        "recommendations": recommendations,
        "agent_response": response["response"]
    }), 200


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
