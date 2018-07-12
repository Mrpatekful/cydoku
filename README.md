# Sudokugen

This repository holds a baseline Python implementation of a backtracking brute force algorithm for solving sudoku.
Integration of optimizations for reducing the branching factor of the search is in progress, as well as different techniques, like `constraint based modelling` or
the famous `dancing-links` method. Currently only single threaded version exists, however I am experimenting with the
efficiency and speed of multi-threaded implementations.

### Benchmarks

CPU: Intel(R) Core(TM) i7-4710HQ CPU @ 2.50GHz
RAM: 8GB

As I have mentioned the code is written in Python, however to evade the overhead of the language, I have used Cython
as the core of the project. This way, the algorithm runs at considerable speed and efficiency.

According to Wikipedia, the following puzzle takes a long time for a basic brute force method.

        +-------+-------+-------+
        | . . . | . . . | . . . |
        | . . . | . . 3 | . 8 5 |
        | . . 1 | . 2 . | . . . |
        +-------+-------+-------+
        | . . . | 5 . 7 | . . . |
        | . . 4 | . . . | 1 . . |
        | . 9 . | . . . | . . . |
        +-------+-------+-------+
        | 5 . . | . . . | . 7 3 |
        | . . 2 | . 1 . | . . . |
        | . . . | . 4 . | . . 9 |
        +-------+-------+-------+

*"A Sudoku can be constructed to work against backtracking. Assuming the solver works from top to bottom
, a puzzle with few clues (17), no clues in the top row, and has a solution "987654321" for the first row,
would work in opposition to the algorithm. Thus the program would spend significant time "counting"
upward before it arrives at the grid which satisfies the puzzle."*

In the current version, no optimization measures have been applied to the search, and still,
the required time for the algorithm to solve this puzzle is ~ __0.24ms__ .



After deleting some of the given clues (12) of this puzzle,
and making it ambiguous it is possible to traverse a wide range of solutions.

        +-------+-------+-------+
        | . . . | . . . | . . . |
        | . . . | . . . | . 8 5 |
        | . . 1 | . . . | . . . |
        +-------+-------+-------+
        | . . . | 5 . 7 | . . . |
        | . . . | . . . | . . . |
        | . 9 . | . . . | . . . |
        +-------+-------+-------+
        | 5 . . | . . . | . 7 3 |
        | . . 2 | . . . | . . . |
        | . . . | . 4 . | . . 9 |
        +-------+-------+-------+

The search manages to find __10,000,000__ solutions to the new puzzle in ~ __74s__ .


### Features

There are currently two methods to follow the process of solving a sudoku.
The debug version of the algorithm features a display mode, using the PyGame module.

![PyGame visualization](https://github.com/Mrpatekful/sudokugen/blob/master/sudoku.gif)


And a 'dump' mode, that logs every state of the algorithm to a file (debug.txt by default).

### Usage

```python3 main.py -s 3```

Will generate a randomly filled sudoku from an empty state. Size 3 is the general 9 x 9 sudoku field.
Solution will be generated to the location given by -o, --output, which is solution.txt by default.


```python3 main.py -s 3 -f input.txt```

Will read the content of the provided file, that is a 9 x 9 sudoku field.
The format of the file must be the following.

    0 0 0 0 0 0 0 0 0
    0 0 0 0 0 0 0 8 5
    0 0 1 0 0 0 0 0 0
    0 0 0 5 0 7 0 0 0
    0 0 0 0 0 0 0 0 0
    0 9 0 0 0 0 0 0 0
    5 0 0 0 0 0 0 7 3
    0 0 2 0 0 0 0 0 0
    0 0 0 0 4 0 0 0 9


```python3 main.py -s 3 -f input.txt -d pygame -t 0.5```

Will use the PyGame visualization, with 0.5 second delay between each frame. The default delay is zero.


```python3 main.py -s 4 --max 10000000```

Will generate a 16 x 16 sudoku grid from an empty state, and tries to find a maximum of 10,000,000 solutions.


### Requirements

- __Python3.x__
- __Cython__
- __gmpy2__
- __NumPy__
