import pytesseract
from PIL import Image
from PyPDF2 import PdfReader


def process_file(file_path):
    try:
        if file_path.endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        elif file_path.endswith(('.jpg', '.png')):
            return extract_text_from_image(file_path)
        else:
            return {"error": "Unsupported file format"}
    except Exception as e:
        return {"error": str(e)}

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() + "\n"
        return {"text": extracted_text}
    except Exception as e:
        return {"error": f"Failed to process PDF: {str(e)}"}

def extract_text_from_image(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return {"text": text}
    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}
