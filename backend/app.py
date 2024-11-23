from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.file_processing import process_file
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат записи
    handlers=[
        logging.FileHandler("backend.log"),  # Запись в файл
        logging.StreamHandler()  # Запись в консоль
    ]
)

app = Flask(__name__)
CORS(app)  # Для разрешения запросов с фронтенда

UPLOAD_FOLDER = 'static/uploaded_docs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    logging.info("Home endpoint was accessed.")
    return jsonify({"message": "Document Validator Backend is Running!"})

# API для загрузки документа
@app.route('/upload', methods=['POST'])
def upload_document():
    logging.info("Upload endpoint was accessed.")
    if 'file' not in request.files:
        logging.error("No file was uploaded.")
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected for upload.")
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    logging.info(f"Saving file to {file_path}.")
    file.save(file_path)

    # Обработка файла
    try:
        logging.info(f"Processing file {file_path}.")
        results = process_file(file_path)
        logging.info(f"File processed successfully. Results: {results}")
    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        return jsonify({"error": "Failed to process file"}), 500

    return jsonify({"message": "File uploaded and processed", "results": results}), 200

@app.route('/document_text/<filename>', methods=['GET'])
def get_document_text(filename):
    logging.info(f"Document text endpoint was accessed for file: {filename}.")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        logging.error(f"File not found: {filename}.")
        return jsonify({"error": "File not found"}), 404

    try:
        logging.info(f"Processing text from file: {file_path}.")
        results = process_file(file_path)
        if "error" in results:
            logging.error(f"Error in file processing: {results['error']}")
            return jsonify({"error": results["error"]}), 400
        logging.info(f"Successfully processed text for file: {filename}.")
        return jsonify(results), 200
    except Exception as e:
        logging.error(f"Error during text extraction: {e}")
        return jsonify({"error": "Failed to extract text"}), 500

if __name__ == '__main__':
    logging.info("Starting Flask application.")
    app.run(debug=True)
