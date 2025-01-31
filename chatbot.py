import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
#from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
import pymupdf
load_dotenv()


"""class PDFHandler:
    @staticmethod
    def get_pdf_text(pdf_docs):
        text = ""
        for pdf in pdf_docs:
            with open(pdf, "rb") as f:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""  # Évite les erreurs si le texte est None
        return text"""


"""class PDFHandler:
    @staticmethod
    def get_pdf_text(pdf_docs):

        text = ""
        for pdf in pdf_docs:
            doc = pymupdf.open(pdf)
            
            for page in doc:
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if "image" not in block and "table" not in block:
                        text += block.get("text", "") + "\n"
            
            doc.close()
        return text.strip()"""

class PDFHandler:
    @staticmethod
    def get_pdf_text(pdf_docs):
        """
        Extrait le texte d'une liste de PDFs en excluant les images et tableaux.
        """
        text = ""
        for pdf in pdf_docs:
            try:
                doc = pymupdf.open(pdf)  # Assurez-vous que pdf est un chemin de fichier valide
                
                for page in doc:
                    blocks = page.get_text("dict")["blocks"]
                    for block in blocks:
                        if block.get("type", "") == 0:  # Vérifie que c'est bien du texte
                            text += block.get("text", "") + "\n"

                doc.close()
            except Exception as e:
                print(f"Erreur lors de la lecture du PDF {pdf}: {e}")
        
        return text.strip()




class TextChunkHandler:
    @staticmethod
    def get_text_chunks(text):
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks



class VectorStoreHandler:
    @staticmethod
    def get_vectorstore(text_chunks):
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings) #FAISS fonctionne uniquement en mémoire.
        return vectorstore


class ConversationChainHandler:
    @staticmethod
    def get_conversation_chain(vectorstore):
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        #memory = ConversationBufferWindowMemory(memory_key='chat_history', return_messages=True, k=8)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory
        )
        return conversation_chain


class UserInputHandler:
    @staticmethod
    def handle_userinput(user_question):
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
