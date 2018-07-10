import pygame
import time


class Display:

    def __init__(self, full_layout):
        self.full_layout = full_layout

    def update(self, grid, candidates, iteration):
        raise NotImplementedError

    def wait(self, s):
        raise NotImplementedError


class Printer(Display):
    def __init__(self, full_layout):
        super().__init__(full_layout)

    def update(self, grid, candidates, iteration):
        print()
        time.sleep(0)

    def wait(self, s):
        time.sleep(s)


class PyGame(Display):

    _WIDTH = 1200
    _HEIGHT = 500

    def __init__(self, n, k=10000, full_layout=False, delay=0):
        super().__init__(full_layout)
        self.n = n
        self.k = k
        self.delay = delay

        pygame.init()

        if self.full_layout:
            w = self._WIDTH
        else:
            w = self._HEIGHT

        self.window = pygame.display.set_mode((w, self._HEIGHT))
        self.grid_wrapper = GridWrapper(
            self.window, self.n, self._HEIGHT, self._HEIGHT, SingleNumber)
        self.candidate_wrapper = None
        if full_layout:
            self.candidate_wrapper = GridWrapper(
                self.window, self.n,
                self._WIDTH - self._HEIGHT, self._HEIGHT,
                NumberSet, translate=self._HEIGHT
            )

    def update(self, grid, candidates, iteration):
        if iteration % self.k == 0:
            self.window.fill((0, 0, 0))
            self.grid_wrapper.draw(grid)

            if self.candidate_wrapper is not None:
                pygame.draw.line(
                    self.window,
                    (255, 255, 255),
                    (self._HEIGHT, 0),
                    (self._HEIGHT, self._HEIGHT), 4)
                self.candidate_wrapper.draw(candidates)
            pygame.display.update()
            time.sleep(self.delay)

    def wait(self, s):
        time.sleep(s)


class GridWrapper:

    _LINE_COLOR = (255, 255, 255)

    def __init__(self, window, n, width, height, cell, translate=0):
        self.n = n
        self.width = width
        self.height = height
        self.window = window
        self.translate = translate
        self.cells = [
            [cell(window, width * col_index / self.n ** 2 + translate,
                  height * row_index / self.n ** 2,
                  self.width / self.n ** 2, self.n ** 2)
             for col_index in range(self.n ** 2)]
            for row_index in range(self.n ** 2)]

    def draw(self, grid):
        for index in range(self.n - 1):
            pygame.draw.line(
                self.window,
                (255, 255, 255),
                (self.translate, self.height / self.n * (index + 1)),
                (self.translate + self.width,
                 self.height / self.n * (index + 1)), 1)
            pygame.draw.line(
                self.window,
                (255, 255, 255),
                (self.translate + self.width / self.n * (index + 1), 0),
                (self.translate + self.width / self.n * (index + 1),
                 self.height), 1)

        for row_index in range(len(self.cells)):
            for col_index in range(len(self.cells)):
                self.cells[row_index][col_index] \
                    .draw(grid[row_index][col_index])


class SingleNumber:

    _NUMBER_COLOR = (255, 0, 0)
    _Q_MARK_COLOR = (100, 0, 0)
    _FILL_COLOR = (255, 255, 0)
    _BORDER = 1

    def __init__(self, window, x, y, size, _):
        self.x = x
        self.y = y
        self.size = size
        self.window = window
        self.font = pygame.font.SysFont('Comic Sans MS', int(self.size))

    def draw(self, number):
        text = self.font.render(
            str(number if number != 0 else '?'), True,
            self._NUMBER_COLOR if number != 0 else self._Q_MARK_COLOR)
        self.window.blit(
            text, (self.x + self.size / 4, self.y + self.size / 4))


class NumberSet:

    _FONT_COLOR = (255, 255, 255)
    _UNIQUE_COLOR = (0, 200, 0)
    _NA_COLOR = (200, 0, 0)
    _BORDER = 1

    def __init__(self, window, x, y, size, numbers):
        self.x = x
        self.y = y
        self.size = size
        self.numbers = numbers
        self.window = window
        self.font = pygame.font.SysFont('Comic Sans MS', int(self.size / 4))

    def draw(self, candidates):
        if len(candidates) > 10:
            full = list(map(str, candidates))
            print_text = '[{} ... {}]'.format(''.join(full[:2]),
                                              ''.join(full[-2:]))

            text = self.font.render(print_text, True, self._FONT_COLOR)
            self.window.blit(
                text, (self.x + self.size / 4,
                       self.y + self.size / 4 - self.size / 10))

        elif len(candidates) > self.numbers // 2 or len(candidates) > 5:
            full = list(map(str, candidates))
            divider = min(self.numbers // 2, 5)
            first_half = '[{}'.format(''.join(full[:divider]))
            second_half = '{}]'.format(''.join(full[divider:]))
            text = self.font.render(first_half, True, self._FONT_COLOR)
            self.window.blit(
                text, (self.x + self.size / 4,
                       self.y + self.size / 4 - self.size / 10))
            text = self.font.render(second_half, True, self._FONT_COLOR)
            self.window.blit(
                text, (self.x + self.size / 4, self.y +
                       self.size / 4 + self.size / 10))

        else:
            if len(candidates) == 1:
                print_text = '[{}]'.format(''.join(list(map(str, candidates))))
                font_color = self._UNIQUE_COLOR

            elif len(candidates) == 0:
                print_text = 'N/A'
                font_color = self._NA_COLOR

            else:
                print_text = '[{}]'.format(''.join(list(map(str, candidates))))
                font_color = self._FONT_COLOR
            text = self.font.render(print_text, True, font_color)
            self.window.blit(
                text, (self.x + self.size / 4, self.y + self.size / 4))
