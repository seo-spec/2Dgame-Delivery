"""공통 치수로 만든 도로 도형. 생성 이미지의 연결부 오차를 제거한다."""

from math import ceil, cos, floor, pi, sin, sqrt

from pico2d import draw_rectangle


GRASS_COLOR = (75, 112, 82)
ASPHALT_COLOR = (66, 73, 77)
SIDEWALK_COLOR = (219, 201, 168)
MARKING_COLOR = (241, 239, 225)
ROAD_WIDTH_RATIO = 0.4
SIDEWALK_WIDTH_RATIO = 0.0466666667


def rotate_mask(mask):
    return (mask >> 1) | ((mask & 1) << 3)


class RoadGeometry:
    def __init__(self, size):
        self.size = size
        self.road_width = round(size * ROAD_WIDTH_RATIO)
        self.sidewalk_width = round(size * SIDEWALK_WIDTH_RATIO)
        self.tiles = {}
        # 렌더링과 판정이 같은 _surface 도형을 공유한다. 좌표는 양 끝 픽셀 포함.
        self.road_tiles = {}
        for original in (0, 5, 3, 11, 15, 4):
            shapes = self._make_tile(original)
            road = self._surface(original, self.road_width / 2)
            mask = original
            for turns in range(4):
                if mask not in self.tiles:
                    self.road_tiles[mask] = tuple(self._rotate_rect(rect, turns) for rect in road)
                    self.tiles[mask] = [
                        (*self._rotate_rect(rect, turns), color) for rect, color in shapes
                    ]
                mask = rotate_mask(mask)

    def _rotate_rect(self, rect, turns):
        x1, y1, x2, y2 = rect
        for _ in range(turns):
            x1, y1, x2, y2 = self.size - 1 - y2, x1, self.size - 1 - y1, x2
        return x1, y1, x2, y2

    def _surface(self, mask, half_width):
        size = self.size
        center = size / 2
        low, high = round(center - half_width), round(center + half_width) - 1
        if mask == 5:
            return [(low, 0, high, size - 1)]
        if mask in (11, 15):
            rectangles = [(0, low, size - 1, high), (low, low, high, size - 1)]
            if mask == 15:
                rectangles.append((low, 0, high, high))
            return rectangles

        # 곡선과 막다른 길은 행별로 계산하고 같은 폭의 연속 행은 합친다.
        rectangles = []
        for y in range(size):
            if mask == 3:
                dy = size - (y + 0.5)
                outer = center + half_width
                inner = center - half_width
                if dy > outer:
                    continue
                left = size - sqrt(max(0.0, outer * outer - dy * dy))
                right = size - sqrt(max(0.0, inner * inner - dy * dy)) if dy < inner else size
                x1 = max(0, ceil(left - 0.5))
                x2 = min(size - 1, floor(right - 0.5))
            elif mask == 4:
                if y + 0.5 <= center:
                    x1, x2 = low, high
                else:
                    dy = y + 0.5 - center
                    if dy > half_width:
                        continue
                    radius = sqrt(max(0.0, half_width * half_width - dy * dy))
                    x1 = ceil(center - radius - 0.5)
                    x2 = floor(center + radius - 0.5)
            else:
                return []
            if x1 > x2:
                continue
            if rectangles and rectangles[-1][0] == x1 and rectangles[-1][2] == x2 and rectangles[-1][3] == y - 1:
                old_x1, old_y1, old_x2, _ = rectangles[-1]
                rectangles[-1] = (old_x1, old_y1, old_x2, y)
            else:
                rectangles.append((x1, y, x2, y))
        return rectangles

    def _make_tile(self, mask):
        if mask == 0:
            return []
        half = self.road_width / 2
        shapes = [(rect, SIDEWALK_COLOR) for rect in self._surface(mask, half + self.sidewalk_width)]
        shapes += [(rect, ASPHALT_COLOR) for rect in self._surface(mask, half)]
        center = self.size // 2
        if mask in (5, 4):
            limit = self.size if mask == 5 else center
            period = self.size // 6
            for y in range(period // 4, limit, period):
                shapes.append(((center - 1, y, center + 1, min(y + period // 3, limit - 1)), MARKING_COLOR))
        elif mask == 3:
            for degrees in range(5, 85):
                if degrees % 20 >= 11:
                    continue
                angle = pi + degrees * pi / 180
                x = round(self.size + center * cos(angle))
                y = round(self.size + center * sin(angle))
                shapes.append(((x - 1, y - 1, x + 1, y + 1), MARKING_COLOR))
        else:
            # 교차로 중앙은 비우고 연결 입구에만 중심선을 표시한다.
            for turns in range(4):
                bit = (1, 8, 4, 2)[turns]
                if not mask & bit:
                    continue
                dash = (center - 1, self.size - 32, center + 1, self.size - 13)
                shapes.append((self._rotate_rect(dash, turns), MARKING_COLOR))
                if mask == 15:
                    stop_line = (center - half + 5, self.size - 30, center - 5, self.size - 26)
                    shapes.append((self._rotate_rect(stop_line, turns), MARKING_COLOR))
                    for x in range(round(center - half + 6), round(center + half - 6), 12):
                        stripe = (x, self.size - 62, x + 5, self.size - 39)
                        shapes.append((self._rotate_rect(stripe, turns), MARKING_COLOR))
        return shapes

    def draw(self, mask, screen_left, screen_bottom):
        # 모든 타일의 원점을 같은 기준으로 반올림해 픽셀 틈을 방지한다.
        left, bottom = round(screen_left), round(screen_bottom)
        for x1, y1, x2, y2, color in self.tiles[mask]:
            draw_rectangle(left + x1, bottom + y1, left + x2, bottom + y2, *color, filled=True)
