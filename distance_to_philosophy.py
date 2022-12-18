"""Module to compute the distance from every article to Philosophy."""


from collections import defaultdict, deque
from random import choice
import time
from typing import DefaultDict, Dict, Optional, Set
from get_to_philosophy import get_edges


def get_reverse_edges(edges: Optional[Dict[str, str]] = None) -> DefaultDict[str, Set]:
    """Compute the reverse edges of Wikipedia articles.
    
    That is, return a dictionary that links the title of an article to the set
    of all other articles that link to it.
    """
    if not edges: edges = get_edges()
    reverse_edges = defaultdict(set)
    print("Computing reverse edges...", end="", flush=True)
    for k, v in edges.items():
        reverse_edges[v].add(k)
    print("Done")
    return reverse_edges


def compute_distances(edges: Optional[Dict[str, str]] = None, reverse_edges: Optional[DefaultDict[str, Set]] = None) -> DefaultDict[str, int]:
    """Compute all the distances to Philosophy."""

    if not edges: edges = get_edges()
    if not reverse_edges: reverse_edges = get_reverse_edges(edges)  # store all articles that point to that link
    seen = set()

    distances = defaultdict(lambda:-1)  # keep track of distances in dict (-1 = no link, 0 = Philosophy, 1 = links to Philosophy, etc)
    q = deque()  # keep track of which articles to look at next
    q.append(["Philosophy"])  # start with Philosophy
    counter = 0
    t0 = time.perf_counter()
    while q:
        articles = q.popleft()  # get batch of articles
        print(f"Batch {counter:3} ({len(articles):7} articles to update) ", end="", flush=True)
        next_articles = []
        for article in articles:
            distances[article] += 1
            if reverse_edges[article] and article not in seen: 
                next_articles.extend(reverse_edges[article])
                seen.add(article)
        for a in next_articles:
            distances[a] = distances[article]  # set value to be equal by default (will be incremented on its turn)
        if next_articles: q.append(next_articles)
        counter += 1
        t1 = time.perf_counter()
        print(f"Completed in {t1 - t0:2.4f}s")
        t0 = t1
    
    print(f"Parsed {len(distances)} articles out of {len(edges)} total ({len(distances) / len(edges) * 100:.4f}% of articles link to Philosophy).")
    return distances


def main():
    """Main method for querying path distances."""

    QUIT_INPUT = 'q'  # the input to close the terminal
    BACK_INPUT = 'b'  # the input to move back one from Philosophy
    FWRD_INPUT = 'f'  # the input to move forward one to Philosophy

    edges = get_edges()
    reverse_edges = get_reverse_edges(edges)
    distances = compute_distances(edges, reverse_edges)

    while True:
        user_input = input(f"Enter an article title ({QUIT_INPUT} to quit): ")
        print()

        if user_input.lower() == QUIT_INPUT:
            print("Closing application...")
            return

        if user_input not in distances:
            print(f"{user_input} either does not link to Philosophy, or is not a valid article title.\n")
            continue

        print(f"{user_input} is {distances[user_input]} articles away from Philosophy\n")
        article = user_input

        while True:
            user_input = input(f"Enter action for {article}\n({BACK_INPUT}) Move away from Philosophy by one (random) article\n({FWRD_INPUT}) Move towards Philosophy by one article\n(*) Go back\n\n")
            print()
            if user_input.lower() == FWRD_INPUT:
                article = edges[article]
                print(f"{article} is {distances[article]} articles away from Philosophy\n")
            elif user_input.lower() == BACK_INPUT:
                if not reverse_edges[article]:
                    print(f"No articles could be found that link to {article}.")
                    continue
                print(f"{len(reverse_edges[article])} articles link to {article}")
                article = choice(list(reverse_edges[article]))  # because set doesnt support indexing, which choice uses
                print(f"{article} is {distances[article]} articles away from Philosophy\n")
            else:
                print("Returning to previous menu...\n")
                break


if __name__=='__main__':
    main()