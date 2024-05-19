from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from consts import DATA_DIR, PDF_PATH


def load_pdfs():
    loader = DirectoryLoader(DATA_DIR + PDF_PATH, glob="*.pdf")
    documents = loader.load()
    document = documents[0].page_content.split("\n\n")
    metadata = documents[0].metadata


    return documents


load_pdfs()