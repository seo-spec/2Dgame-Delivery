"""배달소 출입구 조명과 지붕 환기구의 작은 수증기 효과."""

import ctypes
from importlib import import_module
from math import cos, isfinite, pi, sin

from game.core import game_framework


_pico = import_module('pico2d.pico2d')


def _soft_image(color, lobed=False):
    """초기화 시에만 작은 RGBA 텍스처를 만든다. 외곽 알파는 0이다."""
    size = 48
    pixels = bytearray(size * size * 4)
    for row in range(size):
        for col in range(size):
            x = (col + 0.5 - size / 2) / (size / 2)
            y = (row + 0.5 - size / 2) / (size / 2)
            distance = x * x + y * y
            strength = max(0.0, 1.0 - distance)
            if lobed:
                strength *= 0.85 + 0.15 * sin(x * 9) * cos(y * 7)
            offset = (row * size + col) * 4
            pixels[offset:offset + 4] = bytes((*color, round(255 * strength ** 2)))
    texture = _pico.SDL_CreateTexture(
        _pico.renderer, _pico.SDL_PIXELFORMAT_ABGR8888,
        _pico.SDL_TEXTUREACCESS_STATIC, size, size)
    if not texture:
        raise OSError('배달소 환경 효과 텍스처를 만들지 못했습니다.')
    buffer = ctypes.create_string_buffer(bytes(pixels))
    updated = _pico.SDL_UpdateTexture(texture, None, buffer, size * 4)
    blended = _pico.SDL_SetTextureBlendMode(texture, _pico.SDL_BLENDMODE_BLEND)
    if updated != 0 or blended != 0:
        _pico.SDL_DestroyTexture(texture)
        raise OSError('배달소 환경 효과 텍스처를 준비하지 못했습니다.')
    return _pico.Image(texture)


class DepotAmbience:
    def __init__(self, decoration, layout='original'):
        self.camera = decoration.camera
        self.x, self.y = decoration.x, decoration.y
        self.width, self.height = decoration.width, decoration.height
        self.elapsed = 0.0
        # 이미지 전체(투명 여백 포함)의 중심 기준 비율. 원본 폴백도 원래 부착점을 쓴다.
        if layout == 'pixel':
            self.light_offset = (0.0, 0.375)
            self.light_size = (0.21, 0.055)
            self.vent_offset = (0.296, 0.166)
        else:
            self.light_offset = (0.0, 0.32)
            self.light_size = (0.22, 0.065)
            self.vent_offset = (0.282, 0.151)
        self.light = _soft_image((255, 216, 143))
        self.steam = _soft_image((207, 214, 209), lobed=True)

    def update(self):
        dt = game_framework.frame_time
        if isfinite(dt) and dt > 0:
            # 조명 6초, 수증기 4초 주기가 모두 연결되는 시점에서만 시간을 접는다.
            self.elapsed = (self.elapsed + dt) % 12.0

    def draw(self):
        x, y = self.camera.world_to_screen(self.x, self.y)
        camera = self.camera
        # 효과는 건물 이미지 안에 머무른다. 화면 밖에서는 텍스처 출력도 생략한다.
        if (x + self.width / 2 <= camera.viewport_left
                or x - self.width / 2 >= camera.viewport_left + camera.viewport_width
                or y + self.height / 2 <= camera.viewport_bottom
                or y - self.height / 2 >= camera.viewport_bottom + camera.viewport_height):
            return
        self.light.opacify(0.13 + 0.06 * sin(self.elapsed * 2 * pi / 6))
        self.light.draw(x + self.width * self.light_offset[0],
                        y + self.height * self.light_offset[1],
                        self.width * self.light_size[0], self.height * self.light_size[1])
        # 기존 이미지의 우측 지붕 환기구 중심. 고정된 세 입자로 생성/폐기 없이 반복한다.
        for phase in (0.0, 1 / 3, 2 / 3):
            progress = (self.elapsed / 4 + phase) % 1.0
            opacity = 0.16 * sin(pi * progress) ** 2
            self.steam.opacify(opacity)
            drift = self.width * (-0.045 * progress + 0.008 * sin(2 * pi * progress))
            rise = self.height * 0.07 * progress
            size = self.width * (0.035 + 0.055 * progress)
            self.steam.draw(x + self.width * self.vent_offset[0] + drift,
                            y + self.height * self.vent_offset[1] + rise, size, size * 0.65)
