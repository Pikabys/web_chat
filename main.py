from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

connected_clients = []
message_queue = []

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    connected_clients.append({"websocket": websocket, "username": username})
    
    welcome_message = f"Привет, {username}!"
    await websocket.send_text(welcome_message)

    for message in message_queue:
        await websocket.send_text(message)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            message_queue.append(message)

            for client in connected_clients:
                await client["websocket"].send_text(message)

    except WebSocketDisconnect:
        print(f"{username} отключился")
        connected_clients[:] = [
            client for client in connected_clients
            if client["websocket"] != websocket
        ]
