"""
sheets_sync.py

Run this manually whenever you want to process the sheet:
    python sheets_sync.py

It looks for rows where column A has a YouTube URL and column B is empty,
fetches the transcript, and writes it into column B.
"""

import re
import time

import gspread
from google.oauth2.service_account import Credentials
from youtube_transcript_api import YouTubeTranscriptApi

# ---------- CONFIG: edit these three values ----------
SPREADSHEET_NAME = "Youtube Data"
WORKSHEET_NAME = "Sheet1"
CREDENTIALS_FILE = "credentials.json"
# URL_COL / TRANSCRIPT_COL are 1-indexed column numbers (A=1, B=2, ...)
URL_COL = 1
TRANSCRIPT_COL = 2
START_ROW = 2  # skip header row
# -------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def extract_video_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript_text(video_id):
    api = YouTubeTranscriptApi()

    transcript_list = api.list(video_id)

    # Prefer English
    try:
        transcript = transcript_list.find_transcript(['en'])
    except:
        # Otherwise use any generated transcript available
        transcript = next(iter(transcript_list))

    fetched = transcript.fetch()

    return "\n".join(item.text for item in fetched)


def main():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    rows = sheet.get_all_values()

    print(f"Found {len(rows)} rows. Scanning from row {START_ROW}...")

    for i, row in enumerate(rows[START_ROW - 1:], start=START_ROW):
        url = row[URL_COL - 1].strip() if len(row) >= URL_COL else ""
        existing = row[TRANSCRIPT_COL - 1].strip() if len(row) >= TRANSCRIPT_COL else ""

        if not url or existing:
            continue

        video_id = extract_video_id(url)
        if not video_id:
            sheet.update_cell(i, TRANSCRIPT_COL, "ERROR: Invalid URL")
            continue

        print(f"Row {i}: fetching transcript for {video_id}...")
        try:
            text = get_transcript_text(video_id)
            sheet.update_cell(i, TRANSCRIPT_COL, text)
            print(f"Row {i}: done.")
        except Exception as e:
            sheet.update_cell(i, TRANSCRIPT_COL, f"ERROR: {e}")
            print(f"Row {i}: failed - {e}")

        time.sleep(1)  # be polite to the API / avoid rate limits

    print("Finished.")


if __name__ == "__main__":
    main()