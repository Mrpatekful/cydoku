
from gmpy2 import bit_scan1, popcount

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

    def __init__(self, n: int):
        """Abstract generator instance

        Args:
            :param n: size of the subgrid, e.g. with
                      n = 3 the grid will be standard 9 x 9
        """
        self.n = n
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

    def __init__(self, n: int):
        """A best fit generator instance."""
        super(BruteForceSearch, self).__init__(n)

        self._candidate_values = numpy.empty(
            (self.size, self.n ** 4), dtype=numpy.ulonglong)

        self._candidate_nums = numpy.empty(
            (self.size, self.n ** 4), dtype=numpy.ulonglong)

    def _init(self, grid=None):
        """This class accepts grids with already filled, values.
        The provided grid is checked for errors. If grid is not
        provided an empty board will be filled."""

        self._filled = 0
        self._state_index = 0

        if grid is None:
            self._grid = numpy.zeros((self.n ** 4), dtype=numpy.ulonglong)

            self._value_indices[0] = 0
                # int(numpy.random.random_integers(0, self.n ** 4 - 1, 1))

            self._candidate_values[0, :] = numpy.ulonglong((2 ** 64) - 1)
            self._candidate_nums[0, :] = numpy.uint(self.n ** 2)
            self._available[0, :] = numpy.short(1)

        else:
            # TODO initialize filed state
            pass

    @timed
    def fill(self, grid=None):
        """Fills the board by always choosing the next candidate to
        be the one with the least amount of possible candidates."""

        self._init(grid)

        _sudokugen.brute_force_search(
            self._grid, self._candidate_values, self._candidate_nums,
            self._group_indices, self._value_indices, self._available,
            self._filled)
        print(self._grid.reshape(9, 9))
        print(self._candidate_values[11].reshape(9, 9))
        print(self._candidate_nums[11].reshape(9, 9))


class DebugBestFitGenerator(BruteForceSearch):
    """A class that implements the same logic as the best fit
    generator class, with additional functionality of visualizing
    the current state of the method."""

    def __init__(self, n: int, display):
        super(DebugBestFitGenerator, self).__init__(n)
        self._display = display(n)

    def _candidates(self, index):
        candidates = \
            ~numpy.bitwise_or.reduce(self._grid[self._group_indices[index]])
        candidates = int(candidates) & (2 ** (self.n ** 2 + 1) - 1)
        return candidates, popcount(candidates)

    @timed
    def fill(self, grid=None):
        """The same as the fill function of the super class,
        with additional calls to the visualization engine."""

        self._init(grid)

        size = self.n ** 4
        iteration = 0

        self._display.update(
            self.decode(self._grid, self.n),
            self._candidate_values[self._state_index + 1],
            iteration
        )

        while True:

            print(self._state_index)

            if iteration % 1000000 == 0:
                iteration = 0

            iteration += 1

            # The best fit index, that was chosen for this state.

            value_index = self._value_indices[self._state_index]

            # If there are candidates, which haven't been
            # tried yet, proceed, else revert to the previous state.

            if self._candidate_nums[self._state_index, value_index] == 0:
                self._grid[value_index] = 0
                self._state_index -= 1
                self._filled -= 1
                continue

            # Choosing value from the candidates for the best fit index.

            value = int(2 ** bit_scan1(
                int(self._candidate_values[self._state_index, value_index])))
            self._grid[value_index] = value

            # By setting the value, we reduce the untried
            # candidates for this state by the set value,
            # and reduce the number of candidates by 1.

            self._candidate_values[self._state_index, value_index] &= \
                numpy.ulonglong(~value)
            self._candidate_nums[self._state_index, value_index] -= 1

            # By choosing a value, we can calculate the next
            # state of the board, by building upon
            # the previous state.

            # Preparing the next state

            self._candidate_values[self._state_index + 1, :] = \
                self._candidate_values[self._state_index, :]
            self._candidate_nums[self._state_index + 1, :] = \
                self._candidate_nums[self._state_index, :]
            self._available[self._state_index + 1, :] \
                = self._available[self._state_index, :]

            # By setting the value at this state, the location
            #  will be unavailable at the next state

            self._candidate_values[self._state_index + 1, value_index] = value
            self._available[self._state_index + 1, value_index] = False

            # By setting the value at this state we can calculate
            # the candidates for the effected indices, at the next state.

            effected_indices = self._group_indices[value_index]

            terminate = 0
            for i in range(len(effected_indices)):
                j = effected_indices[i]

                if self._available[self._state_index + 1, j] \
                        and self._candidate_values[self._state_index + 1, j] & numpy.ulonglong(value) != 0:
                    self._candidate_values[self._state_index + 1, j] &= numpy.ulonglong(~value)
                    self._candidate_nums[self._state_index + 1, j] -= 1

                    if self._candidate_nums[self._state_index + 1, j] == 0:
                        terminate = 1
                        break

            if terminate == 1:
                continue

            # effected_data = numpy.array(
            #     list(map(self._candidates, effected_indices)),
            #     dtype=numpy.ulonglong)
            #
            # # Effected data contains the calculated candidates
            # # and number of candidates for the effected locations
            #
            # candidate_nums = effected_data[:, 1]
            #
            # # If there is inconsistency, revert
            #
            # if 0 in candidate_nums:
            #     continue
            #
            # self._candidate_values[self._state_index + 1, effected_indices] = \
            #     effected_data[:, 0]
            #
            # self._candidate_nums[self._state_index + 1, effected_indices] = \
            #     candidate_nums

            self._candidate_values[self._state_index + 1, value_index] = value
            self._available[self._state_index + 1, value_index] = False

            # If the set value passes the consistency check, it can be filled

            self._filled += 1

            self._display.update(
                self.decode(self._grid, self.n),
                self._candidate_values[self._state_index + 1],
                iteration
            )

            if self._filled == size:
                break

            # Looking at the next state, we calculate the next best fit index
            # (the location with the least candidates)
            # (Availability has not changed )

            self._state_index += 1

            self._value_indices[self._state_index] = numpy.argmin(numpy.where(
                self._available[self._state_index],
                self._candidate_nums[self._state_index],
                self._unavailable
            ))
