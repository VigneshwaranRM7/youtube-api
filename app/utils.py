import time
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from pytube import Playlist
from app.config import WEBSHARE_USERNAME, WEBSHARE_PASSWORD
def is_playlist_url(url: str) -> bool:
    return 'playlist' in url or 'list=' in url

# Extract Video ID
def get_video_id(url: str) -> str:
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        raise ValueError("Invalid YouTube URL")
    except Exception:
        raise ValueError("Could not parse YouTube URL")

# Fetch Transcript
def get_transcript(url, retry_count=3, delay=2):
    """Get transcript from YouTube video with retry mechanism and better error handling."""
    video_id = get_video_id(url)

    for attempt in range(retry_count):
        try:
            # Check if transcript is available before fetching
            available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            if not available_transcripts:
                return {"video_id": video_id, "error": "Transcript not available"}

            # Try fetching the transcript
            transcript_snippets = YouTubeTranscriptApi.get_transcript(video_id)
            formatted_transcript = " ".join(snippet['text'] for snippet in transcript_snippets)

            return {"video_id": video_id, "transcript": formatted_transcript}

        except Exception as e:
            if attempt == retry_count - 1:
                return {"video_id": video_id, "error": str(e)}
            print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff to avoid YouTube rate limits


# Process Playlist
def process_playlist(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        transcripts = []
        for index, video_url in enumerate(playlist.video_urls, 1):
            print(f"\nProcessing video {index}/{len(playlist.video_urls)}...")
            transcript_data = get_transcript(video_url)
            transcripts.append(transcript_data)

            # Increase delay to avoid rate limiting
            if index < len(playlist.video_urls):
                time.sleep(5)

        return {"playlist": transcripts}

    except Exception as e:
        return {"error": f"Error processing playlist: {str(e)}"}


# Process Single Video
def process_single_video(url: str):
    """Fetch transcript for a single video"""
    return get_transcript(url)