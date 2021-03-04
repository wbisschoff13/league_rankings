import sys
import re
from collections import defaultdict


REGEX_STRING = r"([\w ]+) (\d+), ([\w ]*) (\d+)"


def process_file(filename):
    """
    >>> import tempfile
    >>> import os
    >>> with tempfile.NamedTemporaryFile(delete=False) as tmp:
    ...     tmp.write(b"Lions 3, Snakes 3\\nTarantulas 1, FC Awesome 0\\nLions 1, FC Awesome 1\\nTarantulas 3, Snakes 1\\nLions 4, Grouches 0\\n") and True
    ...     tmp.flush()
    ...     process_file(tmp.name)
    ...     tmp.close()
    ...     os.unlink(tmp.name)
    True
    0
    >>> with open("output.txt") as f:
    ...     f.read()
    '1. Tarantulas, 6 pts\\n2. Lions, 5 pts\\n3. FC Awesome, 1 pt\\n3. Snakes, 1 pt\\n5. Grouches, 0 pts\\n'
    """

    matches = read(filename)
    points = calculate_points(matches)
    ranks = calculate_rank(points)
    return write_rank(ranks)


def read(filename):
    """Reads from file, using regex to retrieve important data. Returns list of tuples

    >>> re.findall(REGEX_STRING, "Lions 3, Snakes 3\\nTarantulas 1, FC Awesome 0\\n")
    [('Lions', '3', 'Snakes', '3'), ('Tarantulas', '1', 'FC Awesome', '0')]
    >>> import tempfile, os
    >>> with tempfile.NamedTemporaryFile(delete=False) as tmp:
    ...     tmp.write(b"Lions 3, Snakes 3\\nTarantulas 1, FC Awesome 0\\nLions 1, FC Awesome 1\\nTarantulas 3, Snakes 1\\nLions 4, Grouches 0\\n") and True
    ...     tmp.flush()
    ...     read(tmp.name)
    ...     tmp.close()
    ...     os.unlink(tmp.name)
    True
    [('Lions', '3', 'Snakes', '3'), ('Tarantulas', '1', 'FC Awesome', '0'), ('Lions', '1', 'FC Awesome', '1'), ('Tarantulas', '3', 'Snakes', '1'), ('Lions', '4', 'Grouches', '0')]
    >>> read("nonexistantfile")
    Traceback (most recent call last):
        ...
    FileNotFoundError
    """

    try:
        with open(filename) as f:
            matches = re.findall(REGEX_STRING, f.read().strip())
    except:
        raise FileNotFoundError()
    return matches


def calculate_points(matches):
    """Iterates through matches, adding up points from all matches. Returns dictionary.

    >>> calculate_points([('Lions', '3', 'Snakes', '3'), ('Tarantulas', '1', 'FC Awesome', '0'), ('Lions', '1', 'FC Awesome', '1'), ('Tarantulas', '3', 'Snakes', '1'), ('Lions', '4', 'Grouches', '0')])
    {'Lions': 5, 'Snakes': 1, 'Tarantulas': 6, 'FC Awesome': 1, 'Grouches': 0}
    >>> calculate_points([('Lions', '3', 'Snakes', '3')])
    {'Lions': 1, 'Snakes': 1}
    >>> calculate_points([('Lions', '3', 'Lions', '3')])
    Traceback (most recent call last):
        ...
    ValueError...
    >>> calculate_points([])
    {}
    """
    points = defaultdict(int)
    for match in matches:
        team1, score1, team2, score2 = match
        if team1 == team2:
            raise ValueError("Invalid teams")
        points1, points2 = calculate_match_points(score1, score2)
        points[team1] += points1
        points[team2] += points2
    return dict(points)


def calculate_match_points(score1, score2):
    """Calculates points based on match score. Win = 3, Tie = 1, Lose = 0. Returns points tuple.

    >>> calculate_match_points(0, 1)
    (0, 3)
    >>> calculate_match_points(1, 0)
    (3, 0)
    >>> calculate_match_points(1, 1)
    (1, 1)
    >>> calculate_match_points(0, 0)
    (1, 1)
    >>> calculate_match_points(1)
    Traceback (most recent call last):
        ...
    TypeError...
    """
    points1 = points2 = 0
    if score1 == score2:
        points1 = points2 = 1
    elif score1 > score2:
        points1 = 3
    else:
        points2 = 3
    return points1, points2


def sort_points(points):
    """Sorts dictionary of "team":"points" by points descending, then team ascending.

    >>> sort_points({'Lions': 1, 'Snakes': 1})
    {'Lions': 1, 'Snakes': 1}
    >>> sort_points({'Lions': 1, 'Snakes': 2})
    {'Snakes': 2, 'Lions': 1}
    >>> sort_points({'Lions': 1, 'Elephants': 1})
    {'Elephants': 1, 'Lions': 1}
    """
    return dict(sorted(points.items(), key=lambda k: (-k[1], k[0])))


def calculate_rank(points):
    """Takes sorted dictionary as input. Calculates the ranking of each team. Tied scores have the same ranking.

    >>> calculate_rank({'Lions': 1, 'Snakes': 1})
    {1: [('Lions', 1), ('Snakes', 1)]}
    >>> calculate_rank({'Snakes': 2, 'Lions': 1})
    {1: [('Snakes', 2)], 2: [('Lions', 1)]}
    >>> calculate_rank({'Snakes': 2, 'Lions': 1, 'Tarantulas': 2})
    {1: [('Snakes', 2), ('Tarantulas', 2)], 3: [('Lions', 1)]}
    """
    counter = 1
    prev_points = -1
    nth = -1
    rank = defaultdict(list)
    sorted_dict = sort_points(points)
    for team, points in sorted_dict.items():
        if points != prev_points:
            nth = counter
        rank[nth].append((team, points))
        counter += 1
        prev_points = points
    return dict(rank)


def write_rank(ranks):
    """Takes sorted dictionary as input. Writes ranks to output.txt, with 'pt' for single point and 'pts' for 0 or >1.

    >>> write_rank({1: [('Snakes', 2), ('Tarantulas', 2)], 3: [('Lions', 1)]})
    0
    >>> with open("output.txt", "r") as f:
    ...     f.read()
    '1. Snakes, 2 pts\\n1. Tarantulas, 2 pts\\n3. Lions, 1 pt\\n'
    """
    with open("output.txt", "w") as f:
        for rank, teams in ranks.items():
            for team, points in teams:
                f.write(f"{rank}. {team}, {points} {'pt' if points == 1 else 'pts'}\n")
    return 0


if __name__ == "__main__":
    # # Commented out due to running tests via Github Actions
    # import doctest
    # doctest.testmod(optionflags=doctest.ELLIPSIS)

    # TODO: if no filename is specified, but contains "-v" argument for verbose doctest
    if len(sys.argv) == 2 and sys.argv[1] != "-v":
        filename = sys.argv[1]
    else:
        filename = "input.txt"
    process_file(filename)
