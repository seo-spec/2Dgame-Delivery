"""기존 도로 형상 안에만 합성하는 출발지 블록의 정적 아스팔트 재질."""

import ctypes
from importlib import import_module
from math import sin

from game.world.road_geometry import MARKING_COLOR


_pico = import_module('pico2d.pico2d')
ASPHALT_TINT = (58, 65, 69)
PAINT_TINT = (211, 207, 190)


class RoadFinish:
    def __init__(self, road_map, config):
        self.camera = road_map.camera
        self.left, self.bottom, right, top = config['bounds']
        self.width = right - self.left
        self.height = top - self.bottom
        self.image = None
        mask = self._road_mask(road_map.road_surface.rectangles)
        pixels = self._material_pixels(mask, config['fade_width'])
        self._paint_markings(pixels, mask, road_map)
        self.image = self._upload(pixels)

    def _road_mask(self, rectangles):
        """그리기·판정에 쓰는 기존 반열린 사각형에서 도로만 추출한다."""
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

    def _material_pixels(self, mask, fade_width):
        pixels = bytearray(self.width * self.height * 4)
        red, green, blue = ASPHALT_TINT
        fade_x = [self._fade_alpha(x, self.width, fade_width) for x in range(self.width)]
        fade_y = [self._fade_alpha(y, self.height, fade_width) for y in range(self.height)]
        shade_x = [round(1.6 * sin((self.left + x) / 83.0)) for x in range(self.width)]
        for row in range(self.height):
            world_y = self.bottom + self.height - 1 - row
            shade_y = round(1.2 * sin(world_y / 113.0))
            for x in range(self.width):
                index = row * self.width + x
                if not mask[index]:
                    continue
                # 월드 좌표로 결정한 입자라 게임 난수와 타일 경계에 영향을 받지 않는다.
                grain = ((self.left + x) * 73856093) ^ (world_y * 19349663)
                grain ^= grain >> 13
                shade = (grain & 7) - 3 + shade_x[x] + shade_y
                if 2 <= x < self.width - 2 and 2 <= row < self.height - 2:
                    if not (mask[index - 2] and mask[index + 2]
                            and mask[index - self.width * 2] and mask[index + self.width * 2]):
                        shade -= 3
                alpha = min(fade_x[x], fade_y[row])
                pixels[index * 4:index * 4 + 4] = bytes(
                    (red + shade, green + shade, blue + shade, alpha))
        return pixels

    def _paint_markings(self, pixels, mask, road_map):
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
                            wear = ((x * 17 + y * 31) & 3) - 1
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
