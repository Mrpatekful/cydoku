
import numpy as np
cimport numpy as np

import cython


cdef extern int __builtin_popcountll(unsigned long long) nogil
cdef extern int __builtin_ffsll(unsigned long long) nogil


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef int brute_force_search(unsigned long long[::1] grid,
                             unsigned long long[:, ::1] candidate_values,
                             unsigned long[:, ::1] candidate_nums,
                             const Py_ssize_t[:, ::1] group_indices,
                             Py_ssize_t[::1] value_indices,
                             short[:, ::1] available,
                             unsigned int max_solutions):
    """Implementation of a brute force backtracking search, with
    deductive candidate reduction."""

    cdef unsigned long long value
    cdef unsigned int size = grid.shape[0]
    cdef unsigned int group_size = group_indices.shape[1]

    cdef int found = 0

    cdef const Py_ssize_t[::1] effected_indices

    cdef Py_ssize_t i, j
    cdef Py_ssize_t value_index, state = 0

    cdef int filled = initialize(grid, candidate_values[0],
                                 candidate_nums[0], group_indices,
                                 available[0])

    if filled == -1:
        return -1

    elif filled > 0:
        value_indices[0] = argmin(candidate_nums[0], available[0], size)

    while True:

        value_index = value_indices[state]

        # If no candidates left -> backtrack

        if candidate_nums[state, value_index] == 0:
            grid[value_index] = 0
            state -= 1
            filled -= 1

            if state < 0:
                return found

            continue

        # The next value will be the first set bit from the candidates

        value = 1 << (__builtin_ffsll(
            candidate_values[state, value_index]) - 1)

        grid[value_index] = value

        # Chosen value is removed from the candidates

        candidate_values[state, value_index] &= ~value
        candidate_nums[state, value_index] -= 1

        # Preparing the next state, by continuing the previous state

        candidate_values[state + 1, :] = candidate_values[state, :]
        candidate_nums[state + 1, :] = candidate_nums[state, :]
        available[state + 1, :] = available[state, :]

        # Candidate values may contain other values, besides the filled one.
        # These won't be relevant anymore, and must be removed for
        # the correct behaviour of several candidate reduction mechanisms

        candidate_values[state + 1, value_index] = value
        available[state + 1, value_index] = 0

        effected_indices = group_indices[value_index]

        # Update effected indices

        if not update_effected(value,
                               candidate_values[state + 1],
                               candidate_nums[state + 1],
                               effected_indices,
                               available[state + 1]):
            continue

        # TODO update candidates (and getting the least candidate index)

        # Termination upon all cells are filled

        if filled + 1 == size:
            found += 1

            if found == max_solutions:
                return found

            continue

        filled += 1
        state += 1

        value_indices[state] = argmin(
            candidate_nums[state], available[state], size)


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef int brute_force_search_debug(unsigned long long[::1] grid,
                                   unsigned long long[:, ::1] candidate_values,
                                   unsigned long[:, ::1] candidate_nums,
                                   const Py_ssize_t[:, ::1] group_indices,
                                   Py_ssize_t[::1] value_indices,
                                   short[:, ::1] available,
                                   int max_solutions,
                                   debugger):
    """Debug version of the above 'brute_force_search' function"""

    cdef unsigned long long value
    cdef unsigned int size = grid.shape[0]
    cdef unsigned int group_size = group_indices.shape[1]

    cdef int found = 0

    cdef const Py_ssize_t[::1] effected_indices

    cdef Py_ssize_t i, j
    cdef Py_ssize_t value_index, state = 0

    cdef int filled = initialize(grid, candidate_values[0],
                                 candidate_nums[0], group_indices,
                                 available[0])

    if filled == -1:
        return -1

    elif filled > 0:
        value_indices[0] = argmin(candidate_nums[0], available[0], size)

    while True:

        value_index = value_indices[state]

        debugger.update(
            grid,
            candidate_values[state],
            candidate_nums[state],
            value_indices[state],
            state,
            filled,
            found)

        if candidate_nums[state, value_index] == 0:
            grid[value_index] = 0
            state -= 1
            filled -= 1

            if state < 0:
                return found

            continue

        # The next value will be the first set bit from the candidates

        value = 1 << (__builtin_ffsll(
            candidate_values[state, value_index]) - 1)

        grid[value_index] = value

        # Chosen value is removed from the candidates

        candidate_values[state, value_index] &= ~value
        candidate_nums[state, value_index] -= 1

        # Preparing the next state, by continuing the previous state

        candidate_values[state + 1, :] = candidate_values[state, :]
        candidate_nums[state + 1, :] = candidate_nums[state, :]
        available[state + 1, :] = available[state, :]

        # Candidate values may contain other values, besides the filled one.
        # These won't be relevant anymore, and must be removed for
        # the correct behaviour of several candidate reduction mechanisms

        candidate_values[state + 1, value_index] = value
        candidate_nums[state + 1, value_index] = 1
        available[state + 1, value_index] = 0

        effected_indices = group_indices[value_index]

        # Update effected indices

        if not update_effected(value,
                               candidate_values[state + 1],
                               candidate_nums[state + 1],
                               effected_indices,
                               available[state + 1]):
            continue



        # Termination upon all cells are filled

        if filled + 1 == size:
            found += 1

            debugger.update(
            grid,
            candidate_values[state],
            candidate_nums[state],
            value_indices[state],
            state,
            filled + 1,
            found)

            if found == max_solutions:
                return found

            continue

        filled += 1
        state += 1

        value_indices[state] = argmin(
            candidate_nums[state], available[state], size)


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline Py_ssize_t argmin(const unsigned long[::1] candidate_nums,
                              const short[::1] available,
                              unsigned int size):
    """Finds the index of the minimum value, with respect
    to its availability. """

    cdef Py_ssize_t i, m
    cdef unsigned int min = size + 1

    for i in range(size):
        if available[i]:
            if candidate_nums[i] == 1:
                return i

            if candidate_nums[i] < min:
                m = i
                min = candidate_nums[i]

    return m


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline int initialize(unsigned long long[::1] grid,
                           unsigned long long[::1] candidate_values,
                           unsigned long[::1] candidate_nums,
                           const Py_ssize_t[:,::1] group_indices,
                           short[::1] available):
    """Initializes the state of the algorithm."""

    cdef int filled = 0, found = 1

    cdef Py_ssize_t i, j, k
    cdef Py_ssize_t grid_size = grid.shape[0]
    cdef Py_ssize_t group_size = group_indices.shape[1]

    for i in range(grid_size):
        if grid[i] != 0:
            filled += 1
            available[i] = 0
            candidate_values[i] = grid[i]
            candidate_nums[i] = 1

            for j in range(group_size):
                k = group_indices[i, j]
                if grid[k] == 0 and candidate_values[k] & grid[i]:
                    candidate_values[k] &= ~grid[i]
                    candidate_nums[k] -= 1

                    if candidate_nums[k] == 0:
                        return -1

    return filled


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline short update_effected(const unsigned long long value,
                                  unsigned long long[::1] candidate_values,
                                  unsigned long[::1] candidate_nums,
                                  const Py_ssize_t[::1] effected_indices,
                                  const short[::1] available):
    """Updates the candidates with the chosen value at the
    effected locations."""

    cdef Py_ssize_t i, j
    cdef Py_ssize_t group_size = effected_indices.shape[0]

    for j in range(group_size):
            i = effected_indices[j]

            if available[i] and candidate_values[i] & value:
                candidate_values[i] &= ~value
                candidate_nums[i] -= 1

                if candidate_nums[i] == 0:
                    return False

    return True


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline int reduce_naked_singles(unsigned long long[::1] candidate_values,
                                     unsigned long[::1] candidate_nums,
                                     const Py_ssize_t[:,::1] group_indices,
                                     const short[::1] available):
    """Applies the naked single rule on the whole grid."""

    cdef Py_ssize_t i, j, k
    cdef Py_ssize_t grid_size = candidate_values.shape[0]
    cdef Py_ssize_t group_size = group_indices.shape[1]

    cdef int found = 0

    for i in range(grid_size):
        if available[i] and candidate_nums[i] == 1:
            for j in range(group_size):
                k = group_indices[i, j]

                if available[k] and candidate_values[i] & candidate_values[k]:
                    candidate_values[k] &= ~candidate_values[i]
                    candidate_nums[k] -= 1

                    if candidate_nums[k] == 0:
                        return -1

                    found += 1

    return found


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef Py_ssize_t[::1] _generate_subgrid_indices(Py_ssize_t row_index,
                                                Py_ssize_t col_index,
                                                unsigned int n):
    """Generates the subgrid group indices for a given coordinate"""

    subgrid = np.empty(n ** 2 - 1, dtype=np.intp)
    cdef Py_ssize_t sub_row_index, sub_col_index, row_coord, col_coord
    cdef Py_ssize_t i = 0

    for sub_row_index in range(n):
        for sub_col_index in range(n):
            row_coord = (row_index // n) * n + sub_row_index
            col_coord = (col_index // n) * n + sub_col_index
            if row_coord != row_index or col_coord != col_index:
                subgrid[i] = n ** 2 * row_coord + col_coord
                i += 1

    return subgrid


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef Py_ssize_t[::1] _generate_col_indices(Py_ssize_t row_index,
                                           Py_ssize_t col_index,
                                           unsigned int n):
    """Generates the column group indices for a given coordinate"""

    column = np.empty(n ** 2 - 1, dtype=np.intp)

    cdef Py_ssize_t j, i = 0
    cdef Py_ssize_t size = column.shape[0]

    for j in range(n ** 2):
        if j != row_index:
            column[i] = n ** 2 * j + col_index
            i += 1

    return column


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef Py_ssize_t[::1] _generate_row_indices(Py_ssize_t row_index,
                                           Py_ssize_t col_index,
                                           unsigned int n):
    """Generates the row group indices for a given coordinate"""

    row = np.empty(n ** 2 - 1, dtype=np.intp)

    cdef Py_ssize_t j, i = 0
    cdef Py_ssize_t size = row.shape[0]

    for j in range(n ** 2):
        if j != col_index:
            row[i] = row_index * n ** 2 + j
            i += 1

    return row


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef Py_ssize_t[:, ::1] generate_group_indices(unsigned int n):
    """Generates the tensor, which holds the indices of groups for each
        coordinate
    """
    group_indices = np.empty([n ** 4, (n ** 2 - 1) * 3], dtype=np.intp)

    cdef Py_ssize_t row_index, col_index

    for row_index in range(n ** 2):
        for col_index in range(n ** 2):
            group_indices[row_index * n ** 2 + col_index, :] = \
                np.hstack((
                    _generate_row_indices(row_index, col_index, n),
                    _generate_col_indices(row_index, col_index, n),
                    _generate_subgrid_indices(
                        row_index, col_index, n)))

    return group_indices

