"""Module for computing interesting statistics about this phenomenon."""


from collections import defaultdict
from distance_to_philosophy import get_reverse_edges

from get_to_philosophy import get_articles, get_edges


def compute_heat_graph():
    """Compute a 'heat graph' of the articles and edges stored in the cache.
    
    In the context of this project, we will define a few concepts to make
    syntax and construction easier. Each article has a number of articles
    that link to them. Let us define a 'heat graph' as the sum of all 
    articles that eventually link to it. That is, following a path of
    articles, each article is numerically valued based on how many articles
    will eventually lead to that article.
    
    A cycle is a series of two or more articles that reference each other
    continuously. The only two ways for a chain of articles to terminate is
    when it either reaches a cycle, or reaches an article without any links.
    Given the nature of Wikipedia, the former is far more common, with the
    latter only typically occuring for chains beginning at linkless articles
    in the first place. 
    
    Our methodology is a little complicated, but is enough to come up with a
    fairly accurate, and representative number for each article. To keep an
    account of each article's running sum, we will use a dictionary that
    links the article's title to how many articles eventually link to it. It
    will also help to think of this data set as a set of disconnected graphs,
    where nodes are articles, and edges are the directed relation by which
    one article links to another.
    First, we find every cycle in the data set. That is, create a set of 
    every article that is part of a cycle. We will use each of these nodes as
    'terminating notes.' That is, in our process, if we come across one of
    these cycles, we know this is where we will stop our current path. In
    treating each cycle as one large node, we can think of this problem less
    as a graphing problem, and more as a tree problem, where each cycle is the
    root of a new tree.
    Each of those 'terminating nodes' will be added to a queue, and they will
    each be 'visited' to check their value. A 'visit' will be defined here as
    the process of going to a node, getting the value of its children 
    (computing that first if it has not yet been visited), and setting its
    value to the sum of each of its children, plus the number of children
    themselves. This will be a recursive process.
    Once all 'non-terminating' nodes have been valued, we tackle the nodes in
    cycles. Each node in the cycle will be valued similarly as previous nodes,
    and then it will traverse down the cycle to all other nodes, adding its
    value to theirs.
    Lastly, each of these cycle nodes have their values incremented by one,
    to account for the fact that they each link to each other. This gives us a
    workable, meaningful quantification for how many articles will eventually
    reach a given article.
    """
    hmap = defaultdict(int)
    # articles = get_articles()  # we really dont *need* articles i think?
    edges = get_edges()
    reverse_edges = get_reverse_edges(edges)

    def visit_node(n: str):
        """Visit a node, which essentially assigns it a value in the heat map."""
        for child in reverse_edges[n]:
            visit_node(child)  # if child has no children, this section will never be run anyway
            hmap[n] += hmap[child] + 1

    # Get terminating nodes
    terminating_nodes = set()
    seen_nodes = set()
    for article in edges.keys():
        if article in seen_nodes: continue
        path = [article]
        while len(path) == len(set(path)):  # no duplicates
            next_node = edges[path[-1]]
            if next_node == "": break  # no links
            path.append(next_node)
            if next_node in seen_nodes: break
            seen_nodes.add(next_node)
        nodes_seen_this_batch = path
        next_node = path[-1]
        # Check for terminating nodes
        while next_node not in terminating_nodes and next_node not in seen_nodes and len(path) > 1:
            terminating_nodes.add(path.pop())
            next_node = path[-1]
        # Add to nodes we've seen
        for node in nodes_seen_this_batch:
            seen_nodes.add(node)
    print(terminating_nodes)


if __name__=='__main__':
    compute_heat_graph()
