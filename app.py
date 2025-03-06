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
async def chat(voice_chat: UploadFile = File(...), topic: str = Form(...)):
    try:
        print(f"📢 Received file: {voice_chat.filename}, Size: {voice_chat.size}")
        print(f"📌 Topic received: {topic}")

        raw_file_path = os.path.join(FILES_DIR, voice_chat.filename)
        output_file_path = os.path.join(FILES_DIR, "student.wav")
        generated_response_path = os.path.join(FILES_DIR, "Response.wav")

        # Save received file
        with open(raw_file_path, "wb") as f:
            f.write(await voice_chat.read())

        # Convert audio format
        try:
            audio = AudioSegment.from_file(raw_file_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_file_path, format="wav")
        except Exception as audio_error:
            print(f"❌ Audio processing failed: {audio_error}")
            return JSONResponse(content={"error": f"Audio processing failed: {audio_error}"}, status_code=500)

        # Speech-to-text (STT)
        try:
            from utils.stt import speech_to_text  # Ensure this is correctly imported
            question_text = speech_to_text(output_file_path)
        except Exception as stt_error:
            print(f"❌ Speech-to-text failed: {stt_error}")
            return JSONResponse(content={"error": f"Speech-to-text failed: {stt_error}"}, status_code=500)

        # Generate response using LLM
        try:
            from utils.llm import generation_model  # Ensure this is correctly imported
            response_text = generation_model(question_text, topic)
        except Exception as llm_error:
            print(f"❌ LLM failed: {llm_error}")
            return JSONResponse(content={"error": f"LLM generation failed: {llm_error}"}, status_code=500)

        # Convert text response to speech
        try:
            text_to_speech("en-IE-EmilyNeural", response_text, generated_response_path)
        except Exception as tts_error:
            print(f"❌ Text-to-speech failed: {tts_error}")
            return JSONResponse(content={"error": f"Text-to-speech failed: {tts_error}"}, status_code=500)

        # Return response audio file
        if os.path.exists(generated_response_path):
            return FileResponse(generated_response_path, media_type="audio/wav", filename="Response.wav")
        else:
            print("❌ Response file not found.")
            return JSONResponse(content={"error": "Response file not found"}, status_code=500)

    except Exception as e:
        print(f"❌ General Error: {e}")
        return JSONResponse(content={"error": f"Failed to process file: {str(e)}"}, status_code=500)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)