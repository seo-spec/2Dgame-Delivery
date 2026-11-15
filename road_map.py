"""공통 규격의 도로와 이미지 장식으로 구성한 샘플 맵."""

import json
from pathlib import Path

from pico2d import draw_rectangle, load_image

import settings
from road_geometry import GRASS_COLOR, RoadGeometry


ROOT = Path(__file__).resolve().parent
# 북·동·남·서 연결 비트.
DIRECTIONS = ((0, 1, 1), (1, 0, 2), (0, -1, 4), (-1, 0, 8))


class RoadMap:
    def __init__(self, camera):
        self.camera = camera
        self.width = settings.WORLD_WIDTH
        self.height = settings.WORLD_HEIGHT
        self.config = json.loads((ROOT / 'data/sample_map.json').read_text(encoding='utf-8'))
        self.tile_size = self.config['tile_size']
        if self.width % self.tile_size or self.height % self.tile_size:
            raise ValueError('World dimensions must be multiples of sample tile_size')
        self.columns = self.width // self.tile_size
        self.rows = self.height // self.tile_size
        self.roads = {}
        for start, end in self.config['road_segments']:
            self._add_segment(start, end)
        self.tiles = [
            (x, y, self.roads.get((x, y), 0))
            for y in range(self.rows) for x in range(self.columns)
        ]
        self.geometry = RoadGeometry(self.tile_size)
        self.spawn = self.config['spawn']

    def _add_segment(self, start, end):
        x, y = start
        end_x, end_y = end
        if x != end_x and y != end_y:
            raise ValueError('Road segments must be horizontal or vertical')
        dx = (end_x > x) - (end_x < x)
        dy = (end_y > y) - (end_y < y)
        forward = next((bit for vx, vy, bit in DIRECTIONS if (vx, vy) == (dx, dy)), 0)
        reverse = next((bit for vx, vy, bit in DIRECTIONS if (vx, vy) == (-dx, -dy)), 0)
        while True:
            if not (0 <= x < self.columns and 0 <= y < self.rows):
                raise ValueError('Road segment is outside the sample world')
            self.roads.setdefault((x, y), 0)
            if (x, y) == (end_x, end_y):
                break
            nx, ny = x + dx, y + dy
            self.roads[(x, y)] |= forward
            self.roads[(nx, ny)] = self.roads.get((nx, ny), 0) | reverse
            x, y = nx, ny

    def update(self):
        pass

    def draw(self):
        size = self.tile_size
        left, bottom = self.camera.world_to_screen(0, 0)
        right, top = self.camera.world_to_screen(self.width, self.height)
        draw_rectangle(round(left), round(bottom), round(right) - 1, round(top) - 1,
                       *GRASS_COLOR, filled=True)
        for x, y, mask in self.tiles:
            sx, sy = self.camera.world_to_screen((x + 0.5) * size, (y + 0.5) * size)
            if not self._visible(sx, sy, size, size):
                continue
            tile_left, tile_bottom = self.camera.world_to_screen(x * size, y * size)
            self.geometry.draw(mask, tile_left, tile_bottom)

    def _visible(self, x, y, width, height):
        camera = self.camera
        return (x + width / 2 >= camera.viewport_left
                and x - width / 2 <= camera.viewport_left + camera.viewport_width
                and y + height / 2 >= camera.viewport_bottom
                and y - height / 2 <= camera.viewport_bottom + camera.viewport_height)


class MapDecoration:
    """건물·신호등의 이미지 표시만 담당하는 월드 객체."""

    def __init__(self, camera, image, position, size):
        self.camera = camera
        self.image = image
        self.x, self.y = position
        self.width, self.height = size

    def update(self):
        pass

    def draw(self):
        x, y = self.camera.world_to_screen(self.x, self.y)
        self.image.draw(round(x), round(y), self.width, self.height)


def create_decorations(camera, config):
    decorations = []
    images = {
        name: load_image(str(ROOT / 'assets/images' / filename))
        for name, filename in (
            ('building', 'building_sample.png'),
            ('red', 'traffic_signal_red.png'),
            ('green', 'traffic_signal_green.png'),
        )
    }
    for item in config['buildings']:
        decorations.append(MapDecoration(camera, images['building'], item['position'], item['size']))
    for item in config['signals']:
        decorations.append(MapDecoration(camera, images[item['state']], item['position'], item['size']))
    return decorations
