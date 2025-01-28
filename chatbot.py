import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import HuggingFaceHub
load_dotenv()

class PDFHandler:
    @staticmethod
    def get_pdf_text(pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text


class TextChunkHandler:
    @staticmethod
    def get_text_chunks(text):
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
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
        llm = ChatOpenAI()
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, k=10)
        #Gardez uniquement les 10 derniers échanges avec l'utilisateur
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        # pour Limiter le nombre de chunks récupérés
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory
        )
        return conversation_chain

"""
class UserInputHandler:
    @staticmethod
    def handle_userinput(user_question):
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history_1']

        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
"""