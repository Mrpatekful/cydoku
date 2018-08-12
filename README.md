# Cydoku

This repository holds a baseline Python implementation of a backtracking brute force algorithm for solving sudoku.
The technique is accelerated by using bitwise operations

### Benchmarks

CPU: Intel(R) Core(TM) i7-4710HQ CPU @ 2.50GHz
RAM: 8GB

*A Sudoku can be constructed to work against backtracking. Assuming the solver works from top to bottom
, a puzzle with few clues (17), no clues in the top row, and has a solution "987654321" for the first row,
would work in opposition to the algorithm. Thus the program would spend significant time "counting"
upward before it arrives at the grid which satisfies the puzzle.*

In the current version, no deductive search space reduction techniques have been implemented in the algorithm, and still,
the required time for the algorithm to solve such a puzzle is ~ __0.24ms__ .

After deleting some of the given clues (12) of this puzzle,
and making it ambiguous, it is possible to traverse a wide range of solutions.

### Requirements

- Python3.5
- [Cython](http://cython.org/)
- [gmpy2](http://gmpy2.readthedocs.io/en/latest/intro.html)
- [NumPy](https://www.scipy.org/scipylib/download.html)
