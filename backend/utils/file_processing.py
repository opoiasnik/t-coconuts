import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import pdfplumber
from fpdf import FPDF
import logging


def process_file(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            extracted_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"  # Сохраняем переносы строк

        if not extracted_text.strip():
            raise ValueError("No text could be extracted from the PDF. It might be an image-based PDF.")

        logging.info(f"Extracted text (first 500 chars): {extracted_text[:500]}...")
        return {"text": extracted_text, "message": "File processed successfully"}

    except Exception as e:
        logging.error(f"Failed to process file: {e}")
        return {"error": str(e)}

    try:
        with pdfplumber.open(file_path) as pdf:
            extracted_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"

        if not extracted_text.strip():
            raise ValueError("No text could be extracted from the PDF. It might be an image-based PDF.")

        logging.info(f"Extracted text (first 500 chars): {extracted_text[:500]}...")
        return {"text": extracted_text, "message": "File processed successfully"}

    except Exception as e:
        logging.error(f"Failed to process file: {e}")
        return {"error": str(e)}

    
def save_styled_pdf(output_path, extracted_data):
    """Создает новый PDF с сохранением структуры текста."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Загрузка шрифтов с поддержкой Unicode
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    pdf.add_font('DejaVu', 'I', 'DejaVuSans-Oblique.ttf', uni=True)
    pdf.add_font('DejaVu', 'BI', 'DejaVuSans-BoldOblique.ttf', uni=True)

    for page in extracted_data:
        pdf.add_page()
        pdf.set_font('DejaVu', style="B", size=14)
        pdf.cell(200, 10, f"Page {page['page_number']}", ln=True, align='C')  # Номер страницы
        pdf.set_font('DejaVu', size=12)

        # Добавление текста
        if page["text"]:
            pdf.multi_cell(0, 10, page["text"])

    # Сохранение PDF
    pdf.output(output_path)

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
