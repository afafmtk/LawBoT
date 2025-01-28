#from pypdf import PdfReader
import re
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chatbot import PDFHandler
from PyPDF2 import PdfReader

#nlp = spacy.load("fr_core_news_sm")


def extract_text_simple(pdf_path):
    """
    Extrait le texte d'un PDF en mode simple.
    """
    # Utiliser PDFHandler pour centraliser l'extraction de texte
    raw_text = PDFHandler.get_pdf_text([pdf_path])  # PDFHandler attend une liste de fichiers
    cleaned_text = clean_text(raw_text)
    return cleaned_text


def extract_f_double(pdf_path):
    """
    Extrait et structure le texte pour un PDF à double format.
    """
    # Utiliser PDFHandler pour extraire le texte
    raw_text = PDFHandler.get_pdf_text([pdf_path])
    all_pages_text = []

    for text in raw_text.split("\n\n"):  # Supposer que les pages sont séparées par "\n\n"
        structured_text = analyze_page_structure(clean_text(text))
        all_pages_text.append(structured_text)

    return '\n'.join(all_pages_text)




def detect_pdf_format(pdf_path):
    """
    Detect if the PDF is in single or double column format.
    """
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]  # Load the first page
        text = page.extract_text()
        
        # Simple heuristic: count the number of long spaces to infer columns
        left_count = 0
        right_count = 0
        middle_x = 0.5  # Assume normalized coordinates

        for line in text.splitlines():
            if len(line.strip()) == 0:
                continue
            # Check the position of the text blocks (mocked for PyPDF2 as it doesn't give exact positions)
            words = line.split()
            if len(words) > 0:
                if len(words) <= 5:  # Arbitrary heuristic for left-aligned text
                    left_count += 1
                else:
                    right_count += 1

        if left_count > 0 and right_count > 0:
            return "double"
        else:
            return "simple"
    except Exception as e:
        return f"Erreur lors de la détection : {e}"

def clean_text(text):
    """
    Nettoie et normalise le texte extrait
    """
    text = re.sub(r'\s+', ' ', text)  
    text = re.sub(r'\n+', '\n', text)  
    text = re.sub(r'[^\w\s.,;:!?()\[\]\'"-]', '', text)
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)  
    text = re.sub(r'([.,;:!?])\s+', r'\1 ', text)  
    text = re.sub(r'\s{2,}', ' ', text)

    # Normalisation 
    text = text.lower()

    return text.strip()

def analyze_page_structure(text):
    column_markers = identify_column_markers(text)
    structured_text = reorganize_columns(text, column_markers)
    return structured_text

def identify_column_markers(text):
    markers = []
    space_sequences = re.finditer(r'\s{4,}', text)
    for match in space_sequences:
        markers.append(match.start())
    return markers

def reorganize_columns(text, markers):
    if not markers:
        return text
    columns = []
    start = 0
    for marker in markers:
        columns.append(text[start:marker].strip())
        start = marker
    columns.append(text[start:].strip())
    return '\n'.join(columns)


