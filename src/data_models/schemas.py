from dataclasses import dataclass

@dataclass
class VideoData:
    """A data class to hold video information."""
    title: str
    link: str
    id: str