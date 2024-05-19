from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os
import shutil
from consts import DATA_DIR, PDF_PATH, CHROMA_PATH

def load_pdfs():
    loader = DirectoryLoader(DATA_DIR + PDF_PATH, glob="*.pdf")
    documents = loader.load()
    document = documents[0].page_content.split("\n\n")
    metadata = documents[0].metadata

    return (document, metadata)

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )

    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")



load_pdfs()