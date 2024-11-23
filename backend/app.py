from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.file_processing import process_file
import os
import logging
import speech_recognition as sr  # Для распознавания речи
import openai
from dotenv import load_dotenv
from models import session, UserRequest  # Подключение модели для сохранения запросов
import json

# Load environment variables from .env file
load_dotenv()
print(f"Loaded API Key: {os.getenv('OPENAI_API_KEY')}")


# Get the OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backend.log", encoding="utf-8"),  # Логи в файл с UTF-8
        logging.StreamHandler()  # Потоковый вывод
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


def save_request_to_db(endpoint, request_data, response_data):
    """
    Сохраняет запрос и ответ в базу данных.
    """
    try:
        log_entry = UserRequest(
            endpoint=endpoint,
            request_data=json.dumps(request_data),  # Преобразование в JSON строку
            response_data=json.dumps(response_data),  # Преобразование в JSON строку
        )
        session.add(log_entry)
        session.commit()
        logging.info("Request successfully saved to the database.")
    except Exception as e:
        logging.error(f"Failed to save request to the database: {e}")
        session.rollback()


# API для загрузки документа
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


# API для преобразования речи в текст (Speech-to-Text)
@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    logging.info("Speech-to-Text endpoint was accessed.")
    if 'file' not in request.files:
        logging.error("No audio file was uploaded.")
        response = {"error": "No audio file uploaded"}
        save_request_to_db('/speech_to_text', {}, response)
        return jsonify(response), 400
    audio_file = request.files['file']
    if audio_file.filename == '':
        logging.error("No audio file selected for upload.")
        response = {"error": "No selected audio file"}
        save_request_to_db('/speech_to_text', {}, response)
        return jsonify(response), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
    logging.info(f"Saving audio file to {file_path}.")
    audio_file.save(file_path)

    try:
        logging.info(f"Processing audio file: {file_path}")
        recognizer = sr.Recognizer()
        audio = sr.AudioFile(file_path)
        with audio as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        response = {"message": "Speech converted to text successfully", "text": text}
        save_request_to_db('/speech_to_text', {"file_name": audio_file.filename}, response)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error during speech recognition: {e}")
        response = {"error": "Failed to process speech"}
        save_request_to_db('/speech_to_text', {"file_name": audio_file.filename}, response)
        return jsonify(response), 500


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
        response = {"error": "Instructions are required."}
        save_request_to_db('/process_prompt', data, response)
        return jsonify(response), 400

    if not document_text:
        logging.error("No document text provided.")
        response = {"error": "Document text is required."}
        save_request_to_db('/process_prompt', data, response)
        return jsonify(response), 400

    try:
        logging.info("Sending prompt and document text to OpenAI for analysis.")
        # Используем старую версию OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Укажите актуальную модель
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": document_text},
            ],
            max_tokens=1000,
            temperature=0.7,
)


        # Получение текста анализа
        analysis = response['choices'][0]['message']['content']

        response_data = {"message": "Prompt processed successfully", "analysis": analysis}

        # Сохранение в базу данных
        save_request_to_db('/process_prompt', data, response_data)
        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"Error during prompt processing: {e}")
        response = {"error": "Failed to process prompt"}
        save_request_to_db('/process_prompt', data, response)
        return jsonify(response), 500


if __name__ == '__main__':
    logging.info("Starting Flask application.")
    app.run(debug=True)
