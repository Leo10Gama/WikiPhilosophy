"""Module to actually get to the Wikipedia page for Philosophy."""


import json
from typing import Dict, List, Optional

from graph import Edge, Page


def get_articles() -> List[Page]:
    """Returns the cached list of all articles."""

    print("Retrieving articles...", end="", flush=True)
    BASE_PATH = "cache/articles/"
    extensions = [f"articles_{x}.json" for x in list("abcdefghijklmnopqrstuvwxyz") + ["num", "other"]]
    articles = []
    for extension in extensions:
        with open(BASE_PATH + extension, "r") as infile:
            data = json.load(infile)
            for title, link in data.items():
                articles.append(Page(title, link))
    print("Done")
    return articles


def get_edges() -> Dict[str, str]:
    """Returns the cached dictionary of all edges."""

    print("Retrieving edges...", end="", flush=True)
    BASE_PATH = "cache/edges/"
    extensions = [f"edges_{x}.json" for x in list("abcdefghijklmnopqrstuvwxyz") + ["num", "other"]]
    edges = {}
    for extension in extensions:
        with open(BASE_PATH + extension, "r") as infile:
            data = json.load(infile)
            for base_title, linked_title in data.items():
                edges[base_title] = linked_title
    print("Done")
    return edges


def get_path_to_philosophy(target: str, pages: List[Page], edges: List[Edge]) -> Optional[List[str]]:
    """Find the route from a target Wikipedia page to Philosophy.
    
    Parameters
    ----------
    target: str
        The title of the Wikipedia article to start at. Must be a valid article title.
    pages: List[Page]
        The (cached) list of all Wikipedia pages.
    edges: List[Edge]
        The (cached) list of all Wikipedia edges. That is, links from the title of
        one page to the title of the first page it links to.

    Returns
    -------
    List[str] | None
        A list of Wikipedia article titles, ordered such that first is the target page,
        and last is either "Philosophy", or a duplicate of another page in the list, in
        the case that a loop is created. If the target page is invalid, nothing is
        returned.
    """

    # Target page is invalid
    if target not in [p.title for p in pages]:
        return None

    path = [target]  # initialize list
    if not edges[path[-1]]: return path  # make sure the article links to something
    next_page_title = edges[path[-1]]    # and if it does, get that something
    while next_page_title != "Philosophy" and next_page_title not in path:  # either we reach Philosophy, or loop; no links case handled above
        path.append(next_page_title)
        if not edges[path[-1]]: return path  # reached article with no more links
        next_page_title = edges[path[-1]]

    path.append(next_page_title)
    return path  # we've either reached Philosophy, or looped


def main():
    """The main method for running test queries."""
    QUIT_INPUT = 'q'  # the command to close the process

    articles = get_articles()
    edges = get_edges()

    while True:
        target = input(f"Enter the name of an article to path ({QUIT_INPUT} to quit): ")
        if target.lower() == QUIT_INPUT:
            print("Closing application...")
            return
        path = get_path_to_philosophy(target, articles, edges)
        if not path:
            print(f"No path could be found from {target} to Philosophy. Did you enter the article title correctly?")
            continue
        print("Found path!\n")
        print(path[0])
        for article_title in path[1:]:
            print(f" -> {article_title}")
        print()


if __name__=='__main__':
    main()
