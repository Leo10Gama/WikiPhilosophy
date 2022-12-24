"""Module for articles racing to see which gets to Philosophy first."""


import json
from random import sample
import time
from typing import Dict, List, Optional

from get_to_philosophy import get_edges
from menu import view_results
from vital_articles import CATEGORIES, get_vital_articles_at_level, get_vital_articles_by_category


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
    while "Philosophy" not in racers and not all(has_looped):
        # Move forward one article each
        for i, racer in enumerate(racers):
            if racer == "(no articles linked)": continue
            if edges[racer] == "":
                racers[i] = "(no articles linked)"
            else:
                racers[i] = edges[racer]
            path[i].append(racer)
            has_looped[i] = len(path[i]) != len(set(path[i]))  # casting to set removes duplicates
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
        # Set number of racers
        num_racers = input("How many articles would you like to race? ")
        if num_racers.isnumeric() and int(num_racers) > 0:
            num_racers = int(num_racers)
        else:
            print("Invalid number of racers. Using 2 for now...")
            num_racers = 2

        # Pick categories
        categories = []
        category_selection = input(
            f"Which categories would you like?\n"
            f"(3) Vital articles Level 3 and lower\n"
            f"(4) Vital articles Level 4 and lower\n"
            f"(5) All vital articles\n"
            f"(c) Choose level 5 vital article categories\n"
            f"(*) All articles\n"
        ).lower()
        if category_selection.isnumeric():
            print("Loading vital articles...")
            if int(category_selection) >= 3:
                categories.extend(get_vital_articles_at_level(1))
                categories.extend(get_vital_articles_at_level(2))
                categories.extend(get_vital_articles_at_level(3))
            if int(category_selection) >= 4:
                categories.extend(get_vital_articles_at_level(4))
            if int(category_selection) >= 5:
                categories.extend(get_vital_articles_at_level(5))
        elif category_selection == 'c':
            option = "a"
            my_options = [category for category in CATEGORIES]
            while True:
                option = view_results(my_options, can_select=True, results_per_page=20)
                if not option: break  # no further selection
                categories.extend(get_vital_articles_by_category(option))
                my_options.remove(option)
        else:
            print("Loading all articles...")
            categories.extend(edges.keys())
        print()

        racers: List[str] = sample(categories, num_racers)

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
