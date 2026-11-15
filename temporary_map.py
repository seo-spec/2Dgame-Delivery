"""이미지 없이 격자와 구역 표식으로 표시하는 임시 월드."""

from pico2d import draw_line, draw_rectangle

import settings


GRID_SPACING = 100
MARKER_COLUMNS = 4
MARKER_ROWS = 3
MARKER_HALF_SIZE = 40


class TemporaryMap:
    def __init__(self):
        self.width = settings.WORLD_WIDTH
        self.height = settings.WORLD_HEIGHT

    def update(self):
        pass

    def draw(self):
        for x in range(0, self.width, GRID_SPACING):
            draw_line(x, 0, x, self.height)
        for y in range(0, self.height, GRID_SPACING):
            draw_line(0, y, self.width, y)
        draw_rectangle(0, 0, self.width, self.height)

        # 월드를 4열·3행으로 나누고 각 구역 중심에 표식을 둔다.
        for row in range(MARKER_ROWS):
            for column in range(MARKER_COLUMNS):
                x = round(self.width * (column + 0.5) / MARKER_COLUMNS)
                y = round(self.height * (row + 0.5) / MARKER_ROWS)
                self._draw_marker(x, y, column, row)

    def _draw_marker(self, x, y, column, row):
        size = MARKER_HALF_SIZE
        draw_rectangle(x - size, y - size, x + size, y + size)
        # 세로선 개수는 왼쪽부터 1~4열, 가로선 개수는 아래부터 1~3행.
        for index in range(column + 1):
            tick_x = x - 24 + index * 16
            draw_line(tick_x, y - 24, tick_x, y + 24)
        for index in range(row + 1):
            tick_y = y - 16 + index * 16
            draw_line(x - 32, tick_y, x + 32, tick_y)
