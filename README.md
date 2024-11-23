# Dependencies

Below is the list of dependencies used in the project and their purpose:

## 1. Flask-CORS
- **Installation:** `pip install flask-cors`
- **Purpose:** Enables Cross-Origin Resource Sharing (CORS) to allow communication between the frontend and backend.
- **Usage in the Project:**
  - Allows the frontend (e.g., a web client) to send requests to the backend.
  - Integrated using:
    ```python
    from flask_cors import CORS
    CORS(app)
    ```

## 2. PyTesseract
- **Installation:** `pip install pytesseract`
- **Purpose:** Used for Optical Character Recognition (OCR) to extract text from images.
- **Usage in the Project:**
  - Processes uploaded `.jpg` and `.png` files to extract text.
  - Example:
    ```python
    import pytesseract
    text = pytesseract.image_to_string(image)
    ```

## 3. Pillow
- **Installation:** `pip install pillow`
- **Purpose:** A Python Imaging Library used for opening and manipulating image files.
- **Usage in the Project:**
  - Opens and pre-processes image files before performing OCR.
  - Example:
    ```python
    from PIL import Image
    image = Image.open(file_path)
    ```

## 4. PyMongo
- **Installation:** `pip install pymongo`
- **Purpose:** Provides a Python interface for interacting with MongoDB databases.
- **Usage in the Project:**
  - Stores validation results and retrieves data for specific documents.
  - Example:
    ```python
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")
    db = client["my_database"]
    collection = db["documents"]
    ```

## 5. Transformers
- **Installation:** `pip install transformers`
- **Purpose:** Provides pre-trained models for natural language processing tasks such as text analysis and summarization.
- **Usage in the Project:**
  - Used to process and analyze extracted text using AI.
  - Example:
    ```python
    from transformers import pipeline
    analyzer = pipeline("text-classification")
    result = analyzer("This is an example.")
    ```

## 6. Torch
- **Installation:** `pip install torch`
- **Purpose:** A deep learning library used as a backend for `transformers` to execute pre-trained models efficiently.
- **Usage in the Project:**
  - Supports the `transformers` library for running machine learning models.
  - Automatically used as a backend when running tasks like text classification.
