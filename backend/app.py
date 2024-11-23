from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.file_processing import process_file
import os
import logging
import speech_recognition as sr  # Для распознавания речи
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        
        # Логируем результат обработки
        if "text" in results:
            logging.info(f"Processing successful. Extracted text: {results['text'][:500]}...")
        else:
            logging.error(f"Processing failed. Error: {results.get('error')}")

        logging.info(f"File processed successfully. Results: {results}")
    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        return jsonify({"error": "Failed to process file"}), 500

    return jsonify({"message": "File uploaded and processed", "results": results}), 200

# API для преобразования речи в текст (Speech-to-Text)
@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    logging.info("Speech-to-Text endpoint was accessed.")
    if 'file' not in request.files:
        logging.error("No audio file was uploaded.")
        return jsonify({"error": "No audio file uploaded"}), 400
    audio_file = request.files['file']
    if audio_file.filename == '':
        logging.error("No audio file selected for upload.")
        return jsonify({"error": "No selected audio file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
    logging.info(f"Saving audio file to {file_path}.")
    audio_file.save(file_path)

    try:
        # Распознавание речи
        logging.info(f"Processing audio file: {file_path}")
        recognizer = sr.Recognizer()
        audio = sr.AudioFile(file_path)
        with audio as source:
            recognizer.adjust_for_ambient_noise(source)  # Настройка на шум
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)  # Используем Google Speech API
        logging.info(f"Speech successfully converted to text: {text}")
        return jsonify({"message": "Speech converted to text successfully", "text": text}), 200
    except Exception as e:
        logging.error(f"Error during speech recognition: {e}")
        return jsonify({"error": "Failed to process speech"}), 500

# API для обработки промта
@app.route('/process_prompt', methods=['POST'])
def process_prompt():
    """
    Обработка промта с документом и инструкциями, отправленными с фронтенда.
    """
    logging.info("Processing prompt endpoint was accessed.")
    data = request.json

    # Получаем текстовый ввод и текст документа
    instructions = data.get('instructions', '').strip()
    document_text = data.get('document_text', '').strip()

    logging.info(f"Received instructions: {instructions}")
    logging.info(f"Received document text (first 500 chars): {document_text[:500]}...")

    if not instructions:
        logging.error("No instructions provided.")
        return jsonify({"error": "Instructions are required."}), 400

    if not document_text:
        logging.error("No document text provided.")
        return jsonify({"error": "Document text is required."}), 400

    try:
        logging.info("Sending prompt and document text to OpenAI for analysis.")
        # Отправляем данные в OpenAI API для анализа
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": document_text},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        analysis = response.choices[0].message["content"]
        logging.info(f"Analysis completed: {analysis[:500]}...")

        return jsonify({"message": "Prompt processed successfully", "analysis": analysis}), 200

    except Exception as e:
        logging.error(f"Error during prompt processing: {e}")
        return jsonify({"error": "Failed to process prompt"}), 500

if __name__ == '__main__':
    logging.info("Starting Flask application.")
    app.run(debug=True)
