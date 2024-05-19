from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil
from consts import DATA_DIR, PDF_PATH, CHROMA_PATH, QUESTION_PROMPT

def generate_data_store():
    documents, input_text = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)
    return input_text

def load_documents():
    loader = DirectoryLoader(DATA_DIR + PDF_PATH, glob="*.pdf")
    documents = loader.load()
    input_text = " ".join(documents[0].page_content.split("\n\n"))
    return (documents, input_text)

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")


    return chunks

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


def generate_questions(client, input_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": QUESTION_PROMPT + " Input Text: " + input_text},
        ]
    )

    return response.choices[0].message.content