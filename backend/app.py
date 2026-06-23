import streamlit as st
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


st.title("YouTube Transcript Generator")

url = st.text_input("YouTube URL")

if st.button("Generate"):
    video_id = extract_video_id(url)

    if not video_id:
        st.error("Invalid URL")
    else:
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)

            text = "\n".join(
                item.text
                for item in transcript
            )

            st.text_area(
                "Transcript",
                text,
                height=500
            )

        except Exception as e:
            st.error(str(e))