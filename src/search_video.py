import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

from src.data_models.schemas import VideoData
load_dotenv()

class SerperVideoSearcher:
    """
    Searches videos using the Serper API, focusing on finding the 
    earliest-published video for an exact text snippet.
    """

    def __init__(self, max_results: int = 10):
        """
        Initializes the searcher.
        
        Args:
            serper_api_key: Your Serper.dev API key.
            max_results: The maximum number of videos to request from the API.
        """
        self.api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        self.max_results = max_results

    def _get_earliest_video_data(self, video_results: List[Dict[str, Any]]) -> str | None:
        """
        Internal method to find the video ID of the earliest-published video.
        
        Args:
            video_results: A list of video result dictionaries from the Serper API.
            
        Returns:
            The video ID (str) of the earliest video, or None if the list is empty.
        """
        if not video_results:
            return None
        
        # Serper uses 'date' for the published time. We use the logic from 
        # your previous request: find the dictionary with the chronologically 
        # smallest date string value.
        earliest_video = min(
            video_results, 
            key=lambda x: x.get('date', '9999-12-31') # Use a very late default date
        )

        # The Serper API result contains a 'link' like 'https://www.youtube.com/watch?v=VIDEO_ID...'
        return VideoData(
            title=earliest_video.get('title', 'No Title'),
            link=earliest_video.get('link', ''),
            id=earliest_video.get('link').split("v=")[-1]
        )

    def find_earliest_video_details_by_snippet(self, text_snippet: str) -> str | None:
        """
        Searches Serper.dev for videos matching the text snippet and 
        returns the video ID of the one published first.
        
        Args:
            text_snippet: The exact phrase to search for.
            
        Returns:
            The video ID (str) of the original video, or None if not found.
        """
        # Enclose the query in quotes for an exact phrase search
        search_query = f'"{text_snippet}" site:youtube.com'

        payload = {
            "q": search_query,
            "type": "video",  # Specifically request video search
            "gl": "us",       # Geographic location (e.g., United States)
            "num": self.max_results # Number of results
        }
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            data = response.json()
            
            # The video results are under the 'videos' key in the Serper response
            video_results = data.get('videos', [])
            
            return self._get_earliest_video_data(video_results)
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Serper API: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

