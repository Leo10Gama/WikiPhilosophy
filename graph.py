"""Module to handle graph-related structures."""

from bs4 import BeautifulSoup
import requests
from typing import Tuple


BASE = "https://en.wikipedia.org"


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
    i = 0
    for p in article.find_all('p'):
        text = remove_brackets(str(p))  # remove content in brackets
        a_tag = BeautifulSoup(text, 'html.parser').find('a')  # gets the first result
        if a_tag:
            title = a_tag['title']
            href = a_tag['href']
            if a_tag['class'] and a_tag['class'][0] == "mw-redirect":  # links to redirect, follow it for new Page
                new_soup = BeautifulSoup(requests.get(BASE + a_tag['href']).text, 'html.parser').find('h1', attrs={"id": "firstHeading"})
                title = new_soup.find('span').text
                href = get_url_from_title(title)
            linked_page = Page(title, href)
            return linked_page, Edge(page, linked_page)
    return None  # no links on page :(

    
def remove_brackets(text: str) -> str:
    """Remove content within the brackets of a string."""
    seen_brackets: int = 0
    curr: str = ""
    for letter in text:
        if letter == "(":
            seen_brackets += 1
        if not seen_brackets: curr += letter
        elif letter == ")":
            seen_brackets = 0 if seen_brackets == 0 else seen_brackets - 1
    return curr


def get_url_from_title(title: str) -> str:
    """Returns a Wikipedia link from a page's title."""
    return BASE + "/w/index.php?title=" + title


if __name__=="__main__":
    p, e = parse_page(Page("Leonardo DiCaprio", "https://en.wikipedia.org/wiki/Leonardo_DiCaprio"))
    print(f"Page: href={p.href}, title={p.title}\nEdge: {e.base_page.title} -> {e.linked_page.title}")
