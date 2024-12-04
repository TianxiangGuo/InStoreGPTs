import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import base64

load_dotenv()

from flask import jsonify

#TODO: refer to https://cookbook.openai.com/examples/tag_caption_images_with_gpt4v
#TODO: optimize vectorization(e.g. pandas dataframe loading)

class ImageHandler:
    _openai_api_key: str = os.environ.get("OPENAI_API_KEY", None)
    _openai_model: str = "gpt-4o-mini"
    client = OpenAI()

    def __init__(self, csv_file, upload_folder, system_prompt=None):
        """
        Initialize the ImageHandler with an upload folder and a system prompt.
        """
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)
        if system_prompt is None:
            self.system_prompt = """You are an agent specialized in tagging images with relevant keywords that could be used to search for these items on a marketplace.
You will be provided with an image of the item, and your goal is to extract keywords for the item. 
Keywords should be concise and in lower case."""
        else:
            self.system_prompt = system_prompt
        self.df = pd.read_csv(csv_file)

    def save_image(self, image_file):
        """
        Save the uploaded image to the upload folder.
        """
        if not image_file:
            return None, "No image uploaded"

        filename = secure_filename(image_file.filename)
        if filename == "":
            return None, "No selected file"

        filepath = os.path.join(self.upload_folder, filename)
        image_file.save(filepath)
        return filepath, None

    def generate_caption(self, image_path):
        """
        Generate a caption for the image using GPT-4-o-mini.
        """
        base64_image = self.encode_image(image_path)
        if not base64_image:
            return None, "Failed to generate image URL"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url":  f"data:image/jpeg;base64,{base64_image}"}}]},
                ],
                max_tokens=300,
                top_p=0.1
            )
            caption = response.choices[0].message.content
            return caption, None
        except Exception as e:
            return None, f"Error generating caption: {str(e)}"

    # Function to encode the image
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def reverse_image_search(self, caption, caption_column="IMAGE_CAPTION", top_n=5):
        """
        Perform reverse image search based on the generated caption.

        Args:
            caption (str): The generated image caption to search for.
            caption_column (str): Name of the column in the DataFrame with captions.
            top_n (int): Number of most similar results to return.

        Returns:
            pd.DataFrame: DataFrame with the top N most similar captions and their similarity scores.
        """
        if caption_column not in self.df.columns:
            raise ValueError(f"Column '{caption_column}' not found in the DataFrame.")

        try:
            # Vectorize captions using TF-IDF
            # Replace missing captions with a default value
            self.df["IMAGE_CAPTION"].fillna("No caption available", inplace=True)
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(self.df["IMAGE_CAPTION"])

            # Vectorize the input caption
            input_vector = vectorizer.transform([caption])

            # Compute cosine similarity
            similarities = cosine_similarity(input_vector, tfidf_matrix).flatten()

            # Get top N matches
            top_indices = similarities.argsort()[-top_n:][::-1]
            results = self.df.iloc[top_indices]

            return results, None
        except Exception as e:
            return None, f"Error during reverse image search: {str(e)}"
