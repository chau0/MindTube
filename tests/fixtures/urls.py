"""Test fixtures for YouTube URLs and video IDs."""

from typing import NamedTuple


class UrlTestCase(NamedTuple):
    """Test case for URL parsing with expected video ID."""

    url: str
    expected_video_id: str
    description: str


# Valid YouTube URL formats with their expected video IDs
VALID_URLS = [
    # Standard watch URLs
    UrlTestCase(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        expected_video_id="dQw4w9WgXcQ",
        description="Standard watch URL",
    ),
    UrlTestCase(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        expected_video_id="dQw4w9WgXcQ",
        description="Watch URL without www",
    ),
    UrlTestCase(
        url="http://www.youtube.com/watch?v=dQw4w9WgXcQ", expected_video_id="dQw4w9WgXcQ", description="HTTP watch URL"
    ),
    # URLs with additional parameters
    UrlTestCase(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s",
        expected_video_id="dQw4w9WgXcQ",
        description="Watch URL with timestamp",
    ),
    UrlTestCase(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxyz123&index=5",
        expected_video_id="dQw4w9WgXcQ",
        description="Watch URL with playlist parameters",
    ),
    UrlTestCase(
        url="https://www.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",
        expected_video_id="dQw4w9WgXcQ",
        description="Watch URL with feature parameter before video ID",
    ),
    # Short URLs (youtu.be)
    UrlTestCase(url="https://youtu.be/dQw4w9WgXcQ", expected_video_id="dQw4w9WgXcQ", description="Short youtu.be URL"),
    UrlTestCase(url="http://youtu.be/dQw4w9WgXcQ", expected_video_id="dQw4w9WgXcQ", description="HTTP short URL"),
    UrlTestCase(
        url="https://youtu.be/dQw4w9WgXcQ?t=42", expected_video_id="dQw4w9WgXcQ", description="Short URL with timestamp"
    ),
    # YouTube Shorts
    UrlTestCase(
        url="https://www.youtube.com/shorts/dQw4w9WgXcQ",
        expected_video_id="dQw4w9WgXcQ",
        description="YouTube Shorts URL",
    ),
    UrlTestCase(
        url="https://youtube.com/shorts/dQw4w9WgXcQ",
        expected_video_id="dQw4w9WgXcQ",
        description="YouTube Shorts URL without www",
    ),
    # Mobile URLs
    UrlTestCase(
        url="https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        expected_video_id="dQw4w9WgXcQ",
        description="Mobile YouTube URL",
    ),
    # Embed URLs
    UrlTestCase(
        url="https://www.youtube.com/embed/dQw4w9WgXcQ", expected_video_id="dQw4w9WgXcQ", description="Embed URL"
    ),
    UrlTestCase(
        url="https://www.youtube.com/embed/dQw4w9WgXcQ?start=42",
        expected_video_id="dQw4w9WgXcQ",
        description="Embed URL with start parameter",
    ),
    # Different video ID formats (all valid 11-character IDs)
    UrlTestCase(
        url="https://www.youtube.com/watch?v=ABC123def_g",
        expected_video_id="ABC123def_g",
        description="Video ID with mixed case and underscore",
    ),
    UrlTestCase(
        url="https://www.youtube.com/watch?v=123-ABC_def",
        expected_video_id="123-ABC_def",
        description="Video ID with numbers, dash, and underscore",
    ),
]


# Invalid URLs that should raise exceptions
INVALID_URLS = [
    "https://www.google.com",  # Not a YouTube URL
    "https://www.youtube.com/watch",  # Missing video ID
    "https://www.youtube.com/watch?v=",  # Empty video ID
    "https://www.youtube.com/watch?v=tooshort",  # Video ID too short
    "https://www.youtube.com/watch?v=toolongvideoid123",  # Video ID too long
    "https://www.youtube.com/watch?v=invalid@chars",  # Invalid characters
    "https://youtu.be/",  # Empty short URL
    "https://www.youtube.com/shorts/",  # Empty shorts URL
    "not_a_url_at_all",  # Not a URL
    "",  # Empty string
    "https://www.youtube.com/channel/UCxyz123",  # Channel URL, not video
    "https://www.youtube.com/playlist?list=PLxyz123",  # Playlist URL, not video
]


# Edge case URLs
EDGE_CASE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ#t=42s",  # Fragment instead of query param
    "https://www.youtube.com/watch?time_continue=42&v=dQw4w9WgXcQ",  # Video ID not first param
    "HTTPS://WWW.YOUTUBE.COM/WATCH?V=dQw4w9WgXcQ",  # All caps
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&amp;t=42s",  # HTML encoded ampersand
]
