from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from utils.llm import generation_model
from utils.tts import text_to_speech
import uvicorn
import os

app = FastAPI()

# Path for generated lecture file
LECTURE_FILE_PATH = "Lecture.wav"

def generate_lecture_file(topic):
    """
    Function to generate Lecture using Mistral LLM.
    """
    # Simulating LLM-generated audio file
    lecture = generation_model(topic)
    print("Lecture.wav generated successfully.")

    return lecture

@app.on_event("startup")
async def on_startup():
    # Generate lecture file on startup
    topic = "Climate Change"
    voice = "en-US-AndrewMultilingualNeural"
    lecture = generate_lecture_file(topic)
    text_to_speech(voice, lecture, LECTURE_FILE_PATH)

@app.get("/")
async def index():
    # Serve the frontend index.html
    return FileResponse("index.html")

@app.get("/startconv")
async def start_conversation():
    # Send the generated Lecture.wav file
    if os.path.exists(LECTURE_FILE_PATH):
        return FileResponse(LECTURE_FILE_PATH, media_type="audio/wav", filename="Lecture.wav")
    return {"error": "Lecture.wav not found"}

@app.post("/chat")
async def chat(voice_chat: UploadFile = File(...)):
    """
    Handle chat audio upload.
    """
    if not voice_chat:
        return {"error": "No audio file uploaded"}
    
    # Save the uploaded file
    uploaded_file_path = f"uploaded_{voice_chat.filename}"
    with open(uploaded_file_path, "wb") as f:
        f.write(await voice_chat.read())
    
    # Mock LLM response (Replace this with actual processing)
    print(f"Received file: {uploaded_file_path}")
    generated_response_path = "Response.wav"
    with open(generated_response_path, "wb") as f:
        f.write(b"This is a mock response audio file.")  # Replace with actual LLM audio response

    # Return the response audio file
    return FileResponse(generated_response_path, media_type="audio/wav", filename="Response.wav")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)