from fastapi import FastAPI
from pydantic import BaseModel
from app.utils import get_transcript, process_playlist

app = FastAPI(title="YouTube Transcript API", version="1.0")

class YouTubeRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"message": "YouTube Transcript API is running!"}

@app.post("/get_transcript")
def fetch_transcript(request: YouTubeRequest):
    """Fetch transcript for a single video or playlist"""
    if "list=" in request.url:
        return {"playlist": process_playlist(request.url)}
    return get_transcript(request.url)

