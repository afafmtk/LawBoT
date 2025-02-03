import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
#from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
import pymupdf
load_dotenv()



class PDFHandler:
    @staticmethod
    def get_pdf_text(pdf_docs):
        text = ""
        for pdf in pdf_docs:
            with open(pdf, "rb") as f:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
        return text


class TextChunkHandler:
    @staticmethod
    def get_text_chunks(text):
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks


class VectorStoreHandler:
    @staticmethod
    def get_vectorstore(text_chunks):
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore

class ConversationChainHandler:
    @staticmethod
    def get_conversation_chain(vectorstore, summary_max_tokens=200):
        """
        Initialise une chaîne de conversation en limitant le contexte via un résumé des 3 chunks récupérés.
        """
        # Initialisation du modèle LLM
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

        # Initialisation de la mémoire conversationnelle
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

        # Définition du retriever pour récupérer les 3 chunks les plus pertinents
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # Récupération des documents pertinents (3 chunks)
        retrieved_docs = retriever.get_relevant_documents("")
        chunks = [doc.page_content for doc in retrieved_docs]

        # Vérification si des chunks ont été trouvés
        if chunks:
            summary_context = ConversationChainHandler.summarize_chunks(chunks, summary_max_tokens)
            system_message = {"role": "system", "content": f"Résumé du contexte pertinent : {summary_context}"}
            memory.chat_memory.add_message(system_message)

        # Création de la chaîne de conversation
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory
        )

        return conversation_chain

    @staticmethod
    def summarize_chunks(chunks, summary_max_tokens=200):
        """
        Résume les 3 chunks sélectionnés pour réduire leur taille avant de les envoyer au modèle.
        """
        from langchain.chat_models import ChatOpenAI
        
        summarizer = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=summary_max_tokens)

        # Concaténer les 3 chunks
        full_text = "\n".join(chunks)

        # Construire l'invite pour le résumé
        prompt = (
            "Voici le contenu extrait d'un document juridique. Résume ce texte de manière concise "
            f"en ne dépassant pas {summary_max_tokens} tokens, tout en conservant les informations essentielles :\n\n"
            f"{full_text}\n\nRésumé :"
        )

        summary = summarizer(prompt)
        return summary


class UserInputHandler:
    @staticmethod
    def handle_userinput(user_question):
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)