from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from utils.llm import generation_model, generate_lecture
from utils.tts import text_to_speech
from utils.stt import speech_to_text
import uvicorn
import os

app = FastAPI()

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount templates as a static directory to serve CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory="files"), name="files")

# Path for generated lecture file
LECTURE_FILE_PATH = os.path.join(FILES_DIR, "Lecture.wav")

def generate_lecture_file(topic):
    """
    Function to generate Lecture using Mistral LLM.
    """
    lecture = generate_lecture(topic)
    print("Lecture has been generated successfully.")
    print(lecture)
    return lecture

@app.on_event("startup")
async def on_startup():
    topic = "Climate Change"
    voice = "en-IE-EmilyNeural"
    lecture = generate_lecture_file(topic)
    text_to_speech(voice, lecture, LECTURE_FILE_PATH)

@app.get("/")
async def index():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("files/favicon.ico")

@app.get("/startconv")
async def start_conversation():
    if os.path.exists(LECTURE_FILE_PATH):
        return FileResponse(LECTURE_FILE_PATH, media_type="audio/wav", filename="Lecture.wav")
    return {"error": "Lecture.wav not found"}

@app.post("/chat")
async def chat(voice_chat: UploadFile = File(...)):
    if not voice_chat:
        return {"error": "No audio file uploaded"}
    
    uploaded_file_path = os.path.join(FILES_DIR, f"uploaded_{voice_chat.filename}")
    with open(uploaded_file_path, "wb") as f:
        f.write(await voice_chat.read())

    print(f"Received file: {uploaded_file_path}")

    # Convert speech to text (STT)
    question_text = speech_to_text(uploaded_file_path)
    print(f"Extracted text from audio: {question_text}")

    # Generate a response using the LLM
    response_text = generation_model(question_text)
    print(f"LLM Response: {response_text}")

    generated_response_path = os.path.join(FILES_DIR, "Response.wav")

    # Convert text to speech (TTS)
    text_to_speech("en-IE-EmilyNeural", response_text, generated_response_path)

    return FileResponse(generated_response_path, media_type="audio/wav", filename="Response.wav")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)