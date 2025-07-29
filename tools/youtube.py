import backoff
from langchain_community.document_loaders import YoutubeLoader
from smolagents import tool

@tool
def load_youtube(video_url: str, phrase: str) -> str:
    """
    Load YouTube video content with customizable language and translation options.
    
    This function retrieves the transcript and metadata from a YouTube video with retry logic
    using exponential backoff for robust handling of temporary failures.
    
    Args:
        video_url (str): The YouTube video URL to load content from.
        phrase (str): The phrase looking for in transcript.
    
    Returns:
        str: The loaded video content that occour after the looking phrase.
    
    Raises:
        Exception: Any exception that occurs after exhausting all retry attempts (max 3 tries).
        
    Examples:
        >>> load_youtube_with_options("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Spanish transcript")
        "Video content with transcript..."
        
        "Spanish transcript translated to English..."
    """
    @backoff.on_exception(backoff.expo, Exception, max_tries=8, max_time=60)
    def _loader(video_url) -> str:
      loader = YoutubeLoader.from_youtube_url(video_url)
      doc = loader.load()
      if doc:
        return doc[0].page_content.lower()
      else:
        raise Exception("Empty document")

    phrase = phrase.replace(".", "").replace("?", "").lower()
    content = _loader(video_url)
    if phrase in content:
      return content[content.index(phrase): len(content)]
    return content   
