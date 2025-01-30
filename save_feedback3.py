
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add the parent directory to the Python path
import streamlit as st
from streamlit_feedback import streamlit_feedback
import csv
import datetime
import uuid
from pathlib import Path
from load_and_prepare2 import FeedbackEmail, ErrorEmail
from load_and_prepare2 import extract_text_simple, extract_text_simple, detect_pdf_format, extract_f_double
from langchain.schema import Document
import logging
import os
from time import time
from chatbot import  TextChunkHandler, VectorStoreHandler, ConversationChainHandler
from dotenv import load_dotenv



logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def initialize_session_state():
    """
    Initialise les variables de session nécessaires pour Streamlit.
    """
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []  # Historique des conversations
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None  # Initialiser à None pour éviter l'erreur



def reset_conversation():
    if len(st.session_state.feedback_history) > 0:
        feedback_file = save_feedback()
        recipient_email = "afafmatouk2001@gmail.com"

        # Envoi du feedback par email
        feedback_sender = FeedbackEmail("afaf83542@gmail.com", "gwsh qfmz shxb cdam")
        feedback_sender.send_feedback_email(recipient_email, feedback_file)

        st.success(f"Email envoyé avec succès au client avec le fichier {feedback_file.name} !")

    # Réinitialisation des variables de session
    st.session_state.messages = []
    st.session_state.feedback_history = []
    st.session_state.file_processed = False
    st.session_state.chat_history = []
    st.session_state.uploaded_file = None
    st.session_state.file_uploader_key += 1
    st.session_state.conversation = None  # Réinitialiser la conversation



def save_uploaded_file(uploaded_file):
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, uploaded_file.name)
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    return file_path


def process_pdf_file(file_path):
    """
    Traite un fichier PDF, extrait le texte, génère des chunks,
    et crée un magasin de vecteurs.
    """
    # Détecter le format du PDF
    format_type = detect_pdf_format(file_path)
    logger.info(f"📝 Format detected. : {format_type}")

    # Extraire le texte selon le format détecté
    if format_type == "double":
        text = extract_f_double(file_path)
    else:
        text = extract_text_simple(file_path)

    text_chunks = TextChunkHandler.get_text_chunks(text)
    logger.info(f" {len(text_chunks)} Chunks generated from the text.")

    vectorstore = VectorStoreHandler.get_vectorstore(text_chunks)
    logger.info(" Vectors successfully created.")

    return vectorstore


def save_feedback():
    """
    Sauvegarde les feedbacks dans un fichier CSV spécifique à la session.
    """
    feedback_dir = Path('feedbacks')
    feedback_dir.mkdir(exist_ok=True)  # Crée le dossier si nécessaire

    filepath = feedback_dir / f'{st.session_state.session_id}.csv'
    file_exists = filepath.exists()

    with open(filepath, mode='w' if not file_exists else 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Ajouter l'en-tête si le fichier est nouveau
        if not file_exists:
            writer.writerow(["Question", "Answer", "Score", "Valeur", "Commentaire"])

        # Écrire les feedbacks dans le fichier
        for feedback in st.session_state.feedback_history:
            writer.writerow([
                feedback.get('Question', ''),
                feedback.get('Réponse', ''),
                feedback.get('feedback', {}).get('score', ''),
                feedback.get('feedback', {}).get('valeur', ''),
                feedback.get('feedback', {}).get('text', '')
            ])

    return filepath  # Retourne le chemin du fichier pour d'autres usages (e.g., email)


def save_feedback():
    """
    Sauvegarde les feedbacks dans un fichier CSV spécifique à la session.
    """
    feedback_dir = Path('feedbacks')
    feedback_dir.mkdir(exist_ok=True)  # Crée le dossier si nécessaire

    filepath = feedback_dir / f'{st.session_state.session_id}.csv'
    file_exists = filepath.exists()

    with open(filepath, mode='w' if not file_exists else 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Ajouter l'en-tête si le fichier est nouveau
        if not file_exists:
            writer.writerow(["Question", "Answer", "Score", "Valeur", "Commentaire"])

        # Écrire les feedbacks dans le fichier
        for feedback in st.session_state.feedback_history:
            writer.writerow([
                feedback['Question'],
                feedback['Réponse'],
                feedback['feedback']['score'],
                feedback['feedback']['valeur'],
                feedback['feedback']['text']
            ])

    return filepath  # Retourne le chemin du fichier pour d'autres usages (e.g., email)

def fbcb(response):
    """
    Ajoute un feedback structuré à l'historique.
    """
    if not st.session_state.feedback_history:
        st.warning("No interaction available to add feedback.")
        return

    # Structuration du feedback
    last_entry = st.session_state.feedback_history[-1]
    feedback = {
        "score": response.get("score"),
        "valeur": "Positive" if response.get("score") == "👍" else ("Négative" if response.get("score") == "👎" else "NaN"),
        "text": response.get("text", "").strip() if response.get("text") else "NAN"
    }

    # Mise à jour du dernier feedback
    last_entry.update({'feedback': feedback})
    st.success("Feedback successfully added to history!")



def main():
    try:
        load_dotenv()
        initialize_session_state()
        st.set_page_config(layout="wide", page_title="LAW_GPT DXC CDG")

        st.markdown("<h1 style='color: purple;'><i class='fas fa-balance-scale'></i> LAWGPT </h1>", unsafe_allow_html=True)
        st.sidebar.image("static/logo_dxc.jpg", width=600)

        # Réinitialiser la conversation
        if st.sidebar.button("🔄 New conversation"):
            reset_conversation()
            st.rerun()

        # Téléchargement de fichier
        uploaded_file = st.file_uploader(
            "Upload a PDF file", type=["pdf"], label_visibility="collapsed",
            key=f"file_uploader_{st.session_state.file_uploader_key}"
        )

        if uploaded_file is not None:
            if not st.session_state.file_processed:
                file_path = save_uploaded_file(uploaded_file)
                with st.spinner("Processing PDF file..."):
                    vectorstore = process_pdf_file(file_path)
                    st.session_state.vectorstore = vectorstore
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Hello, I am your legal chatbot! 😊"
                    })
                    st.session_state.file_processed = True
            else:
                st.info("⚠️ The file has already been processed.")

        # Afficher les messages précédents
        for msg in st.session_state.get("messages", []):
            st.chat_message(msg["role"]).write(msg["content"])

        # Entrée utilisateur
        if user_input := st.chat_input("Ask your legal question..."):
            if not user_input.strip():
                st.warning("❌ Please enter a valid question.")
                return

            # Vérifier les prérequis
            if st.session_state.vectorstore is None:
                st.warning("⚠️ Vectorstore is not initialized. Please process a file first.")
                return

            if st.session_state.conversation is None:
                st.session_state.conversation = ConversationChainHandler.get_conversation_chain(
                    st.session_state.vectorstore
                )

            # Ajouter l'entrée utilisateur à l'historique des messages
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)

            # Ajouter la question utilisateur à l'historique
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Appeler la chaîne conversationnelle
            with st.spinner("Searching in progress..."):
                result = st.session_state.conversation.run({
                    'question': user_input,
                    'chat_history': st.session_state.chat_history
                })

            # Ajouter la réponse du chatbot à l'historique
            st.session_state.messages.append({"role": "assistant", "content": result})
            st.chat_message("assistant").write(result)
            st.session_state.chat_history.append({"role": "assistant", "content": result})

            # Ajouter l'entrée et la réponse au feedback
            st.session_state.feedback_history.append({
                'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Session_ID': st.session_state.session_id,
                'Question': user_input,
                'Réponse': result,
            })

        # Gestion des feedbacks
        if len(st.session_state.feedback_history) > 0:
            feedback_response = streamlit_feedback(
                feedback_type="thumbs",
                optional_text_label="[Optional] Explain your choice.",
                key=f"fb_{len(st.session_state.feedback_history)}",
            )
            if feedback_response:
                fbcb(feedback_response)

    except Exception as e:
        error_message = f"Erreur : {e}"
        st.error("The operation failed because either your connection or upload the right PDF file ")
        print(error_message)

        # Envoi d'un email d'erreur en cas de problème
        email_sender = ErrorEmail("afaf83542@gmail.com", "gwsh qfmz shxb cdam")
        email_sender.send_error_email("afafmatouk2001@gmail.com", error_message)
