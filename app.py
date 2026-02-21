import os
import json
import tempfile
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from faster_whisper import WhisperModel
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory=".")

# Initialize the Whisper model. 'base' or 'tiny' are best for real-time.
print("Loading Vscriber AI Model...")
model_size = "base"
# Run on CPU with int8 for compatibility, change device="cuda" if you have an Nvidia GPU
model = WhisperModel(model_size, device="cpu", compute_type="int8")
print("Model loaded successfully!")

@app.get("/", response_class=HTMLResponse)
async def get_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive audio blob from the browser
            audio_bytes = await websocket.receive_bytes()
            
            # Save the chunk to a temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name

            try:
                # Transcribe the audio chunk
                segments, info = model.transcribe(tmp_file_path, beam_size=5)
                
                transcription = ""
                for segment in segments:
                    transcription += segment.text + " "

                if transcription.strip():
                    # Send back the transcription with a timestamp
                    current_time = datetime.now().strftime("%H:%M:%S")
                    response = {
                        "timestamp": current_time,
                        "text": transcription.strip()
                    }
                    await websocket.send_text(json.dumps(response))
            finally:
                # Clean up the temp file
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

    except Exception as e:
        print(f"WebSocket connection closed or error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
