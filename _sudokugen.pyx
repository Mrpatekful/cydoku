
import numpy as np
cimport numpy as np

import cython

from cython.parallel import prange, parallel


cdef extern int __builtin_popcountll(unsigned long long) nogil
cdef extern int __builtin_ffsll(unsigned long long) nogil


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef Py_ssize_t[::1] _generate_subgrid_indices(Py_ssize_t row_index,
                                                Py_ssize_t col_index,
                                                unsigned int n):

    """Generates the subgrid group indices for a given coordinate

    Args:
        :param row_index: Row index of the element, for which the
		                  the subgrid is generated currently.

	    :param col_index: Column index of the element,
		                  described previously.

    Returns:
	    :return subgrid: A numpy array, that holds
		                 the indices of the n x n - 1 sized subgrid group,
		                 which contains the provided row_index, col_index.
    """
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

    """Generates the column group indices for a given coordinate

    Args:
        :param row_index: Row index of the element, for which the
                          the subgrid is generated currently.

        :param col_index: Column index of the element,
                          described previously.

    Returns:
        :return row: A numpy array, that holds
                     the indices of the n x n - 1 long column group, which
                     contains the provided row_index, col_index.
    """
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

    """Generates the row group indices for a given coordinate

    Args:
        :param row_index: Row index of the element, for which the
                          the subgrid is generated currently.

        :param col_index: Column index of the element,
                          described previously.

    Returns:
        :return row: A numpy array, that holds
                     the indices of the n x n - 1 long row group, which
                     contains the provided row_index, col_index.
    """
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

    Returns:
        :return: A numpy tensor of shape (n ** 4, (n x n - 1) * 3)
    """
    group_indices = np.empty([n ** 4, (n ** 2 - 1) * 3], dtype=np.intp)

    cdef Py_ssize_t row_index, col_index

    for row_index in range(n ** 2):
        for col_index in range(n ** 2):
            group_indices[row_index * n ** 2 + col_index, :] = \
                np.hstack((_generate_row_indices(row_index, col_index, n),
                           _generate_col_indices(row_index, col_index, n),
                           _generate_subgrid_indices(row_index, col_index, n)))

    return group_indices


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void brute_force_search(unsigned long long[::1] grid,
                              unsigned long long[:, ::1] candidate_values,
                              unsigned long long[:, ::1] candidate_nums,
                              const Py_ssize_t[:, ::1] group_indices,
                              Py_ssize_t[::1] value_indices,
                              short[:, ::1] available,
                              unsigned int filled):
    """Implementation of a brute force backtracking search, with
    deductive candidate reduction.

    Args:
        :param grid: The sudoku grid.

        :param candidate_values: An array for caching the candidate
                                 states during the run of the algorithm.

        :param candidate_nums: An array for caching the number of
                               candidates for each position of the grid.

        :param group_indices: An array that serves as a lookup for each
                              position of the grid. The lookup contains
                              the group indices for the corresponding
                              grid index.

        :param value_indices: An array for holding the index
                              visited at every state of the run.

        :param available: An array that holds the availability of a
                          cell at the current state.

        :param filled: Counter for the number of filled cells.

    """

    cdef unsigned long long value
    cdef unsigned int size = grid.shape[0]
    cdef unsigned int group_size = group_indices.shape[1]

    cdef short refresh

    cdef const Py_ssize_t[::1] effected_indices

    cdef Py_ssize_t i, j
    cdef Py_ssize_t value_index, next_state, state = 0

    while True:
        value_index = value_indices[state]

        # If no candidates left -> backtrack

        if candidate_nums[state, value_index] == 0:
            grid[value_index] = 0
            state -= 1
            filled -= 1
            continue

        # TODO refactor next value choosing mechanism
        # The next value will be the first set bit from the candidates

        value = 2 ** (__builtin_ffsll(
            candidate_values[state, value_index]) - 1)

        grid[value_index] = value

        # Chosen value is removed from the candidates

        candidate_values[state, value_index] &= ~value
        candidate_nums[state, value_index] -= 1

        # Preparing the next state, by continuing the previous state

        next_state = state + 1

        candidate_values[next_state, :] = candidate_values[state, :]
        candidate_nums[next_state, :] = candidate_nums[state, :]
        available[next_state, :] = available[state, :]

        # Candidate values may contain other values, besides the filled one.
        # These won't be relevant anymore, and must be removed for
        # the correct behaviour of several candidate reduction mechanisms

        candidate_values[next_state, value_index] = value
        available[next_state, value_index] = 0

        effected_indices = group_indices[value_index]

        # Update effected indices

        if not update_effected(value, candidate_values[next_state],
                candidate_nums[next_state], effected_indices,
                               available[next_state]):
            continue

        if state == 10:
            break

        # TODO update candidates (and getting the least candidate index)

        # Revert to previous state upon error

        # refresh = 1
        # while refresh > 0:
        #     refresh = reduce_candidates()
        #
        # if refresh == -1:
        #     continue

        # Termination upon all cells are filled

        filled += 1
        if filled == size:
            break

        state += 1

        # TODO move this to candidate calculation

        value_indices[state] = argmin(
            candidate_nums[state], available[state], size)


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline Py_ssize_t argmin(const unsigned long long[::1] candidate_nums,
                              const short[::1] available,
                              unsigned int size):
    """Finds the index of the minimum value, with respect
    to its availability. 
    
    Args:
        :param candidate_nums: The array holding the number of candidates
                               for each location of the grid at the current
                               state.
                               
        :param available: Array, that holds whether a particular index
                          is available.
                          
        :param size: Size of the grid.
    
    Returns:
        :return: Index of the element, that contains the least candidates.
    """
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
cdef inline short update_effected(const unsigned long long value,
                                  unsigned long long[::1] candidate_values,
                                  unsigned long long[::1] candidate_nums,
                                  const Py_ssize_t[::1] effected_indices,
                                  const short[::1] available):
    """Updates the candidates with the chosen value at the
    effected locations.
    
    Args:
        :param value: The value, that was chosen at the state for filling.
        
        :param candidate_values: An array for caching the candidate
                                 states during the run of the algorithm.
        
        :param candidate_nums: The array holding the number of candidates
                               for each location of the grid at the current
                               state.
        
        :param effected_indices: Indices of the elements, that have
                                 been effected by inserting a value.
        
        :param available: Array containing the availability of the elements.
    
    Return:
        :return: True, if no controversy has been found during the
                 updating of the effected indices.
    """

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
def reduce_candidates_parallel(const unsigned long long[:] grid,
                               unsigned long long[:] candidate_values,
                               unsigned long long[:] candidate_nums,
                               const Py_ssize_t[:,:] group_indices):

    cdef Py_ssize_t i, j
    cdef Py_ssize_t grid_size = grid.shape[0]
    cdef Py_ssize_t group_size = group_indices.shape[1]

    with nogil:
        for i in prange(grid_size, num_threads=8):
            candidate_values[i] = 0
            for j in range(group_size):
                candidate_values[i] |= grid[group_indices[i, j]]
            candidate_values[i] = ~candidate_values[i]


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline short reduce_candidates(const unsigned long long[:] grid,
                                    unsigned long long[:] candidates,
                                    const Py_ssize_t[:,:] group_indices):

    cdef Py_ssize_t i, j
    cdef Py_ssize_t grid_size = grid.shape[0]
    cdef Py_ssize_t group_size = group_indices.shape[1]

    for i in range(grid_size):  # Parallel
        pass


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline Py_ssize_t find_naked_single(Py_ssize_t index,
                                         unsigned long long[:] candidates,
                                         const Py_ssize_t[:] group_indices):

    cdef Py_ssize_t i
    cdef Py_ssize_t group_size = group_indices.shape[0]

    for i in range(group_size):
        candidates[group_indices[i]] &= ~candidates[index]


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline Py_ssize_t apply_naked_single(Py_ssize_t index,
                                          unsigned long long[:] candidates,
                                          const Py_ssize_t[:] group_indices):

    cdef Py_ssize_t i
    cdef Py_ssize_t group_size = group_indices.shape[0]

    for i in range(group_size):
        candidates[group_indices[i]] &= ~candidates[index]


# noinspection PyUnresolvedReferences
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline unsigned long long fetch_candidates(
        unsigned long long[::1] grid, Py_ssize_t[:] group_indices) nogil:

    cdef unsigned long long total = 0
    cdef Py_ssize_t size = group_indices.shape[0]
    cdef Py_ssize_t i

    for i in range(size):
        total |= grid[group_indices[i]]

    return ~total
