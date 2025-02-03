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


def summarize_chunks(chunks, summary_max_tokens=300):
    summarizer = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=summary_max_tokens)
    full_text = "\n".join(chunks)
    prompt = (
        """
        Voici le contenu extrait de parties d'un document. Résume ce texte de manière concise 
        en ne dépassant pas {summary_max_tokens} tokens, tout en conservant les informations essentielles :\n\n
        {full_text}\n\nRésumé """
    )
    
    summary = summarizer(prompt)
    return summary

class SummarizingRetriever:
    def __init__(self, base_retriever, summary_max_tokens=200):
        self.base_retriever = base_retriever
        self.summary_max_tokens = summary_max_tokens

    def get_relevant_documents(self, query):
        docs = self.base_retriever.get_relevant_documents(query)
        chunks = [doc.page_content for doc in docs]
        summary = summarize_chunks(chunks, summary_max_tokens=self.summary_max_tokens)
        return [Document(page_content=summary, metadata={})]

class ConversationChainHandler:
    @staticmethod
    def get_conversation_chain(vectorstore):
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        base_retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        summarizing_retriever = SummarizingRetriever(base_retriever, summary_max_tokens=200)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=summarizing_retriever,
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
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)