const startButton = document.getElementById('start-button');
const recordButton = document.getElementById('record-button');
const chatHistory = document.getElementById('chat-history');

let isRecording = false;

startButton.addEventListener('click', startConversation);

async function startConversation() {
    startButton.style.display = 'none';
    try {
        // Fetch the bot's first audio message (Hello.wav) from the server
        const response = await fetch('/startconv');
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        // Create an <audio> element for the bot's audio message
        const botAudioElement = document.createElement('audio');
        botAudioElement.src = audioUrl;
        botAudioElement.controls = true;

        // Create a container for the bot's message
        const botMessageContainer = document.createElement('div');
        botMessageContainer.classList.add('chat-message');
        botMessageContainer.classList.add('bot-audio');
        botMessageContainer.appendChild(botAudioElement);

        // Add bot label
        const botLabel = document.createElement('span');
        botLabel.textContent = 'Teacher';
        botLabel.classList.add('bot-label');
        botMessageContainer.appendChild(botLabel);

        // Append the bot's message container to the chat history
        chatHistory.appendChild(botMessageContainer);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        // Show record button after starting the conversation
        recordButton.style.display = 'block';
    } catch (error) {
        console.error('Error starting conversation:', error);
    }
}

recordButton.addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            const chunks = [];

            mediaRecorder.addEventListener('dataavailable', event => {
                chunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', async () => {
                const blob = new Blob(chunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(blob);

                const audio = document.createElement('audio');
                audio.src = audioUrl;
                audio.controls = true;

                const messageContainer = document.createElement('div');
                messageContainer.classList.add('chat-message');
                messageContainer.classList.add('user-audio');
                messageContainer.appendChild(audio);

                // Add user label
                const userLabel = document.createElement('span');
                userLabel.textContent = 'Student';
                userLabel.classList.add('user-label');
                messageContainer.appendChild(userLabel);

                chatHistory.appendChild(messageContainer);
                chatHistory.scrollTop = chatHistory.scrollHeight;

                // Send recorded audio to the server
                const formData = new FormData();
                formData.append('voice_chat', blob, 'user_audio.wav');

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        // Bot's response received from server
                        const botAudioUrl = await response.blob();
                        const botAudioElement = document.createElement('audio');
                        botAudioElement.src = URL.createObjectURL(botAudioUrl);
                        botAudioElement.controls = true;

                        const botMessageContainer = document.createElement('div');
                        botMessageContainer.classList.add('chat-message');
                        botMessageContainer.classList.add('bot-audio');
                        botMessageContainer.appendChild(botAudioElement);

                        // Add bot label
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

                chunks.length = 0;
            });

            mediaRecorder.start();
            isRecording = true;
            recordButton.textContent = 'Stop Recording';
        } catch (err) {
            console.error('Error accessing microphone:', err);
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        recordButton.textContent = 'Record / Stop';
    }
}
