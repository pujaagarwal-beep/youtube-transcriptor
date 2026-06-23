from youtube_transcript_api import YouTubeTranscriptApi
import re


def extract_video_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


url = input("Paste YouTube URL: ").strip()

video_id = extract_video_id(url)

if not video_id:
    print("Invalid YouTube URL")
    exit()

try:
    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    text = "\n".join(
        item.text
        for item in transcript
    )

    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("\nTranscript saved to transcript.txt")

except Exception as e:
    print("Error:", e)