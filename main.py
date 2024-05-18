from fastapi import FastAPI, File, UploadFile
from langchain_community.document_loaders import DirectoryLoader
from typing import Annotated
import aiofiles

DATA_DIR = 'data'

def load_pdfs():
    loader = DirectoryLoader(DATA_DIR, glob="*.pdf")
    documents = loader.load()
    print(documents)
    return documents


app = FastAPI()

# Base Routes
@app.get("/healthCheck")
async def root():
    return {"message": "Hello World"}


# Unity Processing Routes
@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


# PDF Processing Routes
@app.post("/addDocument")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(DATA_DIR + file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}