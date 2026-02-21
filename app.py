from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import json

app = FastAPI()
templates = Jinja2Templates(directory=".")

# Mock state for the UI
server_state = {
    "inference_status": "Running",
    "client_link": "Connected"
}

@app.get("/", response_class=HTMLResponse)
async def get_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive audio data from the browser (mocked here as text commands for setup)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "start_transcription":
                # In a real app, you would stream audio bytes here and pass them to faster-whisper
                await websocket.send_text(json.dumps({
                    "timestamp": "15:36:03",
                    "text": "A fully local and private."
                }))
                await asyncio.sleep(2)
                await websocket.send_text(json.dumps({
                    "timestamp": "15:36:07",
                    "text": "Speech-to-text app for Linux, Windows and Mac OS."
                }))
                await asyncio.sleep(2)
                await websocket.send_text(json.dumps({
                    "timestamp": "15:36:13",
                    "text": "It has a Python backend plus a web frontend."
                }))
                
    except Exception as e:
        print(f"Connection closed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
