import sys
import os
import datetime
import uuid
import csv
import logging
from pathlib import Path
from time import time
from dotenv import load_dotenv

import streamlit as st
from streamlit_feedback import streamlit_feedback

from utils import save_uploaded_file
from dataprep import extract_text_simple, detect_pdf_format, extract_f_double, extract_text_chunks_from_pdf, get_text_chunks
from email_utils import EmailSender
from chat_utils import get_vectorstore, get_conversation_chain

load_dotenv()
email_sender = EmailSender(os.getenv('SENDER_EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD'))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


emoji2str ={"👍": "Positive" ,
            "👎": "Négative"}

def initialize_session_state():
    """
    Initialise les variables de session nécessaires pour Streamlit.
    """
    st.session_state.setdefault('session_id', datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    st.session_state.setdefault('messages', [])
    st.session_state.setdefault('feedback_history', [])
    st.session_state.setdefault('file_processed', False)
    st.session_state.setdefault('chat_history', [])  
    st.session_state.setdefault('uploaded_file', None)
    st.session_state.setdefault('file_uploader_key', 0)
    st.session_state.setdefault('conversation', None)  


def reset_conversation(email_sender):
    """
    Réinitialise l'état de la session pour démarrer une nouvelle conversation,
    tout en sauvegardant les feedbacks et en envoyant un email si nécessaire.
    """
    if len(st.session_state.feedback_history) > 0:
        feedback_file = save_feedback()

        # Envoi du feedback par email
        email_sender.send_feedback_email(os.getenv('RECIP_EMAIL_ADDRESS'), feedback_file)

        st.success(f"Email envoyé avec succès au client avec le fichier {feedback_file.name} !")

    st.session_state.messages = []
    st.session_state.feedback_history = []
    st.session_state.file_processed = False
    st.session_state.chat_history = []
    st.session_state.uploaded_file = None
    st.session_state.file_uploader_key += 1
    st.session_state.conversation = None  


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

    return filepath  


def structure_feedback(response):
    """
    Ajoute un feedback structuré à l'historique.
    """
    if not st.session_state.feedback_history:
        st.warning("Aucune interaction disponible pour ajouter un feedback.")
        return

    # Structuration du feedback
    last_entry = st.session_state.feedback_history[-1]
    feedback = {
        "score": response.get("score"),
        "valeur": emoji2str.get(response.get("score"), 'Nan'),
        "text": response.get("text", "").strip() if response.get("text") else "NAN"
    }
    last_entry.update({'feedback': feedback})
    st.success("Feedback ajouté à l'historique avec succès !")


def main():
    try:
        initialize_session_state()

        st.set_page_config(layout="wide", page_title="LAW_GPT DXC CDG")

        st.markdown("<h1 style='color: purple;'><i class='fas fa-balance-scale'></i> LAWGPT </h1>", unsafe_allow_html=True)
        st.sidebar.image("static/logo_dxc.jpg", width=600)

        # Réinitialiser la conversation
        if st.sidebar.button("🔄 New conversation"):
            reset_conversation(email_sender)
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
                    text_chunks = extract_text_chunks_from_pdf(file_path)
                    vectorstore = get_vectorstore(text_chunks)

                    st.session_state.vectorstore = vectorstore
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Hello, I am your legal chatbot! 😊"
                    })
                    st.session_state.file_processed = True
            else:
                st.info("⚠️ Le fichier a déjà été traité.")

        # Afficher les messages précédents
        for msg in st.session_state.get("messages", []):
            st.chat_message(msg["role"]).write(msg["content"])

        # Entrée utilisateur
        if user_input := st.chat_input("Ask your legal question..."):
            if not user_input.strip():
                st.warning("❌ Veuillez saisir une question valide.")
                return

            # Vérifier les prérequis
            if st.session_state.vectorstore is None:
                st.warning("⚠️ Le vectorstore n'est pas initialisé. Veuillez d'abord traiter un fichier.")
                return

            if st.session_state.conversation is None:
                st.session_state.conversation = get_conversation_chain(
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
                structure_feedback(feedback_response)

    except Exception as e:
        print(e)
        error_message = f"Erreur : {e}"
        st.error("L'opération a échoué. Vérifiez votre connexion ou assurez-vous d'avoir uploadé le bon fichier PDF.")
        email_sender.send_error_email(os.getenv('RECIP_EMAIL_ADDRESS'), error_message)


if __name__ == "__main__":
    main()
