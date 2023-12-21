 window.addEventListener('DOMContentLoaded',function () {
        const courseId = JSON.parse(
            document.getElementById('course-id').textContent
        );

        const requestUser = JSON.parse(
            document.getElementById('request-user').textContent
        );


        const url = 'ws://' + window.location.host +'/ws/chat/room/' + courseId + '/';
        const chatSocket = new WebSocket(url);
        
        chatSocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Timestamp from server:', data);
            // Ajouter votre logique ici pour mettre à jour l'affichage avec le nouveau message
            const chat = document.querySelector('.chat');
            const isMe = data.user === requestUser;
            const source = isMe ? 'right' : 'left';
        
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + source + ' pb-4';
        
            const userImage = document.createElement('img');
            userImage.src = 'https://bootdey.com/img/Content/avatar/avatar1.png';
            userImage.className = 'rounded-circle mr-1';
            userImage.alt = 'User Image';
            userImage.width = 40;
            userImage.height = 40;
        
            const userDiv = document.createElement('div');
            userDiv.appendChild(userImage);

            console.log('Timestamp from server:', data.datetime);
            const textMutedDiv = document.createElement('div');
            textMutedDiv.className = 'text-muted small text-nowrap mt-2';
            textMutedDiv.textContent = new Date(data.datetime).toLocaleString('en', { hour: 'numeric', minute: 'numeric', hour12: true });

    
            userDiv.appendChild(textMutedDiv);
        
            messageDiv.appendChild(userDiv);
        
            const messageContentDiv = document.createElement('div');
            messageContentDiv.className = 'message-content flex-shrink-1 bg-light rounded py-2 px-3 mr-3';
        
            if (!isMe) {
                const usernameDiv = document.createElement('div');
                usernameDiv.className = 'username font-weight-bold mb-1';
                const strongElement = document.createElement('strong');
                strongElement.textContent = data.user.username;
                usernameDiv.appendChild(strongElement);
                messageContentDiv.appendChild(usernameDiv);
            }
        
            const contentSpan = document.createElement('span');
            contentSpan.textContent = data.message;
            messageContentDiv.appendChild(contentSpan);
        
            messageDiv.appendChild(messageContentDiv);
        
            chat.appendChild(messageDiv);
        
            chat.scrollTop = chat.scrollHeight;
        
            if (data.next_message) {
                if (data.timestamp.date !== data.next_message.timestamp.date) {
                    const hrElement = document.createElement('hr');
                    chat.appendChild(hrElement);
        
                    const textCenterDiv = document.createElement('div');
                    textCenterDiv.className = 'text-center text-muted small mb-3';
                    textCenterDiv.textContent = new Date(data.next_message.timestamp).toLocaleString('en', { year: 'numeric', month: 'long', day: 'numeric' });
        
                    chat.appendChild(textCenterDiv);
                }
            }
        };
        
        chatSocket.onclose = function(event) {
                    console.error('Chat socket closed unexpectedly');
        };
        

        const input = document.getElementById('chat-message-input');
        const submitButton = document.getElementById('chat-message-submit');

        submitButton.addEventListener('click', function(event) {
            const message = input.value;
            if(message) {
            // send message in JSON format
                chatSocket.send(JSON.stringify({'message': message}));
                // clear input
                input.innerHTML = '';
                input.focus();
            }
        });

        input.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                // cancel the default action, if needed
                event.preventDefault();
                // trigger click event on button
                submitButton.click();
            }
        });
        
        input.focus();
    });
