import os
from fastapi import FastAPI, File, UploadFile
from openai import OpenAI
from consts import DATA_DIR, PDF_PATH, AUDIO_PATH
from fastapi.staticfiles import StaticFiles
from pdf import generate_data_store, generate_questions
import json

class state:
    chatHistory = []

# Init API
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


# Base Routes
@app.get("/healthCheck")
async def root():
    return {"message": "Server Up"}


# Unity Processing Routes
@app.post("/processAnswer")
def upload(file: UploadFile = File(...)):
    # Save Wav File
    file_location = DATA_DIR + AUDIO_PATH + file.filename
    try:
        contents = file.file.read()
        with open(file_location, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    print("Successfully uploaded file: ", file_location)

    # Process Wav File
    try:
        with open(file_location, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                response_format="text",
                file=f,
            )

            print("Successfully created transcription.\nResulting Transcription: ", transcription)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Answer the following question in 3 sentences or less."},
                    {"role": "user", "content": transcription},
                ]
            )

            print("Successfully created response.\nResulting Response: ", response)

            #speech_file_path = DATA_DIR + AUDIO_PATH + "speech.mp3"
            speech_file_path = "static/speech.mp3"
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=response.choices[0].message.content
            )

            print("Successfully created speech from text.\nResulting audio file saved at: ", speech_file_path)
            audio_response.stream_to_file(speech_file_path)

        return {"message": speech_file_path}
        #return FileResponse(speech_file_path, media_type="audio/mp3")

    except Exception as e:
        print(e)
        return {"message": "There was an error creating the file"}

    return {"message": "There was an error creating the response"}




# For Unity to call to initialize the questions and data store
@app.get("/initialize")
def init():
    input_text = generate_data_store()
    questions = generate_questions(client, input_text)
    print(questions)
    print(type(questions))
    return json.loads(questions)


# PDF Processing Routes
@app.post("/addDocument")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(DATA_DIR + '/' + PDF_PATH + "/" + data.pdf, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    #load_pdfs()

    return {"message": f"Successfully uploaded {file.filename}"}
