from fastapi import FastAPI, File, UploadFile
from consts import DATA_DIR


# Init API
app = FastAPI()


# Base Routes
@app.get("/healthCheck")
async def root():
    return {"message": "Server Up"}


# Unity Processing Routes


# PDF Processing Routes
@app.post("/addDocument")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(DATA_DIR + '/' + file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}

