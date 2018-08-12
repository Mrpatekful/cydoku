
import pygame
import time
import math
import gmpy2


class Debugger:

    def update(self, grid, candidate_values,
               candidate_nums, value, state, filled, found):
        raise NotImplementedError


class Printer(Debugger):

    max_state = 10000

    def __init__(self, n, m, path='debug.txt'):

        if n != 3:
            raise ValueError('Printer debugger '
                             'available for n = 3 value only.')

        self.max = m
        self.file = open(path, 'w', encoding='utf-8')
        self.counter = 1
        self.n = n

    def update(self, grid, candidate_values,
               candidate_nums, value, state, filled, found):

        def bits(x, f, u):
            return ''.join([f if int(x) & 1 << n else u for n in range(9)])

        def nums(x):
            return ''.join([str(n + 1) if int(x) & 1 << n
                            else '-' for n in range(9)])

        if self.counter > Printer.max_state:
            return

        self.file.write(''.join(['#'] * 97))
        self.file.write('\n#{} STEP {} {}#\n'.format(
            ''.join(['='] * ((88 - len(str(self.counter))) // 2)),
            self.counter,
            ''.join(['='] * int(
                math.ceil((88 - len(str(self.counter))) / 2)))))
        self.file.write('\nFILLED:\t\t{}\nSTATE:\t\t{}\nFOUND:\t\t{} / {}\n\n'.
                        format(filled, state, found, self.max))

        sep = ''.join(['-'] * 31)
        self.file.write('GRID:\n')
        for i in range(self.n ** 2):
            if i % self.n == 0:
                self.file.write('+{}+{}+{}+\n'.format(sep, sep, sep))

            self.file.write('| {} {} {} | {} {} {} | {} {} {} |\n'.format(
                *['   ({})   '.format(
                    int(gmpy2.bit_scan1(grid[i * self.n ** 2 + j])) + 1 if
                    int(grid[i * self.n ** 2 + j]) != 0 else '?') for j
                  in range(self.n ** 2)]))

            self.file.write('| {} {} {} | {} {} {} | {} {} {} |\n'.format(
                *[bits(grid[i * self.n ** 2 + j], '#', '.') if
                  grid[i * self.n ** 2 + j] != 0 else ''.join([' '] * 9) for j
                  in range(self.n ** 2)]))

        self.file.write('+{}+{}+{}+\n'.format(sep, sep, sep))
        self.file.write('\nCANDIDATES:\n')
        for i in range(self.n ** 2):
            if i % self.n == 0:
                self.file.write('+{}+{}+{}+\n'.format(sep, sep, sep))

            self.file.write('| {} {} {} | {} {} {} | {} {} {} |\n'.format(
                *['   ({})   '.format(
                    candidate_nums[i * self.n ** 2 + j]) for j
                  in range(self.n ** 2)]))

            self.file.write('| {} {} {} | {} {} {} | {} {} {} |\n'.format(
                *[nums(candidate_values[i * self.n ** 2 + j]) if
                  grid[i * self.n ** 2 + j] == 0 else
                  ''.join([' '] * 9) for j
                  in range(self.n ** 2)]))

        self.file.write('+{}+{}+{}+\n\n'.format(sep, sep, sep))

        self.counter += 1

    def close(self):
        self.file.close()


class PyGame(Debugger):

    _WIDTH = 260
    _HEIGHT = 260

    def __init__(self, n, conv, delay=0, wait=0):
        self.n = n
        self.delay = delay
        self.convert_grid, self.convert_candidates = conv
        self.wait = wait

        pygame.init()

        self.window = pygame.display.set_mode((self._WIDTH, self._HEIGHT))
        self.grid_wrapper = Grid(
            self.window, self.n, self._HEIGHT, self._HEIGHT, Cell)

    def update(self, grid, candidate_values,
               candidate_nums, value, state, filled, found):

        self.window.fill((0, 0, 0))

        end = filled == (self.n ** 4)

        self.grid_wrapper.draw(
            self.convert_grid(grid, self.n),
            self.convert_candidates(candidate_values, self.n), end)

        pygame.display.update()
        time.sleep(self.delay)

        if end:
            time.sleep(self.wait)


class Grid:

    _line_color = (255, 255, 255)
    _sub_line_color = (155, 155, 155)
    _filled_color = (0, 100, 0)
    _unfilled_color = (255, 0, 0)

    def __init__(self, window, n, width, height, cell, translate=0):
        self.n = n
        self.width = width
        self.height = height
        self.window = window
        self.translate = translate
        self.cells = [
            [cell(window, width * col_index / self.n ** 2 + translate,
                  height * row_index / self.n ** 2,
                  self.width / self.n ** 2, n)
             for col_index in range(self.n ** 2)]
            for row_index in range(self.n ** 2)]

    def draw(self, grid, candidates, filled):
        for i in range(self.n - 1):
            for j in range(self.n):
                pygame.draw.line(
                    self.window,
                    Grid._sub_line_color,
                    (self.translate, self.height / self.n * j +
                     (self.height / self.n * (i + 1)) / self.n),
                    (self.translate + self.width,
                     self.height / self.n * j +
                     (self.height / self.n * (i + 1)) / self.n), 1)

            for j in range(self.n):
                pygame.draw.line(
                    self.window,
                    Grid._sub_line_color,
                    (self.translate + self.width / self.n * j +
                     (self.width / self.n * (i + 1)) / self.n, 0),
                    (self.translate + self.width / self.n * j +
                     (self.width / self.n * (i + 1)) / self.n, self.height), 1)

            pygame.draw.line(
                self.window,
                Grid._line_color,
                (self.translate, self.height / self.n * (i + 1)),
                (self.translate + self.width,
                 self.height / self.n * (i + 1)), 3)

            pygame.draw.line(
                self.window,
                Grid._line_color,
                (self.translate + self.width / self.n * (i + 1), 0),
                (self.translate + self.width / self.n * (i + 1),
                 self.height), 3)

        color = Grid._filled_color if filled else Grid._unfilled_color

        for row_index in range(len(self.cells)):
            for col_index in range(len(self.cells)):
                self.cells[row_index][col_index] \
                    .draw(grid[row_index][col_index],
                          candidates[row_index][col_index], color)


class Cell:

    _mark_color = (100, 0, 0)
    _candidate_color = (255, 255, 255)

    def __init__(self, window, x, y, size, n):
        self.x = x
        self.y = y
        self.size = size
        self.window = window
        self.main_font = pygame.font.SysFont(
            'Comic Sans MS', int(self.size * 0.8))
        self.candidate_font = pygame.font.SysFont(
            'Comic Sans MS', int(self.size * 0.3))
        self.denominator = 3 if n == 3 else 4

    def draw(self, number, candidates, color):
        main = self.main_font.render(
            str(number if number != 0 else '?'), True,
            color if number != 0 else self._mark_color)

        self.window.blit(
            main, (self.x + self.size / self.denominator,
                   self.y + self.size / 4))

        if number == 0:
            candidates = list(map(str, candidates))

            if len(candidates) > 4:
                t = '{} .. {}'.format(','.join(candidates[:2]),
                                      ','.join(candidates[-2:]))
            else:
                t = ','.join(candidates)

            candidate = self.candidate_font.render(
                t, True, self._candidate_color)

            self.window.blit(
                candidate, (self.x + self.size / 8,
                            self.y + self.size / 4 + self.size / 2))
