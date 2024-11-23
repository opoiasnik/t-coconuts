from flask import Blueprint, request, jsonify
from app.services.openai_service import call_openai
from app.services.pdf_service import extract_text_from_pdf

# Create a Blueprint for routes
routes = Blueprint("routes", __name__)

@routes.route('/analyze', methods=['POST'])
def analyze_document():
    """
    API route to analyze a document and process it with OpenAI API.
    """
    # Get the uploaded document and instructions from the request
    file = request.files.get('document')
    instructions = request.form.get('instructions')

    # Validate that both document and instructions are provided
    if not file or not instructions:
        return jsonify({"error": "Document and instructions are required"}), 400

    try:
        # Extract text from the uploaded document (e.g., PDF)
        text = extract_text_from_pdf(file)

        # Send the extracted text and instructions to OpenAI API
        response = call_openai(text, instructions)

        # Return the OpenAI response to the user
        return jsonify({"result": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route('/', methods=['GET'])
def home():
    """
    Simple route for testing if the API is working.
    """
    return jsonify({"message": "Welcome to the Document Analysis API!"})