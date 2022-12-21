"""Module to handle graph-related structures."""

import json
from math import floor
from multiprocessing import Pool
import time
import traceback
from bs4 import BeautifulSoup
import requests
from typing import Dict, Tuple

from handle_logging import setup_logger


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
    the second Page. However, only the title of the page is
    needed.
    """

    base_page: str = None
    linked_page: str = None

    def __init__(self, page1: str, page2: str):
        self.base_page = page1
        self.linked_page = page2

    def to_tuple(self) -> Tuple[str, str]:
        return (self.base_page, self.linked_page)


write_logger = setup_logger("Write Files", "write.log")  # Log for when files are written to
no_link_logger = setup_logger("Pages with No Links", "nolinks.log")  # Log for articles found without links
no_article_logger = setup_logger("Nonexistent Pages", "noarticle.log")  # Log for articles that don't exust
error_logger = setup_logger("Errors", "errors.log")  # Log any errors or warnings that occur


def parse_page(page: Page) -> Tuple[Page, Edge]:
    """Parse a Wikipedia Page, returning the Page it links to, and the Edge (representation of the relationship)"""

    soup = BeautifulSoup(requests.get(page.href).text, 'html.parser')
    if not soup:  # connection timeout / requests gave None
        error_logger.info("Timed out trying to reach %s. Sleeping for 10 seconds and trying again...", page.title)
        time.sleep(10)
        return parse_page(page)
    divs = soup.find('div', attrs={"id": "mw-content-text"})
    article = None
    if divs: article = divs.find('div', attrs={"class": "mw-parser-output"})  # get soup

    if not divs or not article:   # empty article or timeout
        if divs: pass             # page doesn't exist
        elif soup.find('title'):  # server down or misconnection
            error_logger.warning('Servers down or experiencing technical problem for %s. Sleeping for 30s and trying again...', page.title)
            time.sleep(30)
            return parse_page(page)
        no_article_logger.warning('No article found for %s. Skipping...', page.title)
        return Page("", ""), Edge("", "")

    def parse_chunk(chunks):
        """Take some chunks of BeautifulSoup tags and parse them."""
        for chunk in chunks:
            if not str(chunk): continue
            text = remove_brackets(str(chunk))  # remove content in brackets
            if BeautifulSoup(text, 'html.parser').find('span', attrs={'id': 'coordinates'}): continue  # skip over coordinates
            a_tags = BeautifulSoup(text, 'html.parser').find_all('a')  # gets the first result
            for a_tag in a_tags:
                if not a_tag or not a_tag.has_attr("title"): continue  # check tag exists and has a title
                title = a_tag['title']
                href = BASE + a_tag['href']
                if (
                    a_tag['href'].startswith("/wiki/Help:") 
                    or a_tag['href'].startswith("/wiki/Wikipedia:")
                    or a_tag['href'].startswith("https://")
                ): continue   # links to not-an-article
                if a_tag.has_attr("class"):
                    if a_tag['class'][0] == "new":          # links to page that doesn't exist, skip
                        continue
                    if a_tag['class'][0] == "mw-redirect":  # links to redirect, follow it for new Page
                        new_soup = BeautifulSoup(requests.get(BASE + a_tag['href']).text, 'html.parser')
                        some_head = None
                        if new_soup: some_head = new_soup.find('h1', attrs={"id": "firstHeading"})
                        if not new_soup or not some_head:
                            error_logger.info("Timed out trying to reach %s. Sleeping for 10 seconds and trying again...", page.title)
                            time.sleep(10)
                            return parse_page(page)
                        head = some_head
                        title = head.text
                        href = get_url_from_title(title)
                linked_page = Page(title, href)
                return linked_page, Edge(page, linked_page)
        return None, None

    for table in article.select("table"):  # we don't need tables; also prevents accidentally grabbing sidebar
        table.extract()

    p, e = parse_chunk(article.find_all(['p', 'ul', 'ol']))   # check all paragraphs (case for like 99% of articles) and list items
    if p and e: return p, e

    no_link_logger.warning("Found article without any links: %s", page.title)
    return Page("", ""), Edge(page.title, "")  # if we've reached this point, no links on page :(

    
def remove_brackets(text: str) -> str:
    """Remove content within the brackets of a string."""
    seen_brackets: int = 0
    in_tag: bool = False
    curr: str = ""
    for letter in text:
        if letter == "<" and not seen_brackets:
            in_tag = True
        if letter == "(":
            seen_brackets += 1
        if not seen_brackets or in_tag: curr += letter
        if letter == ")":
            seen_brackets = 0 if seen_brackets == 0 else seen_brackets - 1
        if letter == ">" and not seen_brackets:
            in_tag = False
    return curr


def get_url_from_title(title: str) -> str:
    """Returns a Wikipedia link from a page's title."""
    return BASE + "/w/index.php?title=" + title


def parse_articles(articles_path: str, file_extension: str = "", cont: bool = False) -> Tuple[Dict[str, str], str]:
    """Given the link to an articles.json file, return the dictionary of edges.
    
    The return value will be a dictionary, where the key is the title of
    the first article, and the value is the title of the article it first
    links to. These values will also be written in the cache as JSON.

    file_extension is the extension to be added to the saved JSON file,
    such that it follows the convention `edges_[extension].json`.

    cont will determine whether or not to continue adding entries to a
    pre-existing list of edges.
    """
    articles = {}
    edges = {}
    try_again: bool = False
    with open(articles_path, "r") as raw:
        articles = json.load(raw)
    if not articles: raise Exception(f"Invalid path: {articles_path}")
    total_articles = len(articles.keys())
    counter = 0
    if cont:  # we're continuing a file
        link = f"{STORAGE_LINK}edges_{file_extension}.json"
        try:
            with open(link, "r") as edge_list:  # get json list of things we've seen (remove from what we're going to see)
                try:
                    seen_edges = dict(json.load(edge_list).items())
                    counter = len(seen_edges.keys())
                    for seen_edge in seen_edges.keys():
                        del articles[seen_edge]
                        edges[seen_edge] = seen_edges[seen_edge]
                except Exception:
                    error_logger.warning("File %s was empty; nothing found in cache", link)
        except:
            error_logger.warning("File %s does not exist. Creating...", link)
            with open(link, "w+") as _:
                pass
    try:
        for title, href in articles.items():
            # logging.info("Parsing %s...", title)
            print(f"{file_extension.upper():5} ({counter:6}/{total_articles:6} = {floor(counter * 100 / total_articles * 100) / 100:5.2f}%) Parsing {title}")
            p, _ = parse_page(Page(title, href))
            edges[title] = p.title
            counter += 1
    except Exception as ex:
        error_logger.error("Something went wrong while parsing %s: %s", articles_path, ex)
        print(traceback.format_exc())
        try_again = True
    finally:
        filename = f"{STORAGE_LINK}edges_{file_extension}.json"
        with open(filename, "w+") as outfile:
            write_logger.info("Writing articles '%s' to '%s'...", file_extension, filename)
            json.dump(edges, outfile, indent=4, sort_keys=True)
        if try_again: 
            error_logger.info("Attempting to continue %s...", articles_path)
            return parse_articles(articles_path, file_extension, True)
        write_logger.info("Returning edges for %s...", articles_path)
        return edges, file_extension


def cleanup(filename: str, disconnected_articles=None):
    """Cleanup method to remove articles that don't point to anything."""

    edges = {}  # make file
    with open(filename, "r") as infile:
        edges = json.load(infile)  # read in json

    remove_if_in = lambda x: "Awards" in x
    edges = {k: v for k, v in edges.items() if not remove_if_in(v)}  # remove items with name

    # for article in disconnected_articles:
    #     if article in edges:
    #         del edges[article]

    with open(filename, "w+") as outfile:
        json.dump(edges, outfile, indent=4, sort_keys=True)  # rewrite json


if __name__=="__main__":
    items = list("abcdefghijklmn") + ["num", "o", "other"] + list("pqrstuvwxyz")
    article_links = [f"cache/articles/articles_{x}.json" for x in items]

    try:
        # Do cleanup
        # disconnected_articles = distance_to_philosophy.get_unconnected_articles()

        for extension in items:
            filename = f"{STORAGE_LINK}edges_{extension}.json"
            print(f"Cleaning {extension} files...")
            cleanup(filename)

        # Run method
        with Pool(28) as p:
            write_logger.info("Starting multiprocessor thread for articles.")
            for edge_batch, extension in p.starmap(parse_articles, zip(article_links, items, [True for _ in range(28)])):
                filename = f"{STORAGE_LINK}edges_{extension}.json"
                with open(filename, "w+") as outfile:
                    write_logger.info("Writing articles '%s' to '%s'...", extension, filename)
                    json.dump(edge_batch, outfile, indent=4, sort_keys=True)

    except KeyboardInterrupt:
        # time.sleep(3)  # give time for threads to write
        pass
        

    # for link, extension in zip(article_links, items):
    #     for edge_batch in parse_articles(link, extension, True)

    # print(parse_page(Page("Test", "https://en.wikipedia.org/wiki/Candidate"))[0].title)
