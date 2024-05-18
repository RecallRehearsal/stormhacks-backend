from langchain_community.document_loaders import DirectoryLoader
from consts import DATA_DIR


def load_pdfs():
    loader = DirectoryLoader(DATA_DIR, glob="*.pdf")
    documents = loader.load()
    print(documents)
    return documents
