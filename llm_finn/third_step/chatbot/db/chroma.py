from os.path import dirname

from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

CHROMA_COLLECTION_NAME = "kakao"
CHROMA_PERSIST_DIR = f"./.chromadb"


def upload_embedding_from_file(intent):
    file_path = f"{dirname(__file__)}/data/{intent}.txt"
    documents = TextLoader(file_path).load()

    text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    ids = [f"{file_path}-{i}" for i in range(len(docs))]

    Chroma.from_documents(
        docs,
        OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=f"{CHROMA_PERSIST_DIR}/{intent}",
        ids=ids,
    )
    print('db success')


def upload_files():
    intents = ["kakao_sync", "kakao_channel", "kakao_social"]
    for intent in intents:
        upload_embedding_from_file(intent)


def query_db(query, intent):
    db = Chroma(
        persist_directory=f"{CHROMA_PERSIST_DIR}/{intent}",
        embedding_function=OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
    )
    docs = db.similarity_search(query, k=5)
    str_docs = [doc.page_content for doc in docs]
    return str_docs
