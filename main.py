from dotenv import load_dotenv
load_dotenv()

__import__('pysqlite3')
import sys
import sqlite3
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

from langchain.chat_models import ChatOpenAI

from langchain.chains import RetrievalQA
import streamlit as st

import tempfile
import os

# 제목
st.title("ChatPDF")
st.write('---')

# 파일 업로드
uploaded_file = st.file_uploader('PDF 파일을 업로드해주세요.',type=['pdf'])
st.write('---')

def pdf_to_document(uploaded_file):
    temp_dir = tempfile.TemporaryDirectory()
    temp_filepath = os.path.join(temp_dir.name, uploaded_file.name)
    with open(temp_filepath, 'wb') as f:
        f.write(uploaded_file.getvalue())
    loader = PyPDFLoader(temp_filepath)
    pages = loader.load_and_split()
    return pages


# 업로드 될 떄 작동하는 코드
if uploaded_file is not None:
    pages = pdf_to_document(uploaded_file)
    
    # split
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunck size, jsut to show
        chunk_size = 300,
        chunk_overlap = 20,
        length_function = len,
        is_separator_regex = False,
    )

    texts = text_splitter.split_documents(pages)
    # print(texts[0])

    # embedding, titoken 설치
    embeddings_model = OpenAIEmbeddings()


    # load it into Chroma
    # export HNSWLIB_NO_NATIVE=1 해야 함
    db = Chroma.from_documents(texts, embeddings_model)


    # Question
    st.header('PDF에게 질문해주세요!')
    question = title = st.text_input('질문을 입력하세요.')

    if st.button('질문하기'):
        with st.spinner('Wait for it...'):
            
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature = 0)
            qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())
            result = qa_chain({'query': question})
            st.write(result['result'])

