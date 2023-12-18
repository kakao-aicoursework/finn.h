from os.path import dirname

from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

CHROMA_COLLECTION_NAME = "kakao"
CHROMA_PERSIST_DIR = f"./.chromadb"


def upload_embedding_from_file(file_path):
    documents = TextLoader(file_path).load()

    text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    ids = [f"{file_path}-{i}" for i in range(len(docs))]

    Chroma.from_documents(
        docs,
        OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
        ids=ids,
    )
    print('db success')


def upload_files():
    files = ["kakao_sync.txt", "kakao_channel.txt", "kakao_social.txt"]
    for file in files:
        upload_embedding_from_file(f"{dirname(__file__)}/data/{file}")


def query_db(query):
    upload_files()

    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
    )
    docs = db.similarity_search(query, k=5)
    str_docs = [doc.page_content for doc in docs]
    return str_docs
