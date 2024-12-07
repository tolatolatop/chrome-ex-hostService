html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket 聊天</title>
        <style>
            .system { color: gray; }
            .error { color: red; }
            .chat { color: black; }
        </style>
    </head>
    <body>
        <h1>WebSocket 聊天示例</h1>
        <div>
            <label for="username">用户名:</label>
            <input type="text" id="username" value="游客" />
        </div>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>发送</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var data = JSON.parse(event.data)
                
                message.className = data.type
                var time = new Date(data.timestamp).toLocaleTimeString()
                var content = document.createTextNode(`[${time}] ${data.sender}: ${data.content}`)
                
                message.appendChild(content)
                messages.appendChild(message)
            };
            
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                var username = document.getElementById("username")
                
                if (input.value) {
                    var message = {
                        type: "chat",
                        content: input.value,
                        sender: username.value
                    }
                    ws.send(JSON.stringify(message))
                    input.value = ''
                }
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
