import itertools
import numpy as np


def remove_players(coalition, players_to_remove):
    """
    Removes all players from the coalition that are in players_to_remove
    :param coalition: List representing a coalition
    :param players_to_remove: List of players to remove
    :return: The coalition without the removed players
    """
    return [p for p in coalition if p not in players_to_remove]


class Structure:
    def __init__(self, collection):
        self.struct = self.freeze(collection)

    def __str__(self):
        return str(self.unfreeze(self.struct))

    def __repr__(self):
        return str(self.unfreeze(self.struct))

    def __hash__(self):
        return self.struct.__hash__()

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def freeze(self, struct):
        """
        Converts coalition structure to a frozenset to be hashable
        :param struct: A collection of collections
        :return: The frozenset version
        """
        return frozenset(map(frozenset, struct))

    def unfreeze(self, frozen_struct):
        """
        Converts a frozenset back to a mutable collection
        :param frozen_struct: A frozen coalition structure
        :return: A list object representing the structure
        """
        return list(map(list, frozen_struct))

    def move_coalition(self, coalition):
        """
        Moves all players in coalition from their orginal coalition to form a new one.
        :param coalition: New coalition to form
        :return: The new coalition structure
        """
        structure = self.unfreeze(self.struct)
        new_structure = [remove_players(c, coalition) for c in structure] \
                        + [coalition]
        filtered = list(filter(None, new_structure))
        return Structure(filtered)

    def check_blocking_coalition(self, dic, coalition):
        """
        checks whether the given coalition blocks the structure
        :param dic: Dictionary containing all utilities for all structures
        :param coalition: The coalition to check
        :return: True if the coalition actually blocks the structure
        """
        new_structure = self.move_coalition(coalition)
        res = True

        for p in coalition:
            if dic[self][p] >= dic[new_structure][p]:
                res = False
                break

        return res

    def is_core_stable(self, dic, all_cs):
        """
        checks whether the structure is core stable
        :param dic: Dictionary containing all utilities for all structures
        :param all_cs: List of all possible coalitions
        :return: True if the structure is core stable
        """
        for c in all_cs:
            if self.check_blocking_coalition(dic, c):
                return False
        return True


def partition(collection):
    """
    https://stackoverflow.com/questions/19368375/set-partitions-in-python
    :param collection: A collection to partition
    :return: A collection of all possible partitions of the collection
    """
    if len(collection) == 1:
        yield [collection]
        return

    first = collection[0]
    for smaller in partition(collection[1:]):
        # insert `first` in each of the subpartition's subsets
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[first] + subset] + smaller[n + 1:]
        # put `first` in its own subset
        yield [[first]] + smaller


def find_coalition(structure, player):
    """
    :param structure: The coalition structure
    :param player: The player to find
    :return: The coalition containing the player
    """
    return [c for c in structure if player in c][0]


def calc_value(coalition, n, player, friends):
    """
    calculate the value of the given coalition for the given player
    :param coalition: The coalition
    :param n: Number of players in the game
    :param player: The player to consider
    :param friends: The player's friends
    :return: The numerical value the player assigns to the coalition
    """
    v = 0
    for p in coalition:
        if p == player:
            continue
        elif p in friends:
            v += n
        else:
            v -= 1
    return v


def calc_utility(structure, n, player, F, degree='SF'):
    """
    Calculate the utility of a given structure for the given player
    :param structure: A coalition structure
    :param n: The number of players in total
    :param player: The player to consider
    :param F: The network of friends
    :param degree: The degree of altruism to use
    :return: The numerical utility the player assigns to the structure
    """
    M = n ** 2

    c = find_coalition(structure, player)
    own_value = calc_value(c, n, player, F[player])
    vs_friends = [calc_value(find_coalition(structure, friend), n, friend,
                             F[friend]) for friend in F[player]]
    min_value_friends = min(vs_friends) if len(vs_friends) != 0 else 0

    if degree == 'SF':
        return M * own_value \
               + min_value_friends

    if degree == 'EQ':
        return min([own_value, min_value_friends])

    if degree == 'AL':
        return own_value \
               + M * min_value_friends


def calculate_all_utilities(N, F, degree='SF'):
    """
    Calculate a dict containing all possible structure and their utilities for
    each player
    :param N: The set of players
    :param F: The network of friends
    :param degree: The degree of altruism
    :return: A dict with all possible structures as keys and list of utilities
    as values
    """
    n = len(N)
    partitions = enumerate(partition(list(N)), 1)
    dic = dict()

    for i, p in partitions:
        uts = []
        for player in N:
            uts.append(calc_utility(p, n, player, F, degree=degree))
        dic[Structure(p)] = uts
    return dic


def find_all_coalitions(N):
    """
    Find all subsets of the set of players.
    :param N: The set of players
    :return: A list containing all possible coalitions
    """
    res = []
    for m in range(len(N) - 1):
        res += (list(itertools.combinations(N, m + 1)))
    return res


def find_core_stable_structure(N, F, dic=None, degree='SF'):
    """
    Checks all possible structures for the ACFG for a core-stable one.
    :param N: The set of players
    :param F: The network of friends
    :param dic: The dict containing all structures and utilities. If 'None', it
                is computed.
    :param degree: The degree of altruism
    :return: The first core-stable structure in dic or 'None' if none exists
    """
    all_cs = find_all_coalitions(N)

    if dic is None:
        dic = calculate_all_utilities(N, F, degree=degree)

    for struct in dic.keys():
        if struct.is_core_stable(dic, all_cs):
            return struct

    return None


def compare_structures(uts_gamma, uts_delta):
    """
    Compare two structures regarding their popularity.
    :param uts_gamma: The utilities of the first structure
    :param uts_delta: The utilities of the second structure
    :return: 1 (-1) if Gamma (Delta) is more popular. 0 if equally popular.
    """
    s = sum([np.sign(a - b) for a, b in zip(uts_gamma, uts_delta)])
    return np.sign(s)


def find_popular_structure(N, F, dic=None, degree='SF', strict=False):
    """
    Checks all possible structures for the ACFG for a (strictly) popular one.
    :param N: The set of players
    :param F: The network of friends
    :param dic: The dict containing all structures and utilities. If 'None', it
                is computed.
    :param degree: The degree of altruism
    :param strict: If True, checks for a strictly popular structure
    :return: The first (strictly) popular structure in dic or 'None' if none
             exists
    """
    if dic is None:
        dic = calculate_all_utilities(N, F, degree=degree)

    for struct1, uts1 in dic.items():
        res = True
        for struct2, uts2 in dic.items():
            if struct1 == struct2:
                continue
            if strict:
                if compare_structures(uts1, uts2) != 1:
                    res = False
                    break
            else:
                if compare_structures(uts1, uts2) < 0:
                    res = False
                    break

        if res:
            return struct1

    return None
