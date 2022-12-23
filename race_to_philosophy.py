"""Module for articles racing to see which gets to Philosophy first."""


from random import sample
import time
from typing import Dict, List, Optional

from get_to_philosophy import get_edges


def race(articles: List[str], edges: Dict[str, str] = None) -> Optional[List[str]]:
    """Race a list of articles towards Philosophy.

    In addition to returning the title of the winning article, the race
    will also be printed as it is happening, so that the user can see
    the two articles as they begin reaching Philosophy.
    
    Parameters
    ----------
    articles: List[str]
        A list of article titles to race towards Philosophy.
    edges: Dict[str, str] = None
        The cache of edges. If not passed, it will be computed in the
        method.

    Returns
    -------
    Optional[List[str]]
        The list of titles of the winning articles. The reason for being a
        list is to have multiple returns in the event of a tie. If all 
        articles loop, None is returned.
    """

    if not edges: edges = get_edges()

    TITLE_LENGTH_CAP = 32
    SECONDS_BETWEEN_ITERATIONS = 1

    racers = [title for title in articles]  # local array to traverse through so we don't ruin the original array
    path = [[] for _ in articles]           # track the current path the articles are taking (so we can tell if/when something loops)
    has_looped = [False for _ in articles]  # keep track of whether an article has looped

    # Make divider
    divider = "+"
    for _ in racers: divider += f"{'-' * TITLE_LENGTH_CAP}+"
    print(divider)
    # Print initial conditions
    print("|", end="")
    for racer_name in racers:
        if len(racer_name) > TITLE_LENGTH_CAP:
            print(f"{racer_name[:TITLE_LENGTH_CAP]}|", end="")
        else:
            print(f"{racer_name:^{TITLE_LENGTH_CAP}}|", end="")
    print(f"\n{divider}")
    time.sleep(SECONDS_BETWEEN_ITERATIONS)
    # RACE! Continue until either we reach Philosophy or all articles have looped
    while "Philosophy" not in racers or all(has_looped):
        # Move forward one article each
        for i, racer in enumerate(racers):
            if racer == "(no articles linked)": continue
            if edges[racer] == "":
                racers[i] = "(no articles linked)"
            else:
                racers[i] = edges[racer]
            path[i].append(racer)
            has_looped[i] = path[i].count(racer) > 1
        # Print the current positions
        print("|", end="")
        for racer_name in racers:
            if len(racer_name) > TITLE_LENGTH_CAP:
                print(f"{racer_name[:TITLE_LENGTH_CAP]}|", end="")
            else:
                print(f"{racer_name:^{TITLE_LENGTH_CAP}}|", end="")
        print(f"\n{divider}")
        time.sleep(SECONDS_BETWEEN_ITERATIONS)
    
    if "Philosophy" not in racers:  # we've looped, return None
        return None
    if racers.count("Philosophy") == 1:  # only one winner
        return [articles[racers.index("Philosophy")]]
    # Handle multiple winners
    winners = []
    for i, article in enumerate(racers):
        if article == "Philosophy":
            winners.append(articles[i])
    return winners


def start_race():
    """Begin a race between two Wikipedia articles."""

    edges = get_edges()
    print()

    while True:
        num_racers = input("How many articles would you like to race? ")
        if num_racers.isnumeric() and int(num_racers) > 0:
            num_racers = int(num_racers)
        else:
            print("Invalid number of racers. Using 2 for now...")
            num_racers = 2

        racers: List[str] = sample(edges.keys(), num_racers)

        # Print the options
        for i in range(len(racers)):
            print(f"({i+1}) {racers[i]}")
        prediction = input("\nWhich do you think will reach Philosophy first? ")

        # Make sure prediction is valid
        if not prediction.isnumeric() or int(prediction) > len(racers) or int(prediction) <= 0:
            print("Invalid prediction. Cancelling race...")
            return

        prediction = int(prediction)
        prediction -= 1  # move prediction from 1-indexed to 0-indexed (like the array)

        winners = race(racers, edges=edges)

        if not winners:  # all looped, no winner
            print("All articles looped, so there is no winner!")
        elif len(winners) == 1:  # only one winner
            winner = winners[0]
            print(f"The winner is... {winner.upper()}!!")
            if racers.index(winner) == prediction:
                print("Your prediction was correct, congratulations!")
            else:
                print("Your prediction was incorrect, better luck next time!")
        else:
            print(f"The winners are... ", end="")
            for winner in winners:
                print(f"{winner.upper()}, ", end="")
            else:
                print()
            if racers[prediction] in winners:
                print("Your prediction was correct, congratulations!")
            else:
                print("Your prediction was incorrect, better luck next time!")
        
        user_input = input("Would you like to play again? (y/n) ").lower()
        if user_input == 'y': 
            print()
            continue
        print("See you again soon!")
        return


if __name__=='__main__':
    start_race()
