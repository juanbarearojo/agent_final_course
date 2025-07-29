import time
from smolagents import DuckDuckGoSearchTool
from smolagents import tool

@tool
def optimized_web_search(
    search_query: str, important_words: list, batch_size: int = 500
) -> str:
    """A tool that performs a web search and filters the results to only include content chunks that contain important keywords.
    Args:
        search_query: The search query to use (e.g., 'Beatles albums Wikipedia')
        important_words: List of important keywords to filter by (e.g., ['Abbey Road', 'Let It Be', '1970'])
        batch_size: The size of content chunks to process (default: 500 characters)
    """
    try:
        # Perform the search using DuckDuckGoSearchTool
        search_tool = DuckDuckGoSearchTool()
        time.sleep(10)
        search_results = search_tool.forward(search_query)
        # Check if search_results is empty or None
        if not search_results or len(search_results) == 0:
            return "No search results found."

        # If search_results is a dictionary, extract the content
        if isinstance(search_results, list):
            all_content = " ".join(
                [result.get("content", "") for result in search_results]
            )
        else:
            all_content = search_results


        batches = []
        for i in range(0, len(all_content), batch_size):
            batches.append(all_content[i : i + batch_size])

        # Filter batches 
        filtered_batches = []
        for batch in batches:
            if any(word.lower() in batch.lower() for word in important_words):
                filtered_batches.append(batch)

        filtered_content = "\n\n".join(filtered_batches)

        if not filtered_content:
            return f"No content containing the important words {important_words} was found in the search results."

        return filtered_content

    except Exception as e:
        return f"Error during optimized web search: {str(e)}"