"""Module to retrieve list of all English Wikipedia articles"""

import json
import time
from bs4 import BeautifulSoup
import requests
from typing import Dict


URL = "https://en.wikipedia.org/wiki/Category:All_Wikipedia_articles_written_in_American_English"
BASE = "https://en.wikipedia.org"
STORAGE_LINK = "cache/"


def get_pages(start_from: str = None) -> Dict[str, str]:
    """Retrieve the list of all English Wikipedia articles

    Parameters
    ----------
    start_from: str = None
        The Wikipedia article to start searching from. If None, starts
        from the beginning
    
    Returns
    -------
    Dict[str, str]
        A dictionary of all English Wikipedia articles, linking the name 
        of the article to its link.
    """
    # Initialize
    articles: Dict[str, str] = {}  # List of links
    url = (BASE 
            + "/w/index.php?title=Category:All_Wikipedia_articles_written_in_American_English&pagefrom=" 
            + start_from 
            + "#mw-pages" 
        if start_from 
        else URL
    )
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    total = int(soup.find('div', attrs={'id': 'mw-pages'}).find('p').text.split("approximately ", 1)[1].split(" total", 1)[0].replace(',', ''))
    # If total == our cache, just return that
    with open(STORAGE_LINK + "articles.json", "r") as raw:
        data = json.load(raw)
        if len(data) == total:
            print("No change since last retrieval. Returning cached article list...")
            return data
    # Iterate through Wikipedia pages for answer
    next = None
    try:
        while True:
            # Get each article (<a> tag) from the list
            for link in soup.find('div', attrs={'class': "mw-category mw-category-columns"}).find_all('a'):
                title = link.get('title')
                href = link.get('href')
                articles[title] = BASE + href
                print(title, flush=True)
            # Get the 'next page' link and go there
            next = [
                BASE + link.get('href') 
                for link 
                in soup.find('div', attrs={'id': 'mw-pages'}).find_all('a') 
                if link.text == 'next page'
            ]
            if not next: break
            soup = BeautifulSoup(requests.get(next[0]).text, 'html.parser')
    except Exception as e:
        print("Error hit. Attempting reconnection in 10 seconds...")
        time.sleep(10)
        return get_pages(next)
    finally:
        if start_from:
            with open(STORAGE_LINK + "articles.json", "r") as raw:
                data = json.load(raw)
                for k, v in data.items():
                    articles[k] = v
        # Write/append to file
        with open(STORAGE_LINK + "articles.json", "w+") as outfile:
            json.dump(articles, outfile, indent=4, sort_keys=True)
            
    print("Articles scraped successfully")
    return articles


if __name__=="__main__":
    get_pages()
