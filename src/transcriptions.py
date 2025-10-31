import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

from logger import logger

class Transcriber:

    def __init__(self):
        self.ytt_api = YouTubeTranscriptApi()
        # Initialize the JSONFormatter
        self.formatter = JSONFormatter()


    def save_transcript_to_txt(self, video_id: str):
        """Fetches the transcript for a video ID, combines the text, and saves it to a file."""
        try:
            # Fetch the transcript for the given video ID
            transcript = self.ytt_api.fetch(video_id)
            logger.info(transcript)
            # Format the transcript into a JSON string
            json_formatted_transcript = self.formatter.format_transcript(transcript)

            # Define the filename for your JSON file
            filename = f'{video_id}.json'
            output_dir = "transcription_db"
            full_path = os.path.join(output_dir, f"{filename}.json") 
            os.makedirs(output_dir, exist_ok=True)

            # Write the JSON string to a file
            with open(full_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_formatted_transcript)

            print(f"Transcript successfully saved to {filename}")

        except Exception as e:
            print(f"An error occurred: {e}")