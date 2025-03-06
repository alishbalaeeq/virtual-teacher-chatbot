const startButton = document.getElementById('start-button');
const recordButton = document.getElementById('record-button');
const chatHistory = document.getElementById('chat-history');
const topicInput = document.getElementById('topic-input');
const loadingMessage = document.getElementById('loading-message'); // Fix: Define the loading message

let isRecording = false;
let mediaRecorder;
let audioChunks = [];

// Hide the record button initially
recordButton.style.display = 'none';

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

document.addEventListener('DOMContentLoaded', function() {
    startButton.addEventListener('click', async function() {
        const topic = topicInput.value.trim();
        if (!topic) {
            alert('Please enter a topic to start the lecture.');
            return;
        }

        startButton.style.display = 'none';
        topicInput.style.display = 'none';
        recordButton.style.display = 'none'; // Ensure record button is hidden
        loadingMessage.style.display = 'block'; // Show loading message

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

            // Create a wrapper div for the lecture message
            const messageContainer = document.createElement('div');
            messageContainer.classList.add('chat-message', 'bot-audio'); // Use bot-audio styling

            // Add "Lecture" label
            const lectureLabel = document.createElement('span');
            lectureLabel.textContent = 'Lecture';
            lectureLabel.classList.add('bot-label'); // Use bot-label styling

            // Create and configure audio element
            const audioElement = document.createElement('audio');
            audioElement.src = audioUrl;
            audioElement.controls = true;
            audioElement.autoplay = true;

            // Append label and audio to the message container
            messageContainer.appendChild(lectureLabel);
            messageContainer.appendChild(audioElement);
            chatHistory.appendChild(messageContainer);

            // ✅ Auto-scroll to the latest message
            scrollToBottom();

            // Hide loading message & show record button after lecture is generated
            loadingMessage.style.display = 'none';
            recordButton.style.display = 'block'; // Make the record button visible

        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
            startButton.style.display = 'block'; // Re-display the start button if there's an error
            loadingMessage.style.display = 'none';
        }
    });
});

recordButton.addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener('stop', async () => {
            await processRecordedAudio(audioChunks);
        });

        mediaRecorder.start();
        isRecording = true;
        recordButton.textContent = 'Stop Recording';
    } catch (err) {
        console.error('Error accessing microphone:', err);
    }
}

async function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        isRecording = false;
        recordButton.textContent = 'Record / Stop';
    }
}

async function processRecordedAudio(audioChunks) {
    const blob = new Blob(audioChunks, { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(blob);
    const audio = document.createElement('audio');
    audio.src = audioUrl;
    audio.controls = true;

    const messageContainer = document.createElement('div');
    messageContainer.classList.add('chat-message', 'user-audio');
    messageContainer.appendChild(audio);

    const userLabel = document.createElement('span');
    userLabel.textContent = 'Student';
    userLabel.classList.add('user-label');
    messageContainer.appendChild(userLabel);

    chatHistory.appendChild(messageContainer);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    await sendAudioToServer(blob);
}

async function sendAudioToServer(blob) {
    const formData = new FormData();
    const topic = document.getElementById('topic-input').value.trim();
    formData.append('voice_chat', blob, 'user_audio.wav');
    formData.append('topic', topic);

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


