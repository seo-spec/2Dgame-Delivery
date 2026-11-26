"""출발지 블록의 잔디·도로·포장을 초기화 시 합성하는 정적 도트 재질."""

import ctypes
from importlib import import_module
from math import sin

from game.world.road_geometry import GRASS_COLOR, MARKING_COLOR, SIDEWALK_COLOR


_pico = import_module('pico2d.pico2d')
ASPHALT_TINT = (65, 72, 75)
# 개선 구역만 밝은 사각형으로 보이지 않도록 기존 월드 잔디와 같은 색 계열을 쓴다.
GRASS_TINT = tuple(channel + offset for channel, offset in zip(GRASS_COLOR, (6, 5, 1)))
PAINT_TINT = (211, 207, 190)


class RoadFinish:
    def __init__(self, road_map, config):
        self.camera = road_map.camera
        self.left, self.bottom, right, top = config['bounds']
        self.width = right - self.left
        self.height = top - self.bottom
        self.image = None
        mask = self._road_mask(road_map.road_surface.rectangles)
        quiet = self._quiet_mask(road_map)
        pixels = self._material_pixels(mask, quiet, config['fade_width'])
        self._paint_paving(pixels, mask, quiet, road_map, config)
        self._paint_markings(pixels, mask, quiet, road_map)
        self.image = self._upload(pixels)

    def _road_mask(self, rectangles):
        """반열린 월드 사각형을 표시용 마스크로 변환한다. 판정 데이터는 수정하지 않는다."""
        mask = bytearray(self.width * self.height)
        for left, bottom, right, top in rectangles:
            x1 = max(0, round(left - self.left))
            x2 = min(self.width, round(right - self.left))
            y1 = max(0, round(bottom - self.bottom))
            y2 = min(self.height, round(top - self.bottom))
            if x1 >= x2 or y1 >= y2:
                continue
            stripe = b'\x01' * (x2 - x1)
            for y in range(y1, y2):
                start = (self.height - 1 - y) * self.width + x1
                mask[start:start + len(stripe)] = stripe
        return mask

    @staticmethod
    def _fade_alpha(position, extent, fade_width):
        ratio = min(1.0, (position + 0.5) / fade_width,
                    (extent - position - 0.5) / fade_width)
        return round(255 * ratio * ratio * (3 - 2 * ratio))

    def _quiet_mask(self, road_map):
        """출발 위치와 실제 상호작용 구역 주변의 표시용 여백."""
        spawn_x, spawn_y = road_map.spawn
        rectangles = [(spawn_x - 70, spawn_y - 70, spawn_x + 70, spawn_y + 70)]
        for building in road_map.config['buildings']:
            for key in ('pickup_zone', 'delivery_zone'):
                zone = building.get(key)
                if zone is None:
                    continue
                x = building['position'][0] + zone['offset'][0]
                y = building['position'][1] + zone['offset'][1]
                half_w, half_h = zone['size'][0] / 2 + 12, zone['size'][1] / 2 + 12
                rectangles.append((x - half_w, y - half_h, x + half_w, y + half_h))
        return self._road_mask(rectangles)

    @staticmethod
    def _grass_color(wx, wy, quiet):
        # 모든 무늬를 월드 2px 격자에 고정한다. 전역 게임 난수는 사용하지 않는다.
        gx, gy = wx // 2, wy // 2
        patch = ((gx // 48 * 37) ^ (gy // 40 * 61)) & 3
        shade = (-4, -2, 0, 2)[patch]
        cell_x, local_x = divmod(gx, 24)
        cell_y, local_y = divmod(gy, 24)
        seed = (cell_x * 73856093) ^ (cell_y * 19349663)
        # 48px 구획 중 일부에만 2~6px 크기의 작은 풀잎을 둔다.
        tuft_x, tuft_y = 4 + (seed >> 5 & 15), 4 + (seed >> 10 & 15)
        if not quiet and seed % 7 == 0:
            dx, dy = local_x - tuft_x, local_y - tuft_y
            if (dx, dy) in ((0, 0), (0, 1), (-1, 1), (1, 2)):
                shade -= 9
            elif (dx, dy) in ((-1, 2), (1, 3)):
                shade += 5
        return tuple(channel + shade for channel in GRASS_TINT)

    def _material_pixels(self, mask, quiet, fade_width):
        pixels = bytearray(self.width * self.height * 4)
        red, green, blue = ASPHALT_TINT
        fade_x = [self._fade_alpha(x, self.width, fade_width) for x in range(self.width)]
        fade_y = [self._fade_alpha(y, self.height, fade_width) for y in range(self.height)]
        shade_x = [round(sin(((self.left + x) // 2 * 2) / 83.0)) * 2
                   for x in range(self.width)]
        for row in range(self.height):
            world_y = self.bottom + self.height - 1 - row
            shade_y = round(sin((world_y // 2 * 2) / 113.0)) * 2
            for x in range(self.width):
                index = row * self.width + x
                alpha = min(fade_x[x // 2 * 2], fade_y[row // 2 * 2])
                if not mask[index]:
                    color = self._grass_color(self.left + x, world_y, quiet[index])
                    pixels[index * 4:index * 4 + 4] = bytes((*color, alpha))
                    continue
                # 월드 좌표로 결정한 입자라 게임 난수와 타일 경계에 영향을 받지 않는다.
                grain = (((self.left + x) // 2) * 73856093) ^ ((world_y // 2) * 19349663)
                grain ^= grain >> 13
                shade = (grain & 3) - 1 + shade_x[x] + shade_y
                if quiet[index]:
                    shade //= 3
                if 2 <= x < self.width - 2 and 2 <= row < self.height - 2:
                    if not (mask[index - 2] and mask[index + 2]
                            and mask[index - self.width * 2] and mask[index + self.width * 2]):
                        shade -= 3
                pixels[index * 4:index * 4 + 4] = bytes(
                    (red + shade, green + shade, blue + shade, alpha))
        return pixels

    def _paint_paving(self, pixels, road_mask, quiet, road_map, config):
        size = road_map.tile_size
        rectangles = [
            (tx * size + left, ty * size + bottom,
             tx * size + right + 1, ty * size + top + 1)
            for tx, ty, connection in road_map.tiles
            for left, bottom, right, top, color in road_map.geometry.tiles[connection]
            if color == SIDEWALK_COLOR
        ]
        for path in road_map.config.get('access_paths', []):
            left, bottom, right, top = path['bounds']
            rectangles.append((left, bottom, right, top + 1))
        sidewalk = self._road_mask(rectangles)
        forecourt = config.get('forecourt')
        yard = self._road_mask([forecourt['bounds']]) if forecourt else bytearray(len(sidewalk))
        fade_x = [self._fade_alpha(x, self.width, config['fade_width'])
                  for x in range(self.width)]
        fade_y = [self._fade_alpha(y, self.height, config['fade_width'])
                  for y in range(self.height)]
        for row in range(self.height):
            wy = self.bottom + self.height - 1 - row
            for x in range(self.width):
                index = row * self.width + x
                if road_mask[index] or not (sidewalk[index] or yard[index]):
                    continue
                wx = self.left + x
                is_walk = bool(sidewalk[index])
                # 월드 좌표에 고정해 타일 경계와 카메라 이동에서 무늬를 이어 준다.
                block_w, block_h = (24, 12) if is_walk else (32, 24)
                block_row, local_y = divmod(wy, block_h)
                block_col, local_x = divmod(wx + (block_row % 2) * (block_w // 2), block_w)
                variation = ((block_col * 37 ^ block_row * 61) & 7) - 3
                grain = (((wx // 2) * 17 ^ (wy // 2) * 31) & 3) - 1
                shade = variation + grain
                if local_x < 2 or local_y < 2:
                    shade -= 10 if is_walk else 7
                elif local_x < 4 or local_y < 4:
                    shade += 2
                if quiet[index]:
                    shade //= 3
                tint = (200, 189, 164) if is_walk else (166, 166, 151)
                alpha = min(fade_x[x // 2 * 2], fade_y[row // 2 * 2])
                if is_walk:
                    # 차도 쪽 2px 면은 연석으로 표현한다. 모서리에서도 같은 마스크를 쓴다.
                    neighbors = (
                        (x >= 2, index - 2, 9),
                        (x < self.width - 2, index + 2, -14),
                        (row >= 2, index - self.width * 2, -14),
                        (row < self.height - 2, index + self.width * 2, 9),
                    )
                    curb = [tone for valid, adjacent, tone in neighbors
                            if valid and road_mask[adjacent]]
                    if curb:
                        shade = sum(curb) // len(curb) + grain
                    else:
                        # 잔디와 맞닿는 바깥 2px은 낮은 대비의 이음부로 정리한다.
                        for valid, adjacent, _ in neighbors:
                            if valid and not sidewalk[adjacent] and not yard[adjacent]:
                                shade -= 5
                                break
                else:
                    left, bottom, right, top = forecourt['bounds']
                    edge = min(wx - left + 0.5, right - wx - 0.5,
                               wy - bottom + 0.5, top - wy - 0.5)
                    # 작업 마당의 외곽만 잔디로 짧게 섞고 보도와 차도는 우선 유지한다.
                    ratio = min(1.0, max(0.0, edge / forecourt['edge_fade']))
                    blend = ratio * ratio * (3 - 2 * ratio)
                    grass = self._grass_color(wx, wy, quiet[index])
                    # 외곽은 새 잔디와 먼저 섞은 뒤 구역 전체의 페이드를 적용한다.
                    color = tuple(round(base * (1 - blend) + (channel + shade) * blend)
                                  for base, channel in zip(grass, tint))
                    pixels[index * 4:index * 4 + 4] = bytes((*color, alpha))
                    continue
                pixels[index * 4:index * 4 + 4] = bytes(
                    (*[channel + shade for channel in tint], alpha))

    def _paint_markings(self, pixels, mask, quiet, road_map):
        for tile_x, tile_y, connection in road_map.tiles:
            for x1, y1, x2, y2, color in road_map.geometry.tiles[connection]:
                if color != MARKING_COLOR:
                    continue
                # 두꺼운 정지선·횡단보도는 중심을 유지하며 양쪽을 각각 1px 줄인다.
                width, height = x2 - x1 + 1, y2 - y1 + 1
                if min(width, height) >= 5:
                    if width <= height:
                        x1, x2 = x1 + 1, x2 - 1
                    else:
                        y1, y2 = y1 + 1, y2 - 1
                left = max(0, round(tile_x * road_map.tile_size + x1 - self.left))
                right = min(self.width, round(tile_x * road_map.tile_size + x2 + 1 - self.left))
                bottom = max(0, round(tile_y * road_map.tile_size + y1 - self.bottom))
                top = min(self.height, round(tile_y * road_map.tile_size + y2 + 1 - self.bottom))
                for y in range(bottom, top):
                    row = self.height - 1 - y
                    for x in range(left, right):
                        index = row * self.width + x
                        if mask[index]:
                            wear = 0 if quiet[index] else ((x // 2 * 17 + y // 2 * 31) & 3) - 1
                            pixels[index * 4:index * 4 + 3] = bytes(
                                channel + wear for channel in PAINT_TINT)

    def _upload(self, pixels):
        renderer = getattr(_pico, 'renderer', None)
        if not renderer:
            raise OSError('도로 재질을 준비할 렌더러가 없습니다.')
        texture = _pico.SDL_CreateTexture(
            renderer, _pico.SDL_PIXELFORMAT_ABGR8888,
            _pico.SDL_TEXTUREACCESS_STATIC, self.width, self.height,
        )
        if not texture:
            raise OSError('도로 재질 텍스처를 만들지 못했습니다.')
        buffer = ctypes.create_string_buffer(bytes(pixels))
        updated = _pico.SDL_UpdateTexture(texture, None, buffer, self.width * 4)
        blended = _pico.SDL_SetTextureBlendMode(texture, _pico.SDL_BLENDMODE_BLEND)
        if updated != 0 or blended != 0:
            _pico.SDL_DestroyTexture(texture)
            raise OSError('도로 재질 텍스처를 준비하지 못했습니다.')
        _pico.SDL_SetTextureScaleMode(texture, 0)
        return _pico.Image(texture)

    def draw(self):
        left, bottom = self.camera.world_to_screen(self.left, self.bottom)
        camera = self.camera
        if (left + self.width <= camera.viewport_left
                or left >= camera.viewport_left + camera.viewport_width
                or bottom + self.height <= camera.viewport_bottom
                or bottom >= camera.viewport_bottom + camera.viewport_height):
            return
        self.image.draw(round(left) + self.width / 2, round(bottom) + self.height / 2,
                        self.width, self.height)
