import os
from fastapi import FastAPI, File, UploadFile
from langchain.chains.flare.prompts import PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from consts import DATA_DIR, PDF_PATH, AUDIO_PATH, ANSWER_PROMPT, ANSWER_PROMPT2, SCORE_THRESH
from fastapi.staticfiles import StaticFiles
from pdf import generate_data_store, generate_questions
import json


class state:
    input_text = ""
    chatHistory = {}
    learning_goals = []
    curr_goal = 0
    curr_question = 0


# Init API
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
state = state()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


# Helpers
def getQuestion():
    key = list(state.learning_goals[state.curr_goal].keys())[0]
    if (state.curr_question < 2):
        question = state.learning_goals[state.curr_goal][key][0]['Introductory Questions'][state.curr_question]
    else:
        question = state.learning_goals[state.curr_goal][key][1]['Complex Questions'][state.curr_question-2]
    return question


# Base Routes
@app.get("/healthCheck")
def healthCheck():
    return {"message": "Server Up"}


# Unity Processing Routes
@app.post("/processAnswer")
def processAnswer(file: UploadFile = File(...)):
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

            prompt_template = ChatPromptTemplate.from_template(ANSWER_PROMPT)
            prompt = prompt_template.format(context=state.input_text, question=getQuestion(), answer=transcription)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt},
                ]
            )

            print("Successfully created response.\nResulting Response: ", response.choices[0].message.content)

            prompt_template_accuracy = ChatPromptTemplate.from_template(ANSWER_PROMPT2)
            prompt_accuracy = prompt_template_accuracy.format(context=state.input_text, question=getQuestion(),
                                                              answer=transcription)

            accuracy = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt_accuracy},
                ]
            )

            print("Successfully calculated accuracy.\nResulting Response: ", accuracy.choices[0].message.content)
            accuracy_num = int(accuracy.choices[0].message.content)

            #speech_file_path = DATA_DIR + AUDIO_PATH + "speech.mp3"
            speech_file_path = "static/speech.mp3"
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="shimmer" if state.curr_question < 2 else "echo",
                input=response.choices[0].message.content + ("Let's Try that again!" if accuracy_num<SCORE_THRESH else "Let's Continue to the next question")
            )

            print("Successfully created speech from text.\nResulting audio file saved at: ", speech_file_path)
            audio_response.stream_to_file(speech_file_path)

            if accuracy_num > SCORE_THRESH:
                if(state.curr_question < 4):
                    state.curr_question += 1
                elif(state.curr_question == 4):
                    state.curr_goal += 1
                    state.curr_question = 0

        return {"correctness": accuracy_num}

    except Exception as e:
        print(e)
        return {"message": "There was an error creating the file"}

    return {"message": "There was an error creating the response"}

@app.get("/generateQuestionAudio")
def generateQuestionAudio():
    prompt = "Learning Goal " + str(state.curr_goal+1) + ", Question " + str(state.curr_question+1) + ". " + getQuestion()
    print("Generating Audio for: " + prompt)
    try:
        speech_file_path = "static/speech.mp3"
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer" if state.curr_question < 2 else "echo",
            input=prompt
        )
        print("Successfully created speech from text.\nResulting audio file saved at: ", speech_file_path)
        audio_response.stream_to_file(speech_file_path)
    except:
        return {"message": "There was an error creating the file"}
    return {"message": "success"}


@app.post("/getHelp")
def getHelp(file: UploadFile = File(...)):
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
                    {"role": "system",
                     "content": "You are a helpful assistant. Answer the following question in 3 sentences or less."},
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
def initialize():
    state.input_text = generate_data_store()
    questions = generate_questions(client, state.input_text)
    state.learning_goals = json.loads(questions)['learning_goals']

    # Transform learning goals for unity
    retVal = {
        "names": [],
        "intro": [],
        "hard": []
    }
    for goal in state.learning_goals:
        retVal["names"].append(list(goal.keys())[0])
        retVal["intro"].append("$".join(list(list(goal.values())[0][0].values())[0]))
        retVal["hard"].append("$".join(list(list(goal.values())[0][1].values())[0]))

    return retVal


# PDF Processing Routes
@app.post("/addDocument")
def addDocument(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(DATA_DIR + '/' + PDF_PATH + "/" + "data.pdf", 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    #load_pdfs()

    return {"message": f"Successfully uploaded {file.filename}"}


@app.get("/test")
def test():
    print(state.learning_goals[state.curr_goal])
    return {"message": "Test"}
