import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

from logger import logger

class Transcriber:

    def __init__(self):
        """
        Initialize the Transcriber with YouTube transcript API and JSON formatter

        :param self: Instance of the Transcriber class
        """
        self.ytt_api = YouTubeTranscriptApi()
        self.formatter = JSONFormatter()

    def prepare_video_id(self, video_id: str) -> str:
        """
        Escape a leading hyphen in a YouTube video ID by prefixing it with a backslash

        :param self: Instance of the Transcriber class
        :param video_id: YouTube video identifier to prepare
        :type video_id: str
        :return: Video ID with a leading hyphen escaped if necessary
        :rtype: str
        """
        if video_id.startswith('-'):
            logger.info('Video is starts with -')
            # Add a backslash to escape the leading hyphen
            return '\\' + video_id
        return video_id

    def save_transcript_to_json(self, video_id: str):
        """
        Fetch the transcript for a YouTube video and save it as a JSON file

        :param self: Instance of the Transcriber class
        :param video_id: YouTube video identifier to fetch the transcript for
        :type video_id: str
        """
        try:
            logger.info('save transcript started')
            # Fetch the transcript for the given video ID
            video_id = self.prepare_video_id(video_id)
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