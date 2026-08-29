from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
import os
import tempfile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import asyncio
import anyio
from vision import VisionProcessor

app = FastAPI()

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = VisionProcessor()

# Pydantic model for settings update
class Settings(BaseModel):
    mode: str = None
    fog_strength: int = None
    brightness: int = None
    contrast: int = None
    split_screen: bool = False
    edge_highlight: bool = False

import anyio

async def generate_frames():
    while True:
        # Rate limit slightly to prevent CPU max out on older devices
        # Target ~30fps max
        await asyncio.sleep(0.03) 
        
        # Run synchronous OpenCV processing in a background thread to prevent blocking event loop
        frame_bytes = await anyio.to_thread.run_sync(processor.get_frame)
        # Yield the frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/api/settings")
def update_settings(settings: Settings):
    processor.update_settings(
        mode=settings.mode,
        fog_strength=settings.fog_strength,
        brightness=settings.brightness,
        contrast=settings.contrast,
        split_screen=settings.split_screen,
        edge_highlight=settings.edge_highlight
    )
    return {"status": "success", "settings": settings}

@app.get("/api/settings")
def get_settings():
    return {
        "mode": processor.mode,
        "fog_strength": processor.fog_strength,
        "brightness": processor.brightness,
        "contrast": processor.contrast,
        "split_screen": processor.split_screen,
        "edge_highlight": processor.edge_highlight
    }

@app.post("/upload_video")
async def upload_video(request: Request):
    filename = request.query_params.get("filename", "uploaded_video.mp4")
    print(f"Upload started for file: {filename}")
    
    # Save the uploaded file to a temporary location
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await request.body()
        buffer.write(content)
        
    # Set the video source in the processor in a background thread
    await anyio.to_thread.run_sync(processor.set_video_source, file_path)
    
    return {"status": "success", "filename": filename, "message": "Video uploaded successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
