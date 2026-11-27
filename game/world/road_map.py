"""공통 규격의 도로와 이미지 장식으로 구성한 샘플 맵."""

import json
from pathlib import Path

from pico2d import draw_rectangle, load_image

from game.config import settings
from game.core import debug_view
from game.world.traffic_signal import TrafficSignal
from game.world.road_geometry import ASPHALT_COLOR, GRASS_COLOR, SIDEWALK_COLOR, RoadGeometry
from game.world.road_surface import RoadSurface
from game.world.road_finish import RoadFinish
from game.world.depot_ambience import DepotAmbience
from game.world.tree_sway import TreeSway


ROOT = Path(__file__).resolve().parents[2]
# 북·동·남·서 연결 비트.
DIRECTIONS = ((0, 1, 1), (1, 0, 2), (0, -1, 4), (-1, 0, 8))


class RoadMap:
    def __init__(self, camera):
        self.camera = camera
        self.width = settings.WORLD_WIDTH
        self.height = settings.WORLD_HEIGHT
        self.config = json.loads((ROOT / 'data/maps/sample_map.json').read_text(encoding='utf-8'))
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
        rectangles = [
            (x * self.tile_size + left, y * self.tile_size + bottom,
             x * self.tile_size + right + 1, y * self.tile_size + top + 1)
            for x, y, mask in self.tiles
            for left, bottom, right, top in self.geometry.road_tiles[mask]
        ]
        # 진입로의 아스팔트도 실제 그리는 범위와 동일하게 합친다. 연석 제외.
        for path in self.config.get('access_paths', []):
            left, bottom, right, top = path['bounds']
            curb = path['curb_width']
            rectangles.append((left + curb, bottom, right - curb, top + 1))
        self.road_surface = RoadSurface(rectangles)
        self.spawn = self.config['spawn']
        self.road_finish = None
        finish_config = self.config.get('road_finish')
        if finish_config:
            try:
                self.road_finish = RoadFinish(self, finish_config)
            except OSError as error:
                print(f'[도로 표현] {error}')

    def is_point_on_road(self, x, y):
        """월드 좌표 점의 도로 포함 여부. 건물 충돌과는 독립적이다."""
        return self.road_surface.contains_point(x, y)

    def is_circle_on_road(self, x, y, radius):
        """원 전체가 연결된 도로 형상 합집합 안에 있는지 판정한다."""
        return self.road_surface.contains_circle(x, y, radius)

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
        self._draw_access_paths()
        if self.road_finish is not None:
            self.road_finish.draw()

    def _draw_access_paths(self):
        # 건물 입구와 도로를 연결하는 진입로. 건물 이미지보다 먼저 출력한다.
        for path in self.config.get('access_paths', []):
            left, bottom, right, top = path['bounds']
            curb = path['curb_width']
            for x1, x2, color in (
                (left, right, SIDEWALK_COLOR),
                (left + curb, right - curb, ASPHALT_COLOR),
            ):
                sx1, sy1 = self.camera.world_to_screen(x1, bottom)
                sx2, sy2 = self.camera.world_to_screen(x2, top)
                draw_rectangle(round(sx1), round(sy1), round(sx2) - 1, round(sy2),
                               *color, filled=True)

    def _visible(self, x, y, width, height):
        camera = self.camera
        return (x + width / 2 >= camera.viewport_left
                and x - width / 2 <= camera.viewport_left + camera.viewport_width
                and y + height / 2 >= camera.viewport_bottom
                and y - height / 2 <= camera.viewport_bottom + camera.viewport_height)


class MapDecoration:
    """건물·도시 소품·신호등의 이미지 표시만 담당하는 월드 객체."""

    def __init__(self, camera, image, position, size, collision=None, object_id=None,
                 is_building=False, tree_sway=None, depot_layout='original'):
        self.camera = camera
        self.image = image
        self.x, self.y = position
        self.width, self.height = size
        # 이미지 크기와 독립적인 월드 단위 오프셋·크기. 지정된 건물·소품만 사용한다.
        self.collision = collision
        self.object_id = object_id
        self.is_building = is_building
        self.tree_sway = tree_sway
        self.ambience = None
        if object_id == 'delivery_depot':
            try:
                self.ambience = DepotAmbience(self, depot_layout)
            except OSError as error:
                print(f'[배달소 환경 효과] {error}')

    def get_collision_bounds(self):
        if self.collision is None:
            return None
        offset_x, offset_y = self.collision['offset']
        width, height = self.collision['size']
        center_x = self.x + offset_x
        center_y = self.y + offset_y
        return (center_x - width / 2, center_y - height / 2,
                center_x + width / 2, center_y + height / 2)

    def update(self):
        if self.ambience is not None:
            self.ambience.update()
        if self.tree_sway is not None:
            self.tree_sway.update()

    def draw(self):
        x, y = self.camera.world_to_screen(self.x, self.y)
        if self.tree_sway is not None:
            self.tree_sway.draw(self.camera, round(x), round(y), self.width, self.height)
        else:
            self.image.draw(round(x), round(y), self.width, self.height)
        if self.ambience is not None:
            self.ambience.draw()
        bounds = self.get_collision_bounds()
        if debug_view.enabled and bounds is not None:
            left, bottom, right, top = bounds
            screen_left, screen_bottom = self.camera.world_to_screen(left, bottom)
            screen_right, screen_top = self.camera.world_to_screen(right, top)
            draw_rectangle(round(screen_left), round(screen_bottom),
                           round(screen_right), round(screen_top), 0, 255, 255)


def create_decorations(camera, config, roads):
    decorations = []
    filenames = {
        'building': 'building_sample.png',
        'shop': 'building_shop.png',
        'blue_house': 'building_blue_house.png',
        'cafe': 'building_cafe.png',
        'apartment': 'building_apartment.png',
        'fountain': 'fountain.png',
        'delivery_depot': 'building_delivery_depot.png',
        'tree': 'tree.png',
        'tree_branches': 'tree_branches.png',
        'tree_foliage': 'tree_foliage.png',
        'bus_stop': 'bus_stop.png',
        'bench': 'bench.png',
        'recycling_bin': 'recycling_bin.png',
        'mailbox': 'mailbox.png',
        'planter': 'planter.png',
    }
    images = {}
    depot_layout = 'original'

    def add_decoration(item, asset, is_building=False):
        nonlocal depot_layout
        if asset not in images:
            if asset == 'delivery_depot':
                try:
                    images[asset] = load_image(str(
                        ROOT / 'assets/images/building_delivery_depot_pixel_v1.png'))
                    depot_layout = 'pixel'
                except OSError as error:
                    print(f'[배달소 이미지] 기존 이미지 사용: {error}')
                    images[asset] = load_image(str(ROOT / 'assets/images' / filenames[asset]))
            else:
                images[asset] = load_image(str(ROOT / 'assets/images' / filenames[asset]))
        image = images[asset]
        # 동일 원본을 쓰는 다른 주택은 유지하고 지정한 한 채만 교체한다.
        if is_building and item.get('id') == 'collision_preview_house':
            key = 'collision_preview_house_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/building_sample_pixel_v1.png'))
                except OSError as error:
                    print(f'[주택 이미지] 기존 이미지 사용: {error}')
                    images[key] = images[asset]
            image = images[key]
        if is_building and item.get('id') == 'delivery_candidate_cafe_450_150':
            key = 'start_cafe_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/building_cafe_pixel_v1.png'))
                except OSError as error:
                    print(f'[카페 이미지] 기존 이미지 사용: {error}')
                    images[key] = images[asset]
            image = images[key]
        if is_building and asset == 'blue_house' and tuple(item['position']) == (150, 150):
            key = 'start_blue_house_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/building_blue_house_pixel_v1.png'))
                except OSError as error:
                    print(f'[파란 주택 이미지] 기존 이미지 사용: {error}')
                    images[key] = images[asset]
            image = images[key]
        if asset == 'bench' and tuple(item['position']) == (630, 580):
            key = 'start_bench_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/bench_pixel_v1.png'))
                except OSError as error:
                    print(f'[벤치 이미지] 기존 이미지 사용: {error}')
                    images[key] = images[asset]
            image = images[key]
        if asset == 'recycling_bin' and tuple(item['position']) == (700, 580):
            key = 'start_recycling_bin_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/recycling_bin_pixel_v1.png'))
                except OSError as error:
                    print(f'[분리수거함 이미지] 기존 이미지 사용: {error}')
                    images[key] = images[asset]
            image = images[key]
        if asset == 'mailbox' and tuple(item['position']) == (620, 330):
            key = 'start_mailbox_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/mailbox_pixel_v1.png'))
                except OSError as error:
                    print(f'[우편함 이미지] 기존 이미지 사용: {error}')
                    images[key] = images[asset]
            image = images[key]
        if asset == 'planter' and tuple(item['position']) == (620, 280):
            key = 'start_planter_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/planter_pixel_v1.png'))
                except OSError as error:
                    print(f'[화분 이미지] 기존 이미지 사용: {error}')
                    images[key] = images[asset]
            image = images[key]
        tree_sway = None
        if asset == 'tree' and 'sway' in item:
            try:
                for layer in ('tree_branches', 'tree_foliage'):
                    if layer not in images:
                        images[layer] = load_image(str(ROOT / 'assets/images' / filenames[layer]))
                tree_sway = TreeSway(images['tree_branches'], images['tree_foliage'], item['sway'])
            except OSError as error:
                print(f'[나무 흔들림] 기존 이미지 사용: {error}')
        decorations.append(MapDecoration(camera, image, item['position'], item['size'],
                                         collision=item.get('collision'), object_id=item.get('id'),
                                         is_building=is_building, tree_sway=tree_sway,
                                         depot_layout=depot_layout))

    for item in config['buildings']:
        add_decoration(item, item.get('asset', 'building'), is_building=True)
    for item in config.get('props', []):
        add_decoration(item, item['asset'])
    # 북·동·남·서가 모두 연결된 타일의 네 모서리에만 배치한다.
    intersections = [(x, y) for (x, y), mask in roads.items() if mask == 15]
    tile = config['tile_size']
    geometry = RoadGeometry(tile)
    for x, y in intersections:
        center = ((x + 0.5) * tile, (y + 0.5) * tile)
        for direction in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            decorations.append(TrafficSignal(
                camera, center, direction, geometry.road_width, geometry.sidewalk_width))
    return decorations
