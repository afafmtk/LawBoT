import faiss
from tqdm import tqdm
from itertools import islice
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain_community.docstore.in_memory import InMemoryDocstore

#from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
import pymupdf
load_dotenv()



def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        with open(pdf, "rb") as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
    return text



# def summarize_text(text):
#     llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
#     summary_prompt = "Résume ce texte de manière concise : " + text[:4000]  
#     response = llm.predict(summary_prompt)
    # return response



def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator=" ",
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    print(len(chunks))
    print(len(chunks[0]))
    print(len(chunks[-1]))
    # raise
    return chunks



# def get_vectorstore(text_chunks):
#     embeddings = OpenAIEmbeddings()
#     print(f'{type(text_chunks)=}')
#     print(f'{len(text_chunks)=}')
#     print(f'{len(text_chunks[0])=}')

#     # text_chunks =text_chunks[:1]*10000
#     print(f'{len(text_chunks)=} dummy')
    
#     vectorstore = FAISS.from_texts(texts=text_chunks, embedding=OpenAIEmbeddings())
#     return vectorstore



def batched(lst, chunk_size):
    it = iter(lst)
    return iter(lambda: list(islice(it, chunk_size)), [])


def get_vectorstore(text_chunks, batch_size=100):
    print(f'{type(text_chunks)=}')
    print(f'{len(text_chunks)=}')
    print(f'{len(text_chunks[0])=}')
    print(f'{len(text_chunks[-1])=}')
    print(f'{text_chunks[0]=}')
    print(f'{text_chunks[-1]=}')


    # text_chunks =text_chunks[:1]*1000
    # print(f'{len(text_chunks)=} dummy')

    embedding_model = OpenAIEmbeddings()

    index = faiss.IndexFlatL2(len(OpenAIEmbeddings().embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=OpenAIEmbeddings(),
        index=index,
        docstore= InMemoryDocstore(),
        index_to_docstore_id={}
    )


    for idx in tqdm(range(0, len(text_chunks), batch_size)):
        print('fffffffffffff', len(text_chunks[idx: idx + batch_size]))
        vector_store.add_texts(text_chunks[idx: idx + batch_size])



   

    print(vector_store)

    # raise
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



"""class PDFProcessor:
    @staticmethod
    def process_pdf(pdf_docs):
        text = PDFHandler.get_pdf_text(pdf_docs)
        summarized_text = TextSummarizer.summarize_text(text)
        text_chunks = TextChunkHandler.get_text_chunks(summarized_text)
        vectorstore = VectorStoreHandler.get_vectorstore(text_chunks)
        return vectorstore
"""

    


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)