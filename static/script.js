const startButton = document.getElementById('start-button');
const recordButton = document.getElementById('record-button');
const chatHistory = document.getElementById('chat-history');
const topicInput = document.getElementById('topic-input');  // Assuming you have an input field for topics

let isRecording = false;

document.addEventListener('DOMContentLoaded', function() {

    startButton.addEventListener('click', async function() {
        const topic = topicInput.value.trim();
        if (!topic) {
            alert('Please enter a topic to start the lecture.');
            return;
        }

        startButton.style.display = 'none';

        try {
            const response = await fetch('/generate-lecture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `topic=${encodeURIComponent(topic)}`
            });

            if (!response.ok) {
                throw new Error('Failed to generate lecture.');
            }

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audioElement = document.createElement('audio');
            audioElement.src = audioUrl;
            audioElement.controls = true;
            audioElement.autoplay = true;

            chatHistory.appendChild(audioElement);
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
            startButton.style.display = 'block';  // Re-display the start button if there's an error
        }
    });
});

recordButton.addEventListener('click', toggleRecording);

async function toggleRecording() {
    // Record button toggles the recording state
    if (!isRecording) {
        // Start recording
        startRecording();
    } else {
        // Stop recording
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const chunks = [];

        mediaRecorder.addEventListener('dataavailable', event => {
            chunks.push(event.data);
        });

        mediaRecorder.addEventListener('stop', async () => {
            // Process the recorded audio after stopping
            processRecordedAudio(chunks);
        });

        mediaRecorder.start();
        isRecording = true;
        recordButton.textContent = 'Stop Recording';
    } catch (err) {
        console.error('Error accessing microphone:', err);
    }
}

async function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    recordButton.textContent = 'Record / Stop';
}

async function processRecordedAudio(chunks) {
    const blob = new Blob(chunks, { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(blob);
    const audio = document.createElement('audio');
    audio.src = audioUrl;
    audio.controls = true;

    const messageContainer = document.createElement('div');
    messageContainer.classList.add('chat-message', 'user-audio');
    messageContainer.appendChild(audio);

    // Add a user label
    const userLabel = document.createElement('span');
    userLabel.textContent = 'Student';
    userLabel.classList.add('user-label');
    messageContainer.appendChild(userLabel);

    chatHistory.appendChild(messageContainer);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Send the recorded audio to the server
    await sendAudioToServer(blob);
}

async function sendAudioToServer(blob) {
    const formData = new FormData();
    formData.append('voice_chat', blob, 'user_audio.wav');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const botAudioBlob = await response.blob();
            const botAudioElement = document.createElement('audio');
            botAudioElement.src = URL.createObjectURL(botAudioBlob);
            botAudioElement.controls = true;

            const botMessageContainer = document.createElement('div');
            botMessageContainer.classList.add('chat-message', 'bot-audio');
            botMessageContainer.appendChild(botAudioElement);

            const botLabel = document.createElement('span');
            botLabel.textContent = 'Teacher';
            botLabel.classList.add('bot-label');
            botMessageContainer.appendChild(botLabel);

            chatHistory.appendChild(botMessageContainer);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        } else {
            console.error('Error receiving bot audio from server');
        }
    } catch (err) {
        console.error('Error sending audio to server:', err);
    }
}
