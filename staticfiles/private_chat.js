window.addEventListener('DOMContentLoaded', function () {
    const otherUserId = JSON.parse(
        document.getElementById('other-user-id').textContent
    );

    const requestUser = JSON.parse(
        document.getElementById('request-user').textContent
    );

    const url = 'ws://' + window.location.host + '/ws/chat/private/' + otherUserId + '/';
    const chatSocket = new WebSocket(url);

    chatSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        const chat = document.getElementById('chat');

        const dateOptions = { hour: 'numeric', minute: 'numeric', hour12: true };
        const datetime = new Date(data.datetime).toLocaleString('en', dateOptions);
        const isMe = data.user === requestUser;
        const source = isMe ? 'me' : 'other';
        const name = isMe ? 'Me' : data.user;

        chat.innerHTML += '<div class="message ' + source + '">' +
            '<strong>' + name + '</strong> ' +
            '<span class="date">' + datetime + '</span><br>' +
            data.message + '</div>';
        chat.scrollTop = chat.scrollHeight;
    };

    chatSocket.onclose = function (event) {
        console.error('Chat socket closed unexpectedly');
    };

    const input = document.getElementById('chat-message-input');
    const submitButton = document.getElementById('chat-message-submit');

    submitButton.addEventListener('click', function (event) {
        const message = input.value;
        if (message) {
            // send message in JSON format
            chatSocket.send(JSON.stringify({ 'message': message }));
            // clear input
            input.value = '';
            input.focus();
        }
    });

    input.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            // cancel the default action, if needed
            event.preventDefault();
            // trigger click event on button
            submitButton.click();
        }
    });

    input.focus();
});