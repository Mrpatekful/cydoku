"""

"""

import argparse
import logging

import sudokugen
import debug
import os


logFormatter = logging.Formatter(
    '%(asctime)s %(levelname)s  %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileHandler = logging.FileHandler(
    '{}.log'.format(os.path.splitext(__file__)[0]))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--size',
        type=int, help='size of the generated grid (size*size)', default=3)
    parser.add_argument(
        '-o', '--output',
        type=str, help='path of the output', default='solution.txt')
    parser.add_argument(
        '-d', '--debug',
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
        '-f', '--file',
        help='show the full screen with candidates (max(n) = 3)',
        type=str, default=None)
    parser.add_argument(
        '-r', '--refresh',
        help='refresh rate for the visualization', type=int, default=1)
    parser.add_argument(
        '-m', '--max',  help='maximum solutions to find',  type=int, default=1)
    args = parser.parse_args(
        ['-s', '3', '-t', '1', '-m', '1', '-d', 'pygame',
         '-f', 'input.txt', '-w', '1'])

    if args.debug is not None:
        if args.debug == 'pygame':
            def debug_method(size, conv):
                return debug.PyGame(
                    n=size, conv=conv, delay=args.time, wait=args.wait)

        elif args.debug == 'printer':
            def debug_method(size, _):
                return debug.Printer(n=size, m=args.max, path='debug.txt')

        else:
            raise ValueError('Invalid value for (-d, --debug)')

        try:

            gen = sudokugen.DebugBruteForceSearch(
                args.size, args.max, debugger=debug_method)

        except ValueError as error:
            logger.error(error)
            return

    else:
        gen = sudokugen.BruteForceSearch(args.size, args.max)

    field = None
    if args.file is not None:
        field = sudokugen.Solver.load(args.file)
        field = gen.encode(field)

    delta_time, (solutions, raw_time) = gen.fill(field)

    # Using milliseconds for logging
    ms = 1000

    if solutions == 0:
        logger.info('{}x{} no solutions in {:.6} ms ({:.6} ms) by {}'.format(
            args.size ** 2, args.size ** 2, delta_time * ms,
            raw_time * ms, gen))

    elif solutions > 1:
        logger.info('{}x{} {} solutions found in {:.6} ms ({:.6} ms) by {}'
                    .format(args.size ** 2, args.size ** 2,
                            solutions, delta_time * ms, raw_time * ms, gen))

    elif solutions == 1 and args.max == 1:
        logger.info('{}x{} filled in {:.6} ms ({:.6} ms) by {}'.format(
            args.size ** 2, args.size ** 2,
            delta_time * ms, raw_time * ms, gen))

    else:
        logger.info('{}x{} 1 solution found in {:.6} ms ({:.6} ms) by {}'.
                    format(args.size**2, args.size**2,
                           delta_time * ms, raw_time * ms, gen))

    gen.save_txt(args.output)


if __name__ == '__main__':
    main()
