import textwrap

from logger import logger
from src.search_video import SerperVideoSearcher
from src.transcriptions import Transcriber
from src.semantic_search import SemanticSearcher



def generate_timed_youtube_url(video_id: str, timestamp_start: str) -> str:
    """
    Generates a direct YouTube URL that starts playback at the specified timestamp.

    The YouTube URL format for starting at a specific time uses the 't' parameter 
    which must be in seconds.

    Args:
        video_id (str): The YouTube video ID (e.g., 'dQw4w9WgXcQ').
        timestamp_start (str): The timestamp in HH:MM:SS format (e.g., '00:00:15').

    Returns:
        str: The full URL for the video starting at the desired time.
    """

    # 1. Convert HH:MM:SS timestamp to total seconds
    try:
        # Pad the hours section if it's single digit (e.g., '0:08:35' -> '00:08:35')
        # Splitting by ':' handles the single-digit hour automatically.
        parts = timestamp_start.split(':')
        
        # Ensure we have at least 3 parts (H, M, S). If not, prepend '0' for hours.
        if len(parts) == 2: # M:S format
             minutes, seconds = map(int, parts)
             hours = 0
        elif len(parts) == 3: # H:M:S format
             hours, minutes, seconds = map(int, parts)
        else:
             return "Error: Invalid timestamp format. Must be H:MM:SS or HH:MM:SS."
        
        total_seconds = (hours * 3600) + (minutes * 60) + seconds
    except ValueError:
        return "Error: Invalid timestamp format. Ensure M and S are numbers."
    
    # 2. Format the final URL
    base_url = "https://www.youtube.com/watch?v="
    timed_url = f"{base_url}{video_id}&t={total_seconds}s"
    
    return timed_url

def display_search_results(result: dict, final_url: str):
    """
    Display formatted search results for a matched YouTube video segment

    :param result: Dictionary containing video match details including video ID, timestamp, and matched text snippet
    :type result: dict
    :param final_url: The generated YouTube URL to start playback at the matched timestamp
    :type final_url: str
    """
    video_id = result['video_id']
    timestamp_start = result['timestamp_start']
    
    # Define box properties
    box_width = 75
    border = "=" * box_width

    print(f"\n{border}")
    print(f"{'VIDEO MATCH FOUND':^{box_width}}")
    print(f"{border}")
    
    # Detail lines
    print(f"| {'Video ID:':<25} | {video_id:<45} |")
    print(f"| {'Timestamp Start:':<25} | {timestamp_start:<45} |")
    print(f"{border}")

    # Matched Text Section
    print(f"| {'Matched Text Snippet:':<73} |")
    # Wrap text for the matched snippet
    
    wrapped_text = textwrap.wrap(result['matched_text'], width=box_width - 4)
    for line in wrapped_text:
        print(f"| {line:<73} |")
    print(f"{border}")

    # URL message
    print(f"\n Please click the URL below to start watching on YouTube:")
    print(f" {final_url}\n")
    print(f"{border}")

if __name__ == '__main__':
    
    query = input("Please enter a snippet that you want to search on youtube : ")

    video_searcher = SerperVideoSearcher()
    video_id = video_searcher.find_earliest_video_details_by_snippet(query)

    transcriber = Transcriber()
    transcriber.save_transcript_to_json(video_id=video_id)


    semantic_Searcher = SemanticSearcher()
    vector_store = semantic_Searcher.embed_and_store_faiss(video_id)
    result = semantic_Searcher.semantic_search_and_time(video_id, vector_store=vector_store, query=query )

    url = generate_timed_youtube_url(video_id, result["timestamp_start"])

    display_search_results(result=result, final_url=url)