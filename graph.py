"""Module to handle graph-related structures."""

import json
from bs4 import BeautifulSoup
import requests
from typing import Dict, Tuple


BASE = "https://en.wikipedia.org"
STORAGE_LINK = "cache/edges/"


class Page:
    """Class to represent a node, graphically.
    
    In the context of this program, a "node" is a Wikipedia page.
    """

    href: str = ""
    title: str = ""

    def __init__(self, title: str, link: str):
        self.href = link
        self.title = title

    
class Edge:
    """Class to represent an edge, graphically.
    
    In the context of this program, an "edge" is a directed
    relationship, where the first Page's hyperlink links to
    the second Page.
    """

    base_page: Page = None
    linked_page: Page = None

    def __init__(self, page1: Page, page2: Page):
        self.base_page = page1
        self.linked_page = page2

    def to_tuple(self) -> Tuple[str, str]:
        return (self.base_page.href, self.linked_page.href)


def parse_page(page: Page) -> Tuple[Page, Edge]:
    """Parse a Wikipedia Page, returning the Page it links to, and the Edge (representation of the relationship)"""

    article = BeautifulSoup(requests.get(page.href).text, 'html.parser').find('div', attrs={"id": "mw-content-text"}).find('div', attrs={"class": "mw-parser-output"})  # get soup
    for p in article.find_all('p'):
        if not str(p): continue
        text = remove_brackets(str(p))  # remove content in brackets
        a_tags = BeautifulSoup(text, 'html.parser').find_all('a')  # gets the first result
        for a_tag in a_tags:
            if a_tag and a_tag.has_attr("title"):
                title = a_tag['title']
                href = a_tag['href']
                if a_tag.has_attr("class") and a_tag['class'][0] == "mw-redirect":  # links to redirect, follow it for new Page
                    new_soup = BeautifulSoup(requests.get(BASE + a_tag['href']).text, 'html.parser').find('h1', attrs={"id": "firstHeading"})
                    title = new_soup.text
                    href = get_url_from_title(title)
                linked_page = Page(title, href)
                return linked_page, Edge(page, linked_page)
    for ul in article.find_all('ul'):  # try again for UL (disambiguation pages)
        if not str(ul): continue
        text = remove_brackets(str(ul))  # remove content in brackets
        a_tags = BeautifulSoup(text, 'html.parser').find_all('a')  # gets the first result
        for a_tag in a_tags:
            if a_tag and a_tag.has_attr("title"):
                title = a_tag['title']
                href = a_tag['href']
                if a_tag.has_attr("class") and a_tag['class'][0] == "mw-redirect":  # links to redirect, follow it for new Page
                    new_soup = BeautifulSoup(requests.get(BASE + a_tag['href']).text, 'html.parser').find('h1', attrs={"id": "firstHeading"})
                    title = new_soup.text
                    href = get_url_from_title(title)
                linked_page = Page(title, href)
                return linked_page, Edge(page, linked_page)
    return None  # no links on page :(

    
def remove_brackets(text: str) -> str:
    """Remove content within the brackets of a string."""
    seen_brackets: int = 0
    in_tag: bool = False
    curr: str = ""
    for letter in text:
        if letter == "<":
            in_tag = True
        if letter == "(":
            seen_brackets += 1
        if not seen_brackets or in_tag: curr += letter
        if letter == ")":
            seen_brackets = 0 if seen_brackets == 0 else seen_brackets - 1
        if letter == ">":
            in_tag = False
    return curr


def get_url_from_title(title: str) -> str:
    """Returns a Wikipedia link from a page's title."""
    return BASE + "/w/index.php?title=" + title


def parse_articles(articles_path: str, file_extension: str = "") -> Dict[str, str]:
    """Given the link to an articles.json file, return the dictionary of edges.
    
    The return value will be a dictionary, where the key is the title of
    the first article, and the value is the title of the article it first
    links to. These values will also be written in the cache as JSON.

    file_extension is the extension to be added to the saved JSON file,
    such that it follows the convention `edges_[extension].json`.
    """
    articles = {}
    edges = {}
    with open(articles_path, "r") as raw:
        articles = json.load(raw)
    if not articles: raise Exception(f"Invalid path: {articles_path}")
    try:
        for title, href in articles.items():
            print(f"Parsing {title}...")
            p, e = parse_page(Page(title, href))
            edges[title] = p.title
    except Exception as ex:
        print(ex)
    finally:
        filename = f"{STORAGE_LINK}edges_{file_extension}.json"
        with open(filename, "w+") as outfile:
            json.dump(edges, outfile, indent=4, sort_keys=True)


if __name__=="__main__":
    parse_articles("cache/articles/articles_x.json", "x")
