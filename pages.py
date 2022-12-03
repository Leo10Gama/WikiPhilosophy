"""Module to retrieve list of all English Wikipedia articles"""

import json
import time
from bs4 import BeautifulSoup
import requests
from typing import Dict


URL = "https://en.wikipedia.org/w/index.php?title=Special:AllPages"
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
    url = (URL 
            + "&from=" 
            + start_from 
        if start_from 
        else URL
    )
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    with open(STORAGE_LINK + "articles.json", "r") as raw:
        data = json.load(raw)
        if input("Would you like to use cache? (y/n) ").lower() == 'y':
            print("Returning cached article list...")
            return data
    # Iterate through Wikipedia pages for answer
    next = None
    try:
        while True:
            # Get each article (<a> tag) from the list
            for link in soup.find('ul', attrs={'class': "mw-allpages-chunk"}).find_all('a'):
                if link.has_attr('class') and link['class'][0] == "mw-redirect": continue
                title = link.get('title')
                href = link.get('href')
                articles[title] = BASE + href
                print(title, flush=True)
            # Get the 'next page' link and go there
            next_tag = soup.find('div', attrs={'class': "mw-allpages-nav"}).find_all('a')[-1]
            if "Previous" in next_tag.text: break
            next = BASE + next_tag.get('href')
            soup = BeautifulSoup(requests.get(next).text, 'html.parser')
    except Exception as e:
        print(f"Error hit:\n{e}\n\nAttempting reconnection in 10 seconds...")
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
