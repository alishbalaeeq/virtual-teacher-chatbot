from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from utils.llm import generation_model, generate_lecture
from utils.tts import text_to_speech
from utils.stt import speech_to_text
from pydub import AudioSegment
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
    """
    Handles audio file upload, converts it to WAV, processes STT, 
    gets an AI response, and converts it to speech.
    """
    if not voice_chat:
        return JSONResponse(content={"error": "No voice chat found"}, status_code=400)

    topic = "Climate change"

    # Define file paths
    raw_file_path = os.path.join(FILES_DIR, voice_chat.filename)
    output_file_path = os.path.join(FILES_DIR, "student.wav")
    generated_response_path = os.path.join(FILES_DIR, "Response.wav")

    try:
        # Ensure the directory exists
        os.makedirs(FILES_DIR, exist_ok=True)

        # Save the uploaded file
        with open(raw_file_path, "wb") as f:
            f.write(await voice_chat.read())

        print(f"Received file: {raw_file_path}")

        # Convert the file to WAV format (16kHz mono)
        audio = AudioSegment.from_file(raw_file_path)
        audio = audio.set_frame_rate(16000).set_channels(1)  # Ensure correct format
        audio.export(output_file_path, format="wav")

        print(f"Converted file saved at: {output_file_path}")

        # Convert speech to text (STT)
        question_text = speech_to_text(output_file_path)
        print(f"Extracted text from audio: {question_text}")

        # Generate a response using the LLM
        response_text = generation_model(question_text, topic)
        print(f"LLM Response: {response_text}")

        # Convert text to speech (TTS)
        text_to_speech("en-IE-EmilyNeural", response_text, generated_response_path)

        print(f"Generated response audio saved at: {generated_response_path}")

        # Return the generated response audio file
        return FileResponse(generated_response_path, media_type="audio/wav", filename="Response.wav")

    except Exception as e:
        return JSONResponse(content={"error": f"Failed to process file: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)