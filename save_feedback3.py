
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add the parent directory to the Python path
import streamlit as st
from streamlit_feedback import streamlit_feedback
import csv
import datetime
import uuid
from pathlib import Path

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
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    if 'fbk' not in st.session_state:
        st.session_state.fbk = str(uuid.uuid4())
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []  # Historique des conversations
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0

def reset_conversation():
    st.session_state.messages = []
    st.session_state.feedback_history = []
    st.session_state.file_processed = False
    st.session_state.vectorstore = None
    st.session_state.conversation = None
    st.session_state.chat_history = []  # Réinitialisation de l'historique
    st.session_state.uploaded_file = None
    st.session_state.file_uploader_key += 1

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


# Sauvegarde du feedback in CSV file
def save_feedback():
    feedback_dir = Path('feedbacks')
    feedback_dir.mkdir(exist_ok=True)
    filepath = feedback_dir / f'{st.session_state.session_id}.csv'

    file_exists = filepath.exists()

    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Question", "Answer", "Score", "Valeur", "Commentaire"])

        for feedback in st.session_state.feedback_history:
            writer.writerow([
                feedback['Question'],
                feedback['Réponse'],
                feedback['feedback']['score'],
                feedback['feedback']['valeur'],
                feedback['feedback']['text']
            ])

# Gestion des feedbacks
def fbcb(response):
    if not st.session_state.feedback_history:
        st.warning("No interaction available to add feedback.")
        return

    last_entry = st.session_state.feedback_history[-1]
    #Structuration du feedback
    feedback = {
        "score": response.get("score"),
        "valeur": "Positive" if response.get("score") == "👍" else ("Négative" if response.get("score") == "👎" else "NaN"),
        "text": response.get("text", "").strip() if response.get("text") else "NAN"
    }

    last_entry.update({'feedback': feedback})
    save_feedback()
    st.success("Feedback successfully recorded!") 



def main():
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
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], label_visibility="collapsed",
                                     key=f"file_uploader_{st.session_state.file_uploader_key}")
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
            try:
                result = st.session_state.conversation.run({
                    'question': user_input,
                    'chat_history': st.session_state.chat_history
                })
            except Exception as e:
                st.error(f"An error occurred: {e}")
                return

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


if __name__ == "__main__":
    main()