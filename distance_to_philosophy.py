"""Module to compute the distance from every article to Philosophy."""


from collections import defaultdict, deque
import time
from typing import Dict
from get_to_philosophy import get_edges


def get_reverse_edges(edges: Dict[str, str] = None) -> defaultdict(str, set):
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


def compute_distances(edges: Dict[str, str] = None, reverse_edges: defaultdict(str, set) = None) -> defaultdict(str, int):
    """Compute all the distances to Philosophy."""

    if not edges: edges = get_edges()
    if not reverse_edges: reverse_edges = get_reverse_edges(edges)  # store all articles that point to that link

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
            if reverse_edges[article]: 
                next_articles.extend(reverse_edges[article])
                reverse_edges[article] = None
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

    distances = compute_distances()

    while True:
        user_input = input(f"What would you like to query? ({QUIT_INPUT} to quit): ")

        if user_input.lower() == QUIT_INPUT:
            print("Closing application...")
            return

        print()
        if user_input in distances:
            print(f"{user_input} is {distances[user_input]} articles away from Philosophy")
        else:
            print(f"{user_input} either does not link to Philosophy, or is not a valid article title.")
        print()


if __name__=='__main__':
    main()