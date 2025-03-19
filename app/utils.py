import time
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from pytube import Playlist
from app.config import WEBSHARE_USERNAME, WEBSHARE_PASSWORD
def is_playlist_url(url):
    """Check if the URL is a playlist"""
    return 'playlist' in url or 'list=' in url

def get_video_id(url):
    """Extract video ID from YouTube URL"""
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

def get_transcript(url, retry_count=3, delay=1):
    """Get transcript from YouTube video with retry mechanism"""
    ytt_api = YouTubeTranscriptApi(
        proxy_config=WebshareProxyConfig(
            proxy_username=WEBSHARE_USERNAME,
            proxy_password=WEBSHARE_PASSWORD,
        )
    )
    for attempt in range(retry_count):
        try:
            video_id = get_video_id(url)
            transcript_list = ytt_api.fetch(video_id)
            # Format transcript
            transcript_list = list(transcript_list)
            print(transcript_list)
            formatted_transcript = ''
            for snippet in transcript_list:
                formatted_transcript +=  f"{snippet.text} "
            # for entry in transcript_list:
            #     formatted_transcript += f"[{entry['start']:.2f}s] {entry['text']}\n"
                
            return formatted_transcript, video_id
        
        except Exception as e:
            if attempt == retry_count - 1:  # Last attempt
                return f"Error getting transcript: {str(e)}", None
            print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

def process_playlist(playlist_url):
    """Process all videos in a playlist"""
    try:
        playlist = Playlist(playlist_url)
        print(f"\nProcessing playlist: {playlist.title}")
        print(f"Found {len(playlist.video_urls)} videos")
        transcripts = []
        for index, video_url in enumerate(playlist.video_urls, 1):
            print(f"\nProcessing video {index}/{len(playlist.video_urls)}")
            transcript, video_id = get_transcript(video_url)
            payload = {
                "video_id": video_id,
                "transcript": transcript
            }
            transcripts.append(payload)
            
            # Add a small delay between videos to be nice to YouTube
            if index < len(playlist.video_urls):
                time.sleep(2)
        return transcripts
                
    except Exception as e:
        print(f"Error processing playlist: {str(e)}")

def process_single_video(url):
    """Process a single video"""
    transcript, video_id = get_transcript(url)
    payload = {
        "video_id": video_id,
        "transcript": transcript
    }
    return payload
