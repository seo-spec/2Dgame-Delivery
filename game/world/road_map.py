"""공통 규격의 도로와 이미지 장식으로 구성한 샘플 맵."""

import json
from time import perf_counter
from importlib import import_module
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
from game.world.start_scene_art import get_asset_spec, load_compact_image


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
        self.road_finish_extensions = []
        self.entrance_finishes = []
        finish_config = self.config.get('road_finish')
        if finish_config:
            finish_started = perf_counter()
            regions = [finish_config['bounds'], *finish_config.get('extensions', [])]
            # 적용 구역들은 빈틈없는 직사각형을 이룬다. 내부 경계는 페이드하지 않는다.
            fade_bounds = [min(bounds[0] for bounds in regions),
                           min(bounds[1] for bounds in regions),
                           max(bounds[2] for bounds in regions),
                           max(bounds[3] for bounds in regions)]
            for index, bounds in enumerate(regions):
                try:
                    finish = RoadFinish(self, {**finish_config, 'bounds': bounds,
                                              'fade_bounds': fade_bounds})
                    if index == 0:
                        self.road_finish = finish
                    else:
                        self.road_finish_extensions.append(finish)
                except OSError as error:
                    print(f'[도로 표현 {index}] {error}')
            for path in finish_config.get('entry_paths', []):
                if not path.get('standalone', False):
                    continue
                try:
                    self.entrance_finishes.append(RoadFinish(self, {
                        'bounds': path['bounds'], 'entrance_only': True,
                        'entry_paths': [path],
                    }))
                except OSError as error:
                    print(f'[주택 진입부] {error}')
            finishes = ([self.road_finish] if self.road_finish is not None else [])
            finishes += self.road_finish_extensions + self.entrance_finishes
            hits = sum(finish.cache_hit for finish in finishes)
            print(f'[지면 준비] 캐시 {hits}/{len(finishes)}, '
                  f'재생성 {len(finishes) - hits}, {perf_counter() - finish_started:.2f}초')

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
        for finish in self.road_finish_extensions:
            finish.draw()
        for entrance in self.entrance_finishes:
            entrance.draw()

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
                 is_building=False, tree_sway=None, depot_layout='original',
                 cull_when_offscreen=False):
        self.camera = camera
        self.image = image
        self.x, self.y = position
        self.width, self.height = size
        # 이미지 크기와 독립적인 월드 단위 오프셋·크기. 지정된 건물·소품만 사용한다.
        self.collision = collision
        self.object_id = object_id
        self.is_building = is_building
        self.cull_when_offscreen = cull_when_offscreen
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
        if self.tree_sway is None and (not self.is_building or self.object_id in (
                'collision_preview_house', 'delivery_house_b', 'delivery_house_c',
                'delivery_house_d', 'delivery_house_e') or self.cull_when_offscreen):
            camera = self.camera
            if (x + self.width / 2 <= camera.viewport_left
                    or x - self.width / 2 >= camera.viewport_left + camera.viewport_width
                    or y + self.height / 2 <= camera.viewport_bottom
                    or y - self.height / 2 >= camera.viewport_bottom + camera.viewport_height):
                return
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
    prop_files = {
        'tree': 'tree_title_pixel_v1.png',
        'bus_stop': 'bus_stop_pixel_v1.png',
        'fountain': 'fountain_pixel_v1.png',
        'bench': 'bench_pixel_v1.png',
        'recycling_bin': 'recycling_bin_pixel_v1.png',
        'mailbox': 'mailbox_pixel_v1.png',
        'planter': 'planter_pixel_v1.png',
    }
    pixel_props = set()
    common_buildings = {
        'building': 'building_sample_pixel_v1.png',
        'blue_house': 'building_blue_house_pixel_v1.png',
        'shop': 'building_shop_pixel_v1.png',
        'cafe': 'building_cafe_pixel_v1.png',
        'apartment': 'building_apartment_pixel_v1.png',
    }
    depot_layout = 'original'

    def add_decoration(item, asset, is_building=False):
        nonlocal depot_layout
        start_spec = get_asset_spec(asset, item.get('id'))
        start_image = None
        if start_spec:
            key = ('title_v2', *start_spec)
            if key not in images:
                try:
                    images[key] = load_compact_image(*start_spec)
                except OSError as error:
                    print(f'[환경 {start_spec[0]}] v1 사용: {error}')
                    images[key] = None
            start_image = images[key]
            if start_image is not None and asset == 'delivery_depot':
                depot_layout = 'title_v2'
        if start_image is None and asset not in images:
            if not is_building and asset in prop_files:
                try:
                    images[asset] = load_image(str(ROOT / 'assets/images' / prop_files[asset]))
                    import_module('pico2d.pico2d').SDL_SetTextureScaleMode(images[asset].texture, 0)
                    pixel_props.add(asset)
                except OSError as error:
                    print(f'[도시 소품 {asset}] 원본 사용: {error}')
                    images[asset] = load_image(str(ROOT / 'assets/images' / filenames[asset]))
            elif is_building and asset in common_buildings:
                try:
                    images[asset] = load_image(str(ROOT / 'assets/images' / common_buildings[asset]))
                    import_module('pico2d.pico2d').SDL_SetTextureScaleMode(images[asset].texture, 0)
                except OSError as error:
                    print(f'[공통 건물 {asset}] 원본 사용: {error}')
                    images[asset] = load_image(str(ROOT / 'assets/images' / filenames[asset]))
            elif asset == 'delivery_depot':
                try:
                    images[asset] = load_image(str(
                        ROOT / 'assets/images/building_delivery_depot_pixel_v1.png'))
                    depot_layout = 'pixel'
                except OSError as error:
                    print(f'[배달소 이미지] 기존 이미지 사용: {error}')
                    images[asset] = load_image(str(ROOT / 'assets/images' / filenames[asset]))
            else:
                images[asset] = load_image(str(ROOT / 'assets/images' / filenames[asset]))
        image = start_image if start_image is not None else images[asset]
        # 배송 건물 세 곳만 교체하고, 두 상점은 하나의 이미지/폴백 캐시를 공유한다.
        entrance_assets = {
            'delivery_house_c': 'building_blue_house_entrance_pixel_v1.png',
            'delivery_house_d': 'building_shop_entrance_pixel_v1.png',
            'delivery_house_e': 'building_shop_entrance_pixel_v1.png',
        }
        entrance_file = entrance_assets.get(item.get('id')) if is_building else None
        if start_image is None and entrance_file:
            if entrance_file not in images:
                try:
                    images[entrance_file] = load_image(str(ROOT / 'assets/images' / entrance_file))
                except OSError as error:
                    print(f'[배송 건물 이미지] 원본 사용: {error}')
                    images[entrance_file] = images[asset]
            image = images[entrance_file]
        if (start_image is None and is_building
                and item.get('id') in ('collision_preview_house', 'delivery_house_b')):
            key = 'north_house_entrance_pixel'
            if key not in images:
                try:
                    images[key] = load_image(str(ROOT / 'assets/images/building_sample_entrance_pixel_v1.png'))
                except OSError as error:
                    print(f'[주택 입구 이미지] 기존 도트 주택 사용: {error}')
                    images[key] = image
            image = images[key]
        tree_sway = None
        if asset == 'tree' and 'sway' in item:
            try:
                if start_image is not None or 'tree' in pixel_props:
                    # 새 나무는 줄기가 드러나지 않는 수관 자산이다. 기존 잎과 중복하지 않는다.
                    tree_sway = TreeSway(None, image, item['sway'])
                else:
                    for layer in ('tree_branches', 'tree_foliage'):
                        if layer not in images:
                            images[layer] = load_image(str(ROOT / 'assets/images' / filenames[layer]))
                    tree_sway = TreeSway(images['tree_branches'], images['tree_foliage'], item['sway'])
            except OSError as error:
                print(f'[나무 흔들림] 기존 이미지 사용: {error}')
        decorations.append(MapDecoration(camera, image, item['position'], item['size'],
                                         collision=item.get('collision'), object_id=item.get('id'),
                                         is_building=is_building, tree_sway=tree_sway,
                                         depot_layout=depot_layout,
                                         cull_when_offscreen=(start_image is not None
                                                              or is_building and asset in common_buildings)))

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
