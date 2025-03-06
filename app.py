from utils.llm import generation_model, generate_lecture
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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
LECTURE_FILE_PATH = os.path.join(FILES_DIR, "Lecture.wav")

# Mount templates as a static directory to serve CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory="files"), name="files")

def generate_lecture_file(topic):
    """
    Function to generate Lecture using Mistral LLM.
    """
    lecture = generate_lecture(topic)
    print("Lecture has been generated successfully.")
    print(lecture)
    return lecture


@app.post("/generate-lecture")
async def generate_lecture_endpoint(topic: str = Form(...)):
    if not topic:
        return JSONResponse(content={"error": "No topic provided"}, status_code=400)
    
    try:
        lecture_text = generate_lecture(topic)  # Assume this function generates the lecture text
        text_to_speech("en-IE-EmilyNeural", lecture_text, LECTURE_FILE_PATH)  # Convert text to speech

        # Check if the lecture file exists and return it
        if os.path.exists(LECTURE_FILE_PATH):
            return FileResponse(LECTURE_FILE_PATH, media_type="audio/wav", filename="Lecture.wav")
        else:
            raise FileNotFoundError("Failed to generate lecture file.")
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to generate lecture: {str(e)}"}, status_code=500)


@app.get("/")
async def index():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("files/favicon.ico")


@app.post("/chat")
async def chat(voice_chat: UploadFile = File(...)):
    if not voice_chat:
        return JSONResponse(content={"error": "No voice chat found"}, status_code=400)

    raw_file_path = os.path.join(FILES_DIR, voice_chat.filename)
    output_file_path = os.path.join(FILES_DIR, "student.wav")
    generated_response_path = os.path.join(FILES_DIR, "Response.wav")

    try:
        with open(raw_file_path, "wb") as f:
            f.write(await voice_chat.read())

        audio = AudioSegment.from_file(raw_file_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_file_path, format="wav")

        question_text = speech_to_text(output_file_path)
        response_text = generation_model(question_text)
        text_to_speech("en-IE-EmilyNeural", response_text, generated_response_path)

        return FileResponse(generated_response_path, media_type="audio/wav", filename="Response.wav")
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to process file: {str(e)}"}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)