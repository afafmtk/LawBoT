#from pypdf import PdfReader
import re
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter

from PyPDF2 import PdfReader
import fitz 
import pymupdf 

import os
import unicodedata
#import spacy
#from spacy.lang.fr.stop_words import STOP_WORDS
#nlp = spacy.load("fr_core_news_sm")
import logging
logger = logging.getLogger(__name__)


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        with open(pdf, "rb") as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
    return text

def clean_text(text):
    """
    Nettoie et normalise le texte extrait en supprimant les caractères indésirables,
    en normalisant l'unicode et en structurant le texte de manière lisible.
    """
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[^\w\s.,;:!?()\[\]\'"-]', '', text)
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    text = re.sub(r'([.,;:!?])\s+', r'\1 ', text)
    text = text.strip()
    text = re.sub(r'Page\s?\d+', '', text, flags=re.IGNORECASE)
    text = text.lower()
    return text


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


def analyze_page_structure(text):
    column_markers = identify_column_markers(text)
    structured_text = reorganize_columns(text, column_markers)
    return structured_text


def extract_text_simple(pdf_path):
    """
    Extrait le texte d'un PDF en mode simple.
    """
    # Utiliser PDFHandler pour centraliser l'extraction de texte
    raw_text = get_pdf_text([pdf_path])  # PDFHandler attend une liste de fichiers
    cleaned_text = clean_text(raw_text)
    return cleaned_text


def extract_f_double(pdf_path):
    """
    Extrait et structure le texte pour un PDF à double format.
    """
    # Utiliser PDFHandler pour extraire le texte
    raw_text = get_pdf_text([pdf_path])
    all_pages_text = []

    for text in raw_text.split("\n\n"):  # Supposer que les pages sont séparées par "\n\n"
        structured_text = analyze_page_structure(clean_text(text))
        all_pages_text.append(structured_text)

    return '\n'.join(all_pages_text)


def detect_pdf_format(pdf_path):
    try:
        # Ouvrir le PDF
        doc = pymupdf.open(pdf_path)
        page = doc.load_page(0)  # Analyse uniquement la première page

        # Extraction du texte avec la méthode des blocs
        blocs = page.get_text("dict")["blocks"]

        # Analyse des positions des blocs
        left_count = 0
        right_count = 0
        middle_x = page.rect.width / 2  # Trouve le milieu de la page

        for block in blocs:
            if "bbox" in block:  # Vérifie si le bloc contient des coordonnées
                x0, _, x1, _ = block["bbox"]  # Coordonnées du bloc

                # Compte les blocs à gauche et à droite
                if x1 <= middle_x:  # Tout le bloc est à gauche
                    left_count += 1
                elif x0 >= middle_x:  # Tout le bloc est à droite
                    right_count += 1

        doc.close()  # Ferme le document après l'analyse

        # Vérifie si les colonnes sont équilibrées
        if left_count > 0 and right_count > 0:
            return "double"  # Deux colonnes détectées
        else:
            return "simple"  # Une seule colonne détectée

    except Exception as e:
        return f"Erreur lors de la détection : {e}"
    

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator=" ",
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def extract_text_chunks_from_pdf(file_path):
    """
    Traite un fichier PDF, extrait le texte, génère des chunks,
    et crée un magasin de vecteurs en intégrant le résumé.
    """
    format_type = detect_pdf_format(file_path)
    logger.info(f"📝 Format detected: {format_type}")

    if format_type == "empty":
        raise ValueError("Le PDF est vide ou ne contient aucune page.")

    if format_type == "double":
        text = extract_f_double(file_path)
    else:
        text = extract_text_simple(file_path)

    if not text.strip():
        raise ValueError("Aucun texte n'a pu être extrait du PDF. Veuillez vérifier le fichier.")
    
    # summarized_text = summarize_text(text)
    text_chunks = get_text_chunks(text)
    if not text_chunks:
        raise ValueError("Le découpage du texte a échoué : aucun chunk n'a été généré.")
    
    logger.info(f"{len(text_chunks)} chunks générés à partir du texte résumé.")

    return text_chunks

    




