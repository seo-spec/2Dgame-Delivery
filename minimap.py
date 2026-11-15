"""전체 월드를 북쪽 고정 축척으로 표시하는 화면 고정 미니맵."""

from math import cos, sin, hypot, sqrt, tau

from pico2d import draw_line, draw_rectangle, get_canvas_width, get_canvas_height

from road_geometry import ROAD_WIDTH_RATIO
import settings


MINIMAP_RADIUS = 104
MINIMAP_MARGIN = 16
MINIMAP_RESERVED_WIDTH = MINIMAP_RADIUS * 2 + MINIMAP_MARGIN * 2
MAP_CONTENT_RADIUS = 82  # 기존 반경 120 - 여백 38의 지도 축척을 유지한다.


class MiniMap:
    def __init__(self, road_map, font):
        self.font = font
        self.width, self.height = road_map.width, road_map.height
        self.config = road_map.config
        self.scale = MAP_CONTENT_RADIUS / hypot(self.width / 2, self.height / 2)
        self.roads = []
        tile = road_map.tile_size
        half = tile * ROAD_WIDTH_RATIO / 2
        for start, end in self.config['road_segments']:
            x1, y1 = ((value + 0.5) * tile for value in start)
            x2, y2 = ((value + 0.5) * tile for value in end)
            self.roads.append((min(x1, x2) - half, min(y1, y2) - half,
                               max(x1, x2) + half, max(y1, y2) + half))

    def world_to_minimap(self, x, y):
        return (self.center_x + (x - self.width / 2) * self.scale,
                self.center_y + (y - self.height / 2) * self.scale)

    @property
    def center_x(self):
        return settings.VIEWPORT_LEFT + settings.VIEWPORT_WIDTH - MINIMAP_MARGIN - MINIMAP_RADIUS

    @property
    def center_y(self):
        return get_canvas_height() - 80 - MINIMAP_RADIUS

    def _rectangle(self, bounds, color):
        left, bottom = self.world_to_minimap(bounds[0], bounds[1])
        right, top = self.world_to_minimap(bounds[2], bounds[3])
        draw_rectangle(round(left), round(bottom), round(right), round(top), *color, filled=True)

    def _text(self, text, x, y, color):
        # 테두리 근처 글자도 전체가 원 안에 들어오도록 위치를 보정한다.
        width = sum(18 if ord(char) > 127 else 10 for char in text)
        y = max(self.center_y - MINIMAP_RADIUS + 20,
                min(self.center_y + MINIMAP_RADIUS - 22, y))
        extent = max(abs(y - 5 - self.center_y), abs(y + 20 - self.center_y))
        half = sqrt(max(0, (MINIMAP_RADIUS - 3) ** 2 - extent ** 2))
        x = max(self.center_x - half + 2, min(self.center_x + half - width - 2, x))
        self.font.draw(round(x + 1), round(y - 1), text, (0, 0, 0))
        self.font.draw(round(x), round(y), text, color)

    def draw(self, motorcycle, delivery_houses):
        cx, cy = self.center_x, self.center_y
        radius = MINIMAP_RADIUS
        # 원 내부만 채운다. 지도는 여백을 둔 내접 직사각형에 종횡비를 유지해 표시한다.
        for offset in range(-radius + 1, radius):
            half = int(sqrt(radius * radius - offset * offset))
            draw_line(round(cx - half), round(cy + offset),
                      round(cx + half), round(cy + offset), 28, 43, 47)
        self._rectangle((0, 0, self.width, self.height), (75, 112, 82))
        for bounds in self.roads:
            self._rectangle(bounds, (55, 63, 68))
        for building in self.config['buildings']:
            x, y = building['position']
            width, height = building['size']
            self._rectangle((x - width / 2, y - height / 2,
                             x + width / 2, y + height / 2), (176, 153, 124))
            if building.get('id') == 'delivery_depot':
                sx, sy = self.world_to_minimap(x, y)
                draw_rectangle(round(sx - 4), round(sy - 4), round(sx + 4), round(sy + 4),
                               255, 180, 65, filled=True)
                self._text('배달소', sx - 25, sy - 20, (255, 210, 120))
        for house in delivery_houses:
            x, y = self.world_to_minimap(house.x, house.y)
            color = (115, 245, 160) if house.delivered else (255, 220, 95)
            draw_rectangle(round(x - 3), round(y - 3), round(x + 3), round(y + 3),
                           *color, filled=not house.delivered)
            # 색 외에도 완료 기호를 추가한다. A~E의 짧은 이름으로 서로 구분한다.
            self._text(house.label.removesuffix('집') + ('+' if house.delivered else ''),
                       x + 5, y + 3, color)
        x, y = self.world_to_minimap(motorcycle.x, motorcycle.y)
        forward = (cos(motorcycle.angle), sin(motorcycle.angle))
        points = [(x + forward[0] * 7, y + forward[1] * 7),
                  (x - forward[0] * 4 - forward[1] * 4, y - forward[1] * 4 + forward[0] * 4),
                  (x - forward[0] * 4 + forward[1] * 4, y - forward[1] * 4 - forward[0] * 4)]
        for index, start in enumerate(points):
            end = points[(index + 1) % len(points)]
            draw_line(round(start[0]), round(start[1]), round(end[0]), round(end[1]), 100, 220, 255)
        for index in range(96):
            angle, next_angle = tau * index / 96, tau * (index + 1) / 96
            draw_line(round(cx + cos(angle) * radius), round(cy + sin(angle) * radius),
                      round(cx + cos(next_angle) * radius), round(cy + sin(next_angle) * radius),
                      220, 235, 225)
