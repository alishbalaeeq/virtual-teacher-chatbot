# Virtual Teacher Student Chatbot

## Overview

The **Virtual Teacher Chatbot** is a speech-to-speech AI-powered application that delivers interactive lectures on specified topics and allows users to engage by asking questions. The chatbot utilizes open-source Large Language Models (LLMs) for content generation and Text-to-Speech (TTS)/Speech-to-Text (STT) models for voice interaction.

## Features

- **AI-Generated Lectures**: The chatbot delivers informative lectures on user-specified topics.
- **Speech-to-Speech Interaction**: Users can ask questions verbally, and the chatbot responds with a voice-generated answer.
- **Open-Source Models**: Uses publicly available LLMs, TTS, and STT models for processing and interaction.
- **Real-Time Response**: Ensures smooth conversation flow between the user and the virtual teacher.
- **Multi-Language Support**: Can be extended to support multiple languages for diverse learning experiences.

## Technologies Used

- **LLMs**: Open-source language models for generating lecture content and answering questions.
- **TTS Models**: Converts the generated text responses into speech.
- **STT Models**: Transcribes the user's speech input into text for processing.
- **Python & FastAPI**: Backend to handle requests and responses.
- **Torchaudio**: Used for processing the audio input from the frontend.

## Installation & Setup

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/alishbalaeeq/virtual-teacher-chatbot.git
   cd virtual-teacher-chatbot
   ```

2. **Create a Virtual Environment (Optional but Recommended)**:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```sh
   uvicorn app:app --port 8000
   ```

5. **Access the API**:
   The application runs on `http://localhost:8000` (FastAPI).

## Usage

1. Start the application and select a lecture topic.
2. The chatbot will generate and deliver an audio lecture.
3. Ask questions by speaking, and the bot will process your query and respond accordingly.
4. Continue the interactive session as needed.

## Future Enhancements

- Support for personalized learning paths.
- More advanced natural-sounding TTS voices.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Open a pull request.

## Contact

For any questions or collaboration requests, reach out to **[alishbalaeeq@gmail.com](mailto:alishbalaeeq@gmail.com)** or visit our [GitHub Issues](https://github.com/alishbalaeeq/virtual-teacher-chatbot/issues).