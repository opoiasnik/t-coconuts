from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utils.file_processing import process_file
import os
import logging
import openai
from dotenv import load_dotenv
from models import session, UserRequest  # Model for saving requests
import json
from gtts import gTTS
from datetime import datetime
from elasticsearch import Elasticsearch

# Initialize Elasticsearch connection
es = Elasticsearch(
    cloud_id="08b3dd79313b4064b845f7f3bb950f55:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRjNjhiNTI5MjhlZDk0ZjQyYjRjYTRkM2UwNWY1NzIwZCQ1MTM0YzJmOGRhMWY0Mzg3YTZmZTNiYzczYTE5MGVmMQ==",  # Replace with your Cloud ID
    basic_auth=("elastic", "EDLUByRRMXi3R4Zu5vGtO0za")  # Replace with your credentials
)

def save_to_elasticsearch(index, data):
    """
    Saves data to the specified Elasticsearch index.
    """
    try:
        response = es.index(index=index, document=data)
        return response["_id"]  # Returns the document ID
    except Exception as e:
        raise RuntimeError(f"Failed to index data in Elasticsearch: {e}")

def search_in_elasticsearch(index, query):
    """
    Searches data in the specified Elasticsearch index.
    """
    try:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["instructions", "document_text", "analysis"]
                }
            }
        }
        response = es.search(index=index, body=body)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        raise RuntimeError(f"Failed to search data in Elasticsearch: {e}")

# Load environment variables from .env file
load_dotenv()
print(f"Loaded API Key: {os.getenv('OPENAI_API_KEY')}")

# Get the OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backend.log", encoding="utf-8"),  # Logs to a file with UTF-8 encoding
        logging.StreamHandler()  # Stream output
    ]
)

app = Flask(__name__)
CORS(app)  # To allow requests from the frontend

UPLOAD_FOLDER = 'static/uploaded_docs'
TEMP_FOLDER = 'static/temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER

# Variable for temporarily storing changes
temp_changes = {}

@app.route('/')
def home():
    logging.info("Home endpoint was accessed.")
    return jsonify({"message": "Document Validator Backend is Running!"})

def save_request_to_db(endpoint, request_data, response_data):
    """
    Saves the request and response to the database.
    """
    try:
        log_entry = UserRequest(
            endpoint=endpoint,
            request_data=json.dumps(request_data),  # Convert to JSON string
            response_data=json.dumps(response_data),  # Convert to JSON string
        )
        session.add(log_entry)
        session.commit()
        logging.info("Request successfully saved to the database.")
    except Exception as e:
        logging.error(f"Failed to save request to the database: {e}")
        session.rollback()

# API for uploading a document
@app.route('/upload', methods=['POST'])
def upload_document():
    logging.info("Upload endpoint was accessed.")
    if 'file' not in request.files:
        logging.error("No file was uploaded.")
        response = {"error": "No file uploaded"}
        save_request_to_db('/upload', {}, response)
        return jsonify(response), 400
    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected for upload.")
        response = {"error": "No selected file"}
        save_request_to_db('/upload', {}, response)
        return jsonify(response), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    logging.info(f"Saving file to {file_path}.")
    file.save(file_path)

    try:
        logging.info(f"Processing file {file_path}.")
        results = process_file(file_path)
        
        if "text" in results:
            logging.info(f"Processing successful. Extracted text: {results['text'][:500]}...")
        else:
            logging.error(f"Processing failed. Error: {results.get('error')}")

        response = {"message": "File uploaded and processed", "results": results}
        save_request_to_db('/upload', {"file_name": file.filename}, response)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        response = {"error": "Failed to process file"}
        save_request_to_db('/upload', {"file_name": file.filename}, response)
        return jsonify(response), 500

# Function to parse the 'Explanation' section and extract reused elements
def parse_reused_elements(explanation):
    """
    Parses the 'Explanation' section and extracts details about reused elements.
    Returns a list of dictionaries with keys 'content', 'origin', and 'application'.
    """
    reused_elements = []
    lines = explanation.splitlines()
    in_reused_section = False
    current_element = {}
    for line in lines:
        line = line.strip()
        if line.lower().startswith("detailed list of reused elements"):
            in_reused_section = True
            continue
        elif in_reused_section and line == '':
            # Empty line may indicate the end of the section
            if current_element:
                reused_elements.append(current_element)
                current_element = {}
            in_reused_section = False
            continue
        if in_reused_section:
            if line.lower().startswith("no information was reused from previous operations"):
                # Explicit indication that no information was reused
                in_reused_section = False
                break
            elif line.startswith("- Exact content reused:"):
                if current_element:
                    reused_elements.append(current_element)
                    current_element = {}
                current_element['content'] = line.replace("- Exact content reused:", "").strip()
            elif line.startswith("- Origin (which previous operation):"):
                current_element['origin'] = line.replace("- Origin (which previous operation):", "").strip()
            elif line.startswith("- How it was applied:"):
                current_element['application'] = line.replace("- How it was applied:", "").strip()
    if current_element:
        reused_elements.append(current_element)
    return reused_elements

# API for prompt processing
@app.route('/process_prompt', methods=['POST'])
def process_prompt():
    """
    Process the prompt by analyzing and improving specific parts of the document based on instructions,
    including information from past operations if relevant.
    """
    global temp_changes
    logging.info("Processing prompt endpoint was accessed.")
    data = request.json

    # Get user instructions and document text
    instructions = data.get('instructions', '').strip()
    document_text = data.get('document_text', '').strip()

    logging.info(f"Received instructions: {instructions}")
    logging.info(f"Received document text (first 500 chars): {document_text[:500]}...")

    if not instructions:
        logging.error("No instructions provided.")
        response = {"error": "Instructions are required."}
        save_request_to_db('/process_prompt', data, response)
        return jsonify(response), 400

    if not document_text:
        logging.error("No document text provided.")
        response = {"error": "Document text is required."}
        save_request_to_db('/process_prompt', data, response)
        return jsonify(response), 400

    try:
        # Fetch related data from Elasticsearch
        logging.info("Searching for related past operations in Elasticsearch.")
        past_responses = search_in_elasticsearch("user_requests", instructions)

        # Build context with previous responses
        previous_info = ""
        if past_responses:
            logging.info("Details of found past operations:")
            for i, response in enumerate(past_responses, 1):
                previous_info += f"Previous Operation {i}:\n"
                previous_info += f"Instructions: {response.get('instructions', 'N/A')}\n"
                previous_info += f"Analysis: {response.get('analysis', 'N/A')}\n\n"
                logging.info(f"Operation {i} Instructions: {response.get('instructions', 'N/A')}")
                logging.info(f"Operation {i} Analysis: {response.get('analysis', 'N/A')[:500]}...")

        logging.info(f"Found {len(past_responses)} related past operations.")

        # Prompt instructions for OpenAI API
        prompt_instructions = (
            f"Using the following instructions:\n\n{instructions}\n\n"
            "Please analyze the document below and make improvements specifically "
            "based on the instructions provided. This includes:\n"
            "1. Adding any missing or necessary information.\n"
            "2. Removing redundant or unnecessary information.\n"
            "3. Rephrasing unclear or overly complex sentences to improve readability.\n"
            "4. Keeping unchanged parts of the document intact if they do not require any updates.\n\n"
            "Consider the following previous operations if relevant:\n\n"
            f"{previous_info}\n\n"
            "**Important:** If any information from past operations is reused, you must specify clearly:\n"
            "1. **Exact elements reused**: List the specific phrases, sentences, or ideas taken from previous operations.\n"
            "2. **Origin of elements**: Indicate from which specific operation each element was taken.\n"
            "3. **Application in current analysis**: Explain how each element was applied in the current document.\n\n"
            "At the end of the modified document, provide a detailed explanation of the changes made, structured as follows:\n"
            "1. **Summary of new changes**: Briefly summarize the improvements made.\n"
            "2. **Detailed List of Reused Elements**: For each reused element, provide its exact content, origin, and how it was used.\n"
            "   - If no information was reused from previous operations, state explicitly: 'No information was reused from previous operations.'\n\n"
            "Ensure that you include the section 'Detailed List of Reused Elements' in your explanation, even if it states that no information was reused.\n\n"
            f"Document:\n{document_text}\n\n"
            "**Output format:**\n"
            "1. **Updated Document Content**\n"
            "2. **Explanation of Changes** (prefixed with 'Explanation:')\n"
            "   - **Summary of New Changes**\n"
            "   - **Detailed List of Reused Elements**\n"
            "     - For each element:\n"
            "       - Exact content reused\n"
            "       - Origin (which previous operation)\n"
            "       - How it was applied\n"
        )

        # Send data to OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a text improvement assistant."},
                {"role": "user", "content": prompt_instructions},
            ],
            max_tokens=2000,
            temperature=0.5,
        )
        analysis = response.choices[0].message["content"]
        logging.info(f"Analysis completed (first 500 chars): {analysis[:500]}...")

        # Split the analysis into document content and explanation
        if "Explanation:" in analysis:
            content, explanation = analysis.split("Explanation:", 1)
            content = content.strip()
            explanation = explanation.strip()
        else:
            content = analysis.strip()
            explanation = "No explanation provided by the model."

        # Log the full explanation
        logging.info(f"Full explanation:\n{explanation}")

        # Parse the explanation to extract reused elements
        reused_elements = parse_reused_elements(explanation)

        # Log details of reused elements
        if reused_elements:
            logging.info("Reused elements from past operations:")
            for element in reused_elements:
                logging.info(f"Content reused: {element['content']}")
                logging.info(f"Origin: {element['origin']}")
                logging.info(f"Application: {element['application']}")
        else:
            logging.info("No reused elements from past operations.")

        # Save changes to temp_changes
        temp_changes = {
            "instructions": instructions,
            "document_text": document_text,
            "analysis": content,
            "explanation": explanation,
        }

        response_data = {"message": "Prompt processed successfully", "analysis": content, "explanation": explanation}
        save_request_to_db('/process_prompt', data, response_data)

        # Save the request and response to Elasticsearch
        data_to_save = {
            "instructions": instructions,
            "document_text": document_text,
            "analysis": content,
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat()
        }
        save_to_elasticsearch("user_requests", data_to_save)

        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"Error during prompt processing: {e}")
        response = {"error": "Failed to process prompt"}
        save_request_to_db('/process_prompt', data, response)
        return jsonify(response), 500

# API for speaking changes
@app.route('/speak_changes', methods=['GET'])
def speak_changes():
    """
    Speaks the latest changes.
    """
    global temp_changes
    if not temp_changes:
        return jsonify({"error": "No changes available for speaking."}), 400

    # Text to speak (explanation of changes)
    text_to_speak = temp_changes.get('explanation', 'No explanation available.')
    audio_path = os.path.join(app.config['TEMP_FOLDER'], 'output.mp3')

    try:
        # Use gTTS for speech synthesis
        tts = gTTS(text=text_to_speak, lang='en')  # Choose language, e.g., 'en' for English
        tts.save(audio_path)

        return send_file(audio_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Error during speech synthesis with gTTS: {e}")
        return jsonify({"error": "Failed to generate speech."}), 500

@app.route('/save_to_elasticsearch', methods=['POST'])
def save_to_elasticsearch_endpoint():
    """
    Saves data to Elasticsearch.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        data["timestamp"] = datetime.utcnow().isoformat()  # Add a timestamp
        document_id = save_to_elasticsearch("user_requests", data)
        return jsonify({"message": "Data saved successfully", "document_id": document_id}), 200
    except RuntimeError as e:
        logging.error(f"Error saving to Elasticsearch: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search_in_elasticsearch', methods=['POST'])
def search_in_elasticsearch_endpoint():
    """
    Searches data in Elasticsearch.
    """
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        results = search_in_elasticsearch("user_requests", query)
        return jsonify({"results": results}), 200
    except RuntimeError as e:
        logging.error(f"Error searching in Elasticsearch: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_explanation', methods=['GET'])
def get_explanation():
    """
    Returns the explanation text.
    """
    global temp_changes
    if not temp_changes or 'explanation' not in temp_changes:
        return jsonify({"error": "No explanation available"}), 400

    return jsonify({"explanation": temp_changes['explanation']}), 200

if __name__ == '__main__':
    logging.info("Starting Flask application.")
    app.run(debug=True)
