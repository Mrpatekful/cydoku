"""

"""

import argparse
import logging

import sudokugen
import visual

import numpy


logFormatter = logging.Formatter(
    '%(asctime)s %(levelname)s  %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileHandler = logging.FileHandler('sudoku.log')
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m', '--method',
        type=str, help='method, that is used for generation',
        default='recursive')
    parser.add_argument(
        '-s', '--size',
        type=int, help='size of the generated grid (size*size)', default=3)
    parser.add_argument(
        '-o', '--output',
        type=str, help='path of the output', default='gen.txt')
    parser.add_argument(
        '-d', '--display',
        type=str, help='possible display types '
                       'are "pygame" or "console", default None', default=None)
    parser.add_argument(
        '-e', '--empty', type=int,
        help='number of empty fields of the generated grid', default=10)
    parser.add_argument(
        '-t', '--time', type=float,
        help='number of seconds between showed steps '
             '(only relevant with defined display)', default=0)
    parser.add_argument(
        '-w', '--wait', type=float,
        help='seconds of delay after finished generation', default=0)
    parser.add_argument(
        '-f', '--full',
        help='show the full screen with candidates (max(n) = 3)',
        action='store_true')
    parser.add_argument(
        '-r', '--refresh',
        help='refresh rate for the visualization',
        type=int, default=1)
    parser.add_argument(
        '-n', '--new', type=int)
    parser.add_argument('-b', '--benchmark',
                        help='toggle benchmark mode', action='store_true')
    args = parser.parse_args(
        ['-s', '3', '-t', '0', '-w', '3'])

    display_method = args.display
    if display_method == 'pygame':
        def display_method(size):
            return visual.PyGame(n=size, k=args.refresh, delay=args.time)
    elif display_method == 'console':
        display_method = visual.Printer

    non_candidate_checking_methods = ['swap', 'sort']

    full_layout = args.full
    if args.method in non_candidate_checking_methods and full_layout:
        logger.warning(
            '{} is not candidate checking method, full layout '
            'will not be used'.format(args.method))

        full_layout = False

    if args.benchmark:
        if args.display is not None or args.full:
            logger.warning('In benchmark mode, the layout is disabled')
            full_layout = False
            display_method = None

    if display_method is not None:
        gen = sudokugen.DebugBestFitGenerator(
            args.size, display=display_method)
    else:
        gen = sudokugen.BruteForceSearch(args.size)

    field = None
    if False:
        field = numpy.array([
            [0, 7, 0,   2, 5, 0,   4, 0, 0],
            [8, 0, 0,   0, 0, 0,   9, 0, 3],
            [0, 0, 0,   0, 0, 3,   0, 7, 0],

            [7, 0, 0,   0, 0, 4,   0, 2, 0],
            [1, 0, 0,   0, 0, 0,   0, 0, 7],
            [0, 4, 0,   5, 0, 0,   0, 0, 8],

            [0, 9, 0,   6, 0, 0,   0, 0, 0],
            [4, 0, 1,   0, 0, 0,   0, 0, 5],
            [0, 0, 7,   0, 8, 2,   0, 3, 0]
        ])

        field = gen.encode(field, 3)

    delta_time, _ = gen.fill(field)

    logger.info('{}x{} generated in {:.6}s'.format(
        args.size**2, args.size**2, delta_time))

    gen.save_txt(args.output)


if __name__ == '__main__':
    main()
