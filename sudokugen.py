
from gmpy2 import bit_scan1

import _sudokugen

import numpy
import time


def timed(func):
    """Convenience function for benchmarking."""

    def wrapper(*args, **kwargs):
        start = time.time()
        outputs = func(*args, **kwargs)
        return time.time() - start, outputs

    return wrapper


class Solver:
    """Base generator class"""

    def __init__(self, n: int, m: int):
        """Abstract generator instance

        Args:
            :param n: size of the subgrid, e.g. with
                      n = 3 the grid will be standard 9 x 9

            :param m: maximum number of solutions to look for
        """
        self.n = n
        self.m = m
        self.size = n ** 4 + 1

        self._value_indices = \
            numpy.empty(self.size, dtype=numpy.intp)

        self._available = numpy.empty(
            (self.size, self.n ** 4), dtype=numpy.short)

        self._unavailable = numpy.ones(
            (self.n ** 4), dtype=numpy.ulonglong) * self.n ** 2 + 1

        self._group_indices = _sudokugen.generate_group_indices(n)

        self._grid = None
        self._filled = None
        self._state_index = None

    @property
    def grid(self):
        return self._grid

    @staticmethod
    def decode(grid: numpy.ndarray, n: int) -> numpy.ndarray:
        """Decodes the given 1D binary grid to a regular
        2D numpy array with human readable numbers.

        Args:
            :param grid: Grid to be decoded.
            :param n: Size of the subgrid of the provided grid.

        Returns:
            :return: Converted grid.
        """
        converter = numpy.vectorize(
            lambda x: bit_scan1(int(x)) + 1
            if x != 0 else 0, otypes=[numpy.ulonglong])

        return converter(grid).reshape(n ** 2, n ** 2)

    @staticmethod
    def candidates(candidates: numpy.ndarray, n: int) -> list:
        """Converts the array of possible candidates in bits to
        :param candidates:
        :param n:
        :return:
        """
        def bits(x):
            return [number + 1 for number in
                    range(0, n ** 2) if x & (1 << number)]
        return [[bits(candidates[i * n ** 2 + j])
                 for j in range(n ** 2)] for i in range(n ** 2)]

    @staticmethod
    def encode(grid: numpy.ndarray) -> numpy.ndarray:
        """Encodes the given 2D grid to a 1D binary numpy array
        with coded numbers.

        Args:
            :param grid: Grid to be encoded.

        Returns:
            :return: Converted grid.
        """
        converter = numpy.vectorize(
            lambda x: numpy.uint64(2 ** (x - 1)),
            otypes=[numpy.ulonglong])

        return converter(grid).reshape(-1)

    @staticmethod
    def load(path: str):
        """
        Loads a field from a file.

        :param path: Path of the file
        """
        with open(path, 'r') as file:
            field = numpy.array(
                [[int(num) for num in
                  line.strip().split()]
                 for line in file],
                dtype=numpy.ulonglong)

            return field

    def _init(self, grid=None):
        """Initializes the generator with a grid"""
        raise NotImplementedError

    def fill(self, grid=None):
        """Fills the initialized grid."""
        raise NotImplementedError

    def save_txt(self, path):
        """Saves the grid of the generator object in decoded form.

        Args:
            :param path: Path to be saved to.
        """

        # noinspection PyTypeChecker
        numpy.savetxt(
            path, self.decode(self._grid, self.n),
            fmt='%i', delimiter=' ', newline='\n')


class BruteForceSearch(Solver):
    """Generator that implements a more sophisticated way
    of choosing the next fill index."""

    def __init__(self, n: int, m: int):
        """A best fit generator instance."""
        super(BruteForceSearch, self).__init__(n, m)

        self._candidate_values = numpy.empty(
            (self.size, self.n ** 4), dtype=numpy.ulonglong)

        self._candidate_nums = numpy.empty(
            (self.size, self.n ** 4), dtype=numpy.uint)

    def __str__(self):
        return 'brute force search'

    def _init(self, grid=None):
        """This class accepts grids with already filled, values.
        The provided grid is checked for errors. If grid is not
        provided an empty board will be filled."""

        self._filled = 0
        self._state_index = 0

        self._grid = grid

        if grid is None:
            self._grid = numpy.zeros((self.n ** 4), dtype=numpy.ulonglong)

            self._value_indices[0] = int(
                numpy.random.random_integers(0, self.n ** 4 - 1, 1))

        self._candidate_values[0, :] = numpy.ulonglong((2 ** 64) - 1)
        self._candidate_nums[0, :] = numpy.uint(self.n ** 2)
        self._available[0, :] = numpy.short(1)

    @timed
    def fill(self, grid=None):
        """Fills the board by always choosing the next candidate to
        be the one with the least amount of possible candidates."""

        self._init(grid)

        start = time.time()

        solutions = _sudokugen.brute_force_search(
            self._grid, self._candidate_values, self._candidate_nums,
            self._group_indices, self._value_indices, self._available, self.m)

        return solutions, time.time() - start


class DebugBruteForceSearch(BruteForceSearch):
    """A class that implements the same logic as the best fit
    generator class, with additional functionality of visualizing3
    the current state of the method."""

    def __init__(self, n: int, m: int, debugger):
        super(DebugBruteForceSearch, self).__init__(n, m)

        self._debugger = debugger(n, (Solver.decode, Solver.candidates))

    def __str__(self):
        return '{} (debug)'.format(super().__str__())

    @timed
    def fill(self, grid=None):
        """The same as the fill function of the super class,
        with additional calls to the visualization engine."""

        self._init(grid)

        start = time.time()

        solutions = _sudokugen.brute_force_search_debug(
            self._grid, self._candidate_values, self._candidate_nums,
            self._group_indices, self._value_indices,
            self._available, self.m, self._debugger)

        end = time.time() - start

        try:

            self._debugger.close()

        except AttributeError:
            pass

        return solutions, end
