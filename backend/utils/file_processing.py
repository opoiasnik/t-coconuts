import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import pdfplumber
from fpdf import FPDF

def process_file(file_path):
    """Обрабатывает PDF-файл и сохраняет текст с разметкой в новом PDF."""
    try:
        with pdfplumber.open(file_path) as pdf:
            extracted_data = []
            for page in pdf.pages:
                extracted_data.append({
                    "page_number": page.page_number,
                    "text": page.extract_text(),
                    "layout": page.extract_words()  # Извлечение разметки текста
                })

        # Сохранение в новый PDF с сохранением разметки
        styled_pdf_path = file_path.replace('.pdf', '_processed.pdf')
        save_styled_pdf(styled_pdf_path, extracted_data)

        return {"message": "File processed successfully", "styled_pdf": styled_pdf_path}
    except Exception as e:
        return {"error": f"Failed to process file: {e}"}
    
def save_styled_pdf(output_path, extracted_data):
    """Создает новый PDF с сохранением структуры текста."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Настройка шрифта
    pdf.set_font("Arial", size=12)

    for page in extracted_data:
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 10, f"Page {page['page_number']}", ln=True, align='C')  # Номер страницы
        pdf.set_font("Arial", size=12)

        # Добавление текста
        for word in page["layout"]:
            x, y = word["x0"], word["top"]
            pdf.set_xy(x, y)  # Установка координат
            pdf.cell(0, 10, word["text"], ln=True)  # Текст строки

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
