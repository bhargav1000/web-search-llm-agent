import requests
from bs4 import BeautifulSoup
from googlesearch import search
from tqdm import tqdm
from langchain.tools import tool
from typing import List, Dict


def google_search(query: str, num_results: int = 5) -> List[str]:
    """Performs a Google search and returns a list of result URLs."""
    results = []
    for url in search(query, num_results=num_results, sleep_interval=2):
        results.append(url)
    return results

def fetch_page_content(url: str, content_length: int = 10000) -> str:
    """Fetches and returns the main content of the webpage at the specified URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # Raise an error if the request failed
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        page_content = "\n".join([para.get_text() for para in paragraphs])
        return page_content[:content_length] + "..." if len(page_content) > content_length else page_content
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return f"Access denied for {url}. Content cannot be retrieved."
        return f"Error fetching content from {url}: {e}"
    
def execute_query(user_query: str, num_results: int = 5, content_length: int = 10000) -> Dict[int, str]:
    """
    Processes a user query.
    it performs a Google search, fetches content from the results, and generates a response.
    """
    # Perform Google search
    search_results = google_search(user_query, num_results=num_results)
    
    # Fetch content for each search result
    content_results = {}
    for i, url in tqdm(enumerate(search_results), desc="Searching The Web for results"):
        content = fetch_page_content(url, content_length=content_length)
        content_results[i] = content
        # content_results.append(f"{i+1}. URL: {url}\nContent:\n{content}\n")

    # filter empty results
    content_results = dict(filter(lambda x: x[1] != "", content_results.items()))

    return content_results