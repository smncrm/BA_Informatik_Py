import itertools


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


def value_coalition(coalition, n, player, friends):
    """
    calculate the value of the given coalition for the given player
    :param coalition: The coalition
    :param n: Number of players in the game
    :param player: The player to consider
    :param friends: The network of friends
    :return: The numerical value the player assigns to the coalition
    """
    v = 0
    for p in coalition:
        if p == player:
            continue
        elif p in friends[player]:
            v += n
        else:
            v -= 1
    return v


def utility(structure, n, player, friends, type='SF'):
    M = n ** 2

    c = find_coalition(structure, player)
    own_value = value_coalition(c, n, player, friends)
    min_value_friends = min(
        [value_coalition(find_coalition(structure, friend), n, friend, friends)
         for friend in friends[player]])
    if type == 'SF':
        return M * own_value \
               + min_value_friends

    if type == 'EQ':
        return min([own_value, min_value_friends])

    if type == 'AL':
        return own_value \
               + M * min_value_friends


def calculate_all_utilities(N, F, degree='SF'):
    n = len(N)
    partitions = enumerate(partition(list(N)), 1)
    dic = dict()

    for i, p in partitions:
        uts = []
        for player in N:
            uts.append(utility(p, n, player, F, type=degree))
        dic[Structure(freeze(p))] = uts
    return dic


def find_all_coalitions(N):
    res = []
    for m in range(len(N) - 1):
        res += (list(itertools.combinations(N, m + 1)))
    return res
