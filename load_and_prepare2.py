#from pypdf import PdfReader
import re
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chatbot import PDFHandler
from PyPDF2 import PdfReader
import fitz 
import pymupdf 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import unicodedata



def extract_text_simple(uploaded_file):
    """
    Extrait le texte d'un PDF en mode simple en excluant les images et tableaux.
    """
    raw_text = PDFHandler.get_pdf_text(uploaded_file)
    cleaned_text = clean_text(raw_text)
    return cleaned_text


def extract_f_double(uploaded_file):
    """
    Extrait et structure le texte pour un PDF à double format en excluant les images et tableaux.
    """
    raw_text = PDFHandler.get_pdf_text(uploaded_file)
    all_pages_text = []
    
    for text in raw_text.split("\n\n"):  # Supposer que les pages sont séparées par "\n\n"
        structured_text = analyze_page_structure(clean_text(text))
        all_pages_text.append(structured_text)
    
    return '\n'.join(all_pages_text)


def detect_pdf_format(uploaded_file):
    try:
        if isinstance(uploaded_file, BytesIO):
            doc = pymupdf.open(stream=uploaded_file, filetype="pdf")
        else:
            doc = pymupdf.open(uploaded_file)
        
        page = doc.load_page(0)
        blocs = page.get_text("dict")["blocks"]
        
        left_count = 0
        right_count = 0
        middle_x = page.rect.width / 2
        
        for block in blocs:
            if "bbox" in block and block.get("type", "") == 0:
                x0, _, x1, _ = block["bbox"]
                if x1 <= middle_x:
                    left_count += 1
                elif x0 >= middle_x:
                    right_count += 1
        
        doc.close()
        
        if left_count > 0 and right_count > 0:
            return "double"
        else:
            return "simple"
    except Exception as e:
        return f"Erreur lors de la détection : {e}"
    


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

class EmailSender:
    def __init__(self, sender_email, sender_password):
        
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587  # Port pour TLS

    def send_email(self, recipient_email, subject, body, attachment_path=None):
        
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Ajouter une pièce jointe si un fichier est fourni
        if attachment_path:
            if os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
                    msg.attach(part)
            else:
                print(f"⚠️ Le fichier {attachment_path} n'existe pas. Email envoyé sans pièce jointe.")

        # Envoi de l’email via SMTP
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            print(f"✅ Email envoyé avec succès à {recipient_email} !")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email : {e}")

class FeedbackEmail(EmailSender):
    def __init__(self, sender_email, sender_password):
        super().__init__(sender_email, sender_password)

    def send_feedback_email(self, recipient_email, filepath):
        if os.path.exists(filepath):
            subject = f"Feedbacks de votre session {os.path.basename(filepath)}"
            body = "Veuillez trouver ci-joint le fichier contenant les feedbacks de votre session."
            self.send_email(recipient_email, subject, body, filepath)
        else:
            print("⚠️ Fichier feedback non trouvé, email non envoyé.")

class ErrorEmail(EmailSender):
    def __init__(self, sender_email, sender_password):
        super().__init__(sender_email, sender_password)

    def send_error_email(self, recipient_email, error_message):
        subject = "🚨 Erreur dans LAW_GPT"
        body = f"Une erreur est survenue dans l'application :\n\n{error_message}"
        self.send_email(recipient_email, subject, body)
