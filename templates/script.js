document.addEventListener('DOMContentLoaded', () => {
    // Universal navigation active link handling
    const currentPath = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else if (currentPath === '' && link.getAttribute('href') === 'index.html') {
            link.classList.add('active'); // For root path
        }
    });

    // Chatbot specific logic
    if (document.body.classList.contains('chatbot-page')) {
        const fileUpload = document.getElementById('file-upload');
        const uploadBtn = document.querySelector('.upload-btn');
        const uploadedFilesList = document.getElementById('uploaded-files-list');
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.querySelector('.send-button');
        const chatMessages = document.getElementById('chat-messages');
        const voiceButton = document.querySelector('.voice-button');

        let uploadedFiles = [];

        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => {
                fileUpload.click();
            });
        }

        if (fileUpload) {
            fileUpload.addEventListener('change', (event) => {
                const files = event.target.files;
                if (files.length > 0) {
                    for (let i = 0; i < files.length; i++) {
                        const file = files[i];
                        if (!uploadedFiles.some(f => f.name === file.name)) { // Prevent duplicate uploads by name
                            uploadedFiles.push(file);
                            renderUploadedFiles();
                        }
                    }
                }
                // Clear the input so the same file can be selected again if needed
                fileUpload.value = '';
            });
        }

        function renderUploadedFiles() {
            if (uploadedFilesList) {
                uploadedFilesList.innerHTML = '';
                if (uploadedFiles.length === 0) {
                    uploadedFilesList.innerHTML = '<li style="text-align: center;">No files uploaded yet.</li>';
                } else {
                    uploadedFiles.forEach((file, index) => {
                        const li = document.createElement('li');
                        li.textContent = file.name;
                        const removeBtn = document.createElement('span');
                        removeBtn.textContent = 'x';
                        removeBtn.classList.add('remove-file');
                        removeBtn.addEventListener('click', () => {
                            uploadedFiles.splice(index, 1);
                            renderUploadedFiles();
                        });
                        li.appendChild(removeBtn);
                        uploadedFilesList.appendChild(li);
                    });
                }
            }
        }

        function appendMessage(sender, text) {
            if (chatMessages) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message', `${sender}-message`);
                const contentDiv = document.createElement('div');
                contentDiv.classList.add('message-content');
                contentDiv.textContent = text;
                messageDiv.appendChild(contentDiv);
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
            }
        }

        async function sendMessage() {
            const userQuestion = chatInput.value.trim();
            if (userQuestion === '') return;

            appendMessage('user', userQuestion);
            chatInput.value = ''; // Clear input immediately

            // Simulate API call (replace with actual backend integration)
            // In a real scenario, you'd send `userQuestion` and `uploadedFiles` to your Python backend
            // For now, let's simulate a bot response after a delay.
            try {
                // Here you would make an API call to your Flask/FastAPI backend
                // Example:
                // const formData = new FormData();
                // formData.append('question', userQuestion);
                // uploadedFiles.forEach(file => {
                //     formData.append('files', file);
                // });
                // const response = await fetch('/api/chat', {
                //     method: 'POST',
                //     body: formData
                // });
                // const data = await response.json();
                // appendMessage('bot', data.answer);

                // --- Simulated response ---
                const botResponse = await new Promise(resolve => setTimeout(() => {
                    if (uploadedFiles.length > 0) {
                        resolve(`Thanks for your question "${userQuestion}"! I've processed your files: ${uploadedFiles.map(f => f.name).join(', ')}. Please wait for a detailed answer from the AI.`);
                    } else {
                        resolve(`Thanks for your question "${userQuestion}"! I'll try to answer that for you. If you have any PDFs, feel free to upload them.`);
                    }
                }, 1500));
                appendMessage('bot', botResponse);
                // --- End Simulated response ---

            } catch (error) {
                console.error('Error sending message:', error);
                appendMessage('bot', 'Oops! Something went wrong. Please try again.');
            }
        }

        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault(); // Prevent new line on Enter
                    sendMessage();
                }
            });
        }

        // Voice input (integrates with your voice_to_text.py if exposed via API)
        if (voiceButton) {
            voiceButton.addEventListener('click', async () => {
                console.log("Voice input button clicked.");
                appendMessage('user', 'Listening for your voice...'); // Provide feedback

                // In a real application, you'd trigger your voice_to_text.py script
                // via an API endpoint that handles the recording and transcription.
                try {
                    // Simulate API call to your voice_to_text backend endpoint
                    const response = await fetch('/api/record_voice', {
                        method: 'POST',
                        // You might need to send a signal to your backend to start listening
                    });
                    const data = await response.json();
                    if (data.text) {
                        chatInput.value = data.text;
                        appendMessage('bot', `Transcribed: "${data.text}"`);
                        // Optionally, send the message immediately after transcription
                        // sendMessage();
                    } else {
                        appendMessage('bot', 'Could not recognize voice. Please try again.');
                    }
                } catch (error) {
                    console.error('Error during voice input:', error);
                    appendMessage('bot', 'Voice recognition failed. Make sure your microphone is working and try again.');
                }
            });
        }
        
        // Initial render for uploaded files
        renderUploadedFiles();
    }
});