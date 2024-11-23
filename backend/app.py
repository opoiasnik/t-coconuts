from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.file_processing import process_file
from utils.database import save_document, get_validation_results
from models.document_validator import validate_document
import os

app = Flask(__name__)
CORS(app)  # Для разрешения запросов с фронтенда

UPLOAD_FOLDER = 'static/uploaded_docs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return jsonify({"message": "Document Validator Backend is Running!"})

# API для загрузки документа
@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Обработка файла
    results = process_file(file_path)
    save_document(file.filename, results)

    return jsonify({"message": "File uploaded and processed", "results": results}), 200

# API для валидации документа
@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    document_id = data.get('document_id')
    validation_results = validate_document(document_id)
    return jsonify(validation_results), 200

# API для получения результатов валидации
@app.route('/results/<document_id>', methods=['GET'])
def get_results(document_id):
    results = get_validation_results(document_id)
    if not results:
        return jsonify({"error": "No results found"}), 404
    return jsonify(results), 200

@app.route('/document_text/<filename>', methods=['GET'])
def get_document_text(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    results = process_file(file_path)
    if "error" in results:
        return jsonify({"error": results["error"]}), 400

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(debug=True)
