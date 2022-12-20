"""Module for creating efficient menus for the CLI."""

from typing import List, T, Optional


def view_results(results: List[T], can_select: bool=False, page: int=1, results_per_page: int=10) -> Optional[T]:
    """View results in terminal, and return a selected value (if specified).
    
    The function will create a window in the terminal, listing the elements
    of `results`. Each "page" contains only as many elements as specified,
    and they can only be selected if the caller allows. If elements can be
    selected, then when an element's index is entered, it is returned at the
    end of the function. As such, values assigned to be the result of this
    function will take on whatever element is selected by the user.
    Note that `page` represents the on-screen number such that the index of
    the list is exactly one fewer than `page`. In addition, the inequality
    1 <= `page` <= `totalPages` should always hold.

    Parameters
    ----------
    results: List[T]
        A list of all the elements to be selected from.
    can_select: bool
        Whether or not the user can select a result from the list. 
        (Default is False)
    page: int
        Which page number to show results from. (Default is 1)
    results_per_page: int
        How many results to show on a single page. (Default is 10)
    
    Returns
    -------
    T | None
        Either an element selected from the list (if can_select is True), or None
        if either can_select is False, or an invalid selection is made.
    """
    prompt: str = "(p) Previous page\n(n) Next page\n(#) Select this one\n(*) Close view\n\n" if can_select else "(p) Previous page\n(n) Next page\n(*) Close view\n\n"
    cmd: str = "."
    totalPages: int = int(len(results) / results_per_page)
    if len(results) % results_per_page != 0: totalPages += 1
    while cmd:
        print(f"======================== RESULT  VIEWER ========================")   # Header
        # Print all results
        print(f"\t{len(results)} results:\n")
        for i in range((page - 1) * results_per_page, min(((page - 1) * results_per_page) + results_per_page, len(results))):
            print(f"{f'({i + 1})'.ljust(5, ' ')} {results[i]}")
        else:
            print()

        # NAV BAR AT THE BOTTOM
        # Print prefix part
        print(f"<(p) ", end="")
        if page > 2:
            print(f"1 ", end="")
        if page > 3:    # Print prefix dots (maybe)
            print(f"... ", end="")
        # Print current selection
        if page == 1:   
            print("{%d} " % page, end="")
            if page + 1 <= totalPages:
                print(f"{page + 1} ", end="")
        else:
            print("%d {%d} " % (page - 1, page), end="")    # Previous and current number
            if page + 1 <= totalPages:  # Next number (if possible)
                print(f"{page + 1} ", end="")
        if page < totalPages - 2:   # Print suffix dots (maybe)
            print(f"... ", end="")
        # Print suffix part
        if (page + 1) <= totalPages - 1:
            print(f" {totalPages} ", end="")
        print(f"(n)>\n================================================================\n")   # Footer

        # Prompt next action
        cmd = input(prompt).lower()
        print()
        if cmd != "" and not can_select: cmd = cmd[0]
        if cmd.isnumeric() and can_select:
            cmd = int(cmd)
            if cmd >= 1 and cmd <= len(results):
                print(f"Selected option ({cmd}): {results[cmd - 1]}\n")
                return results[cmd - 1]
        if cmd != "p" and cmd != "n": cmd = ""
        if cmd == "p":
            if page > 1: page -= 1
            else: print(f"This is the first page; cannot go back\n")
        elif cmd == "n":
            if page + 1 <= totalPages: page += 1
            else: print(f"This is the last page; cannot go further\n")
    return None
