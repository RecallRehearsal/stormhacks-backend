import os
from fastapi import FastAPI, File, UploadFile
from langchain.chains.flare.prompts import PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from consts import DATA_DIR, PDF_PATH, AUDIO_PATH, SCORE_THRESH, HELP_PROMPT, \
    ANSWER_PROMPT_CHILD, ANSWER_PROMPT_STUDENT, ACCURACY_PROMPT_CHILD, ACCURACY_PROMPT_STUDENT
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

            prompt_template = ChatPromptTemplate.from_template(ANSWER_PROMPT_CHILD if state.curr_question < 2 else ANSWER_PROMPT_STUDENT)
            prompt = prompt_template.format(context=state.input_text, question=getQuestion(), answer=transcription)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt},
                ]
            )

            print("Successfully created response.\nResulting Response: ", response.choices[0].message.content)

            prompt_template_accuracy = ChatPromptTemplate.from_template(ACCURACY_PROMPT_CHILD if state.curr_question < 2 else ACCURACY_PROMPT_STUDENT)
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

            speech_file_path = "static/speech.mp3"
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="nova" if state.curr_question < 2 else "echo",
                input=response.choices[0].message.content + ("Let's Try that again! " + getQuestion() if accuracy_num<SCORE_THRESH else "Let's Continue to the next question")
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
            voice="nova" if state.curr_question < 2 else "echo",
            input=prompt
        )
        print("Successfully created speech from text.\nResulting audio file saved at: ", speech_file_path)
        audio_response.stream_to_file(speech_file_path)
    except:
        print(state.curr_goal, state.curr_question)
        return {"message": "There was an error creating the file"}
    return {"message": "success"}

@app.get("/generateIntro")
def generateIntro():
    try:
        speech_file_path = "static/speech.mp3"
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="nova" if state.curr_question < 2 else "echo",
            input="Welcome to Recall Rehearsal. We're here to help you rehearse for your exam. Let's get recalling with your first question."
        )
        print("Successfully created speech from text.\nResulting audio file saved at: ", speech_file_path)
        audio_response.stream_to_file(speech_file_path)
    except:
        print(state.curr_goal, state.curr_question)
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

            prompt_template = ChatPromptTemplate.from_template(HELP_PROMPT)
            prompt = prompt_template.format(context=state.input_text, question=getQuestion(), inquiry=transcription)
            print(prompt)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt},
                ]
            )

            print("Successfully created help response.\nResulting Response: ", response.choices[0].message.content)

            speech_file_path = "static/speech.mp3"
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input="No problem, I am glad to help. " + response.choices[0].message.content + " I hope this helps you understand the question better."
            )

            print("Successfully created speech from text.\nResulting audio file saved at: ", speech_file_path)
            audio_response.stream_to_file(speech_file_path)

        return {"message": speech_file_path}

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
