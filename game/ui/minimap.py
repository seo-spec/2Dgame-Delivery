"""전체 월드를 북쪽 고정 축척으로 표시하는 화면 고정 미니맵."""

from math import ceil, cos, floor, sin, hypot, sqrt, tau

from pico2d import draw_line, draw_rectangle, get_canvas_width, get_canvas_height

from game.world.road_geometry import ROAD_WIDTH_RATIO
from game.config import settings
from game.config.meteor import BLOCK_DURATION
MINIMAP_RADIUS = 104
MINIMAP_MARGIN = 16
MINIMAP_RESERVED_WIDTH = MINIMAP_RADIUS * 2 + MINIMAP_MARGIN * 2
MAP_CONTENT_RADIUS = 82  # 기존 반경 120 - 여백 38의 지도 축척을 유지한다.
WARNING_RED = (255, 83, 73)
BLOCK_RED = (220, 61, 56)


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

    def _circle_line(self, x1, y1, x2, y2, color):
        """원형 미니맵 내부와 겹치는 선분만 출력한다."""
        dx, dy = x2 - x1, y2 - y1
        ox, oy = x1 - self.center_x, y1 - self.center_y
        radius = MINIMAP_RADIUS - 2
        a = dx * dx + dy * dy
        if a == 0:
            if ox * ox + oy * oy <= radius * radius:
                draw_line(round(x1), round(y1), round(x1), round(y1), *color)
            return
        b = ox * dx + oy * dy
        discriminant = b * b - a * (ox * ox + oy * oy - radius * radius)
        if discriminant < 0:
            return
        root = sqrt(discriminant)
        start, end = max(0.0, (-b - root) / a), min(1.0, (-b + root) / a)
        if start <= end:
            draw_line(round(x1 + dx * start), round(y1 + dy * start),
                      round(x1 + dx * end), round(y1 + dy * end), *color)

    def _ring(self, x, y, radius, color):
        for index in range(48):
            a, b = tau * index / 48, tau * (index + 1) / 48
            self._circle_line(x + cos(a) * radius, y + sin(a) * radius,
                              x + cos(b) * radius, y + sin(b) * radius, color)

    def _disk(self, x, y, radius, color):
        if radius <= 0:
            return
        clip_radius = MINIMAP_RADIUS - 2
        for row in range(max(ceil(y - radius), ceil(self.center_y - clip_radius)),
                         min(floor(y + radius), floor(self.center_y + clip_radius)) + 1):
            half = sqrt(max(0.0, radius * radius - (row - y) ** 2))
            clip_half = sqrt(max(0.0, clip_radius ** 2 - (row - self.center_y) ** 2))
            left = ceil(max(x - half, self.center_x - clip_half))
            right = floor(min(x + half, self.center_x + clip_half))
            if left <= right:
                draw_line(left, row, right, row, *color)

    def _meteor_markers(self, meteor_system):
        # 상태 복제나 별도 타이머 없이 실제 목록과 차단 잔여 시간을 참조한다.
        for crater in meteor_system.obstacles:
            x, y = self.world_to_minimap(crater.x, crater.y)
            radius = max(3.0, min(5.0, crater.radius * self.scale))
            remaining = meteor_system.crater_remaining(crater.obstacle_id)
            if remaining is None:
                self._disk(x, y, radius, BLOCK_RED)
                self._circle_line(x - radius * 0.65, y, x + radius * 0.65, y, (255, 240, 225))
            else:
                fraction = max(0.0, min(1.0, remaining / BLOCK_DURATION))
                self._disk(x, y, radius * fraction, BLOCK_RED)
            # 외곽선은 차단이 실제로 끝날 때까지 같은 크기로 유지한다.
            self._ring(x, y, radius, WARNING_RED)
        for meteor in meteor_system.meteors:
            x, y = self.world_to_minimap(meteor.x, meteor.y)
            radius = max(3.0, min(5.0, meteor.radius * self.scale))
            color = WARNING_RED if meteor.warning_bright else (135, 48, 45)
            self._ring(x, y, radius, color)

    def overlay_bounds(self):
        """월드 안내 문구가 피해야 하는 미니맵·범례 화면 영역."""
        return (self.center_x - MINIMAP_RADIUS - 8, self.center_y - MINIMAP_RADIUS - 76,
                self.center_x + MINIMAP_RADIUS + 8, self.center_y + MINIMAP_RADIUS + 8)

    def draw(self, motorcycle, delivery_houses, meteor_system=None, returning=False):
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
        if meteor_system is not None:
            self._meteor_markers(meteor_system)
        # 운석 위에 목적지·복귀·플레이어를 그려 우선순위를 보장한다.
        for building in self.config['buildings']:
            if building.get('id') != 'delivery_depot':
                continue
            x, y = building['position']
            zone = building.get('pickup_zone')
            if zone:
                x, y = x + zone['offset'][0], y + zone['offset'][1]
            sx, sy = self.world_to_minimap(x, y)
            color = (115, 245, 160) if returning else (255, 180, 65)
            self._disk(sx, sy, 4, color)
            if returning:
                self._ring(sx, sy, 7, color)
            self._text('복귀' if returning else '배달소', sx - 25, sy - 20, color)
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
            self._circle_line(start[0], start[1], end[0], end[1], (100, 220, 255))
        for index in range(96):
            angle, next_angle = tau * index / 96, tau * (index + 1) / 96
            draw_line(round(cx + cos(angle) * radius), round(cy + sin(angle) * radius),
                      round(cx + cos(next_angle) * radius), round(cy + sin(next_angle) * radius),
                      220, 235, 225)
        if meteor_system is not None:
            legend_x, legend_y = cx - radius, cy - radius - 22
            self.font.draw(round(legend_x), round(legend_y), '점멸 원: 낙하', WARNING_RED)
            self.font.draw(round(legend_x), round(legend_y - 22), '채움: 해제까지', (255, 186, 165))
            self.font.draw(round(legend_x), round(legend_y - 44), '가로선: 수동 차단', (225, 220, 210))
