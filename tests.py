import unittest
import min_acfg


class MyTestCase(unittest.TestCase):
    def test_construct_structure(self):
        g = [[0, 1, 2], [3, 4], [5]]
        d = [[5], [4, 3], [2, 0, 1]]

        gamma = min_acfg.Structure(g)
        delta = min_acfg.Structure(d)
        self.assertEqual(gamma, delta)

    def test_move_empty_coalition(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = []

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g))

    def test_move_existing_coalition(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = [0, 1, 2]

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g))

    def test_move_all_coalitions(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = [0, 1, 2, 3, 4, 5]
        g_exp = [[0, 1, 2, 3, 4, 5]]

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g_exp))

    def test_move_coalition(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = [3, 2]
        g_exp = [[0, 1], [2, 3], [4], [5]]

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g_exp))

    def test_calc_value_alone(self):
        v = min_acfg.calc_value([1], 4, 1, [2,3])
        self.assertEqual(v, 0)

    def test_calc_value_alone_and_no_friends(self):
        v = min_acfg.calc_value([1], 4, 1, [])
        self.assertEqual(v, 0)

    def test_calc_value_only_enemies(self):
        n = 5
        v = min_acfg.calc_value([1, 4, 5], n, 1, [2, 3])
        self.assertEqual(v, -2)

    def test_number_of_possible_structures(self):
        n = 5
        N = range(n)
        F = dict(zip(N, [[]]*n))
        dic = min_acfg.calculate_all_utilities(N, F)

        self.assertEqual(len(dic.keys()), bell_number(n))


def bell_number(n):
    bell = [[0 for i in range(n + 1)] for j in range(n + 1)]
    bell[0][0] = 1
    for i in range(1, n + 1):

        # Explicitly fill for j = 0
        bell[i][0] = bell[i - 1][i - 1]

        # Fill for remaining values of j
        for j in range(1, i + 1):
            bell[i][j] = bell[i - 1][j - 1] + bell[i][j - 1]

    return bell[n][0]


if __name__ == '__main__':
    unittest.main()
