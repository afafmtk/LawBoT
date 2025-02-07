import faiss
from tqdm import tqdm
import streamlit as st
from PyPDF2 import PdfReader
from langchain.memory import ConversationBufferMemory
from langchain_community.docstore.in_memory import InMemoryDocstore

#from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
import pymupdf

from utils import batched
load_dotenv()


def get_vectorstore(text_chunks, batch_size=1000):
    embedding_model = OpenAIEmbeddings()

    index = faiss.IndexFlatL2(len(OpenAIEmbeddings().embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=OpenAIEmbeddings(),
        index=index,
        docstore= InMemoryDocstore(),
        index_to_docstore_id={}
    )


    for batch in batched(text_chunks, batch_size):    
        vector_store.add_texts(batch)


    return vector_store



def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    return conversation_chain


    

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)