"""실제 구역에 맞춘 짧은 바닥선과 독립된 작은 도트 기호."""

import ctypes
from importlib import import_module

from game.systems.delivery import select_delivery_target
from game.systems.stage import StageState


_pico = import_module('pico2d.pico2d')
ICON_SIZE = 24
NORMAL = (187, 178, 145)
ACTIVE = (244, 205, 112)
COMPLETE = (139, 175, 151)
# 초기화 시 텍스처로 준비할 단순 UI 기호: 수령 화살표, 배송 핀, 복귀 집, 완료 체크.
GLYPHS = {
    'pickup': ('............', '.....##.....', '.....##.....', '.....##.....',
               '...######...', '....####....', '.....##.....', '............',
               '..##....##..', '..##....##..', '..########..', '............'),
    'delivery': ('............', '....####....', '...######...', '..###..###..',
                 '..###..###..', '..########..', '...######...', '....####....',
                 '.....##.....', '.....##.....', '............', '............'),
    'return': ('............', '.....##.....', '....####....', '...######...',
               '..########..', '.###....###.', '..##....##..', '..##.##.##..',
               '..##.##.##..', '..########..', '............', '............'),
    'complete': ('............', '............', '.........##.', '........###.',
                 '.......###..', '..##..###...', '..######....', '...####.....',
                 '....##......', '............', '............', '............'),
}


def _image(width, height, rectangles):
    pixels = bytearray(width * height * 4)
    for left, bottom, right, top in rectangles:
        stripe = b'\xff\xff\xff\xff' * (right - left)
        for y in range(bottom, top):
            offset = ((height - 1 - y) * width + left) * 4
            pixels[offset:offset + len(stripe)] = stripe
    texture = _pico.SDL_CreateTexture(
        _pico.renderer, _pico.SDL_PIXELFORMAT_ABGR8888,
        _pico.SDL_TEXTUREACCESS_STATIC, width, height)
    if not texture:
        raise OSError('배송 위치 텍스처를 만들지 못했습니다.')
    buffer = ctypes.create_string_buffer(bytes(pixels))
    updated = _pico.SDL_UpdateTexture(texture, None, buffer, width * 4)
    blended = _pico.SDL_SetTextureBlendMode(texture, _pico.SDL_BLENDMODE_BLEND)
    if updated != 0 or blended != 0:
        _pico.SDL_DestroyTexture(texture)
        raise OSError('배송 위치 텍스처를 준비하지 못했습니다.')
    _pico.SDL_SetTextureScaleMode(texture, 0)
    return _pico.Image(texture)


class ZoneMarkers:
    def __init__(self, camera, motorcycle, controller, delivery_houses, pickup_bounds):
        self.camera = camera
        self.motorcycle = motorcycle
        self.controller = controller
        self.delivery_houses = delivery_houses
        self.pickup_bounds = pickup_bounds
        self.icons = {
            kind: _image(12, 12, [(x, 11 - row, x + 1, 12 - row)
                                 for row, line in enumerate(lines)
                                 for x, pixel in enumerate(line) if pixel == '#'])
            for kind, lines in GLYPHS.items()
        }
        self.frames = {}
        self.positions = {}
        left, bottom, right, _ = pickup_bounds
        # 배달소의 수령 구역은 건물 북쪽에 연결되어 있다.
        self._prepare(pickup_bounds, ((left + right) / 2, bottom - 1))
        for house in delivery_houses:
            bounds = house.get_zone_bounds()
            if bounds is not None:
                self._prepare(bounds, (house.x, house.y))

    def _prepare(self, bounds, building):
        left, bottom, right, top = bounds
        width, height = round(right - left), round(top - bottom)
        key = (width, height)
        if key not in self.frames:
            length = min(10, width // 4, height // 4)
            rectangles = []
            for x in (0, width - length):
                rectangles.extend(((x, 0, x + length, 2),
                                   (x, height - 2, x + length, height)))
            for y in (0, height - length):
                rectangles.extend(((0, y, 2, y + length),
                                   (width - 2, y, width, y + length)))
            self.frames[key] = _image(width, height, rectangles)
        inset = ICON_SIZE / 2 + 4
        candidates = [(x, y) for x in (left + inset, right - inset)
                      for y in (bottom + inset, top - inset)]
        # 입구 중심은 비우고 건물에서 먼 구역 안쪽 모서리를 우선한다.
        self.positions[tuple(bounds)] = tuple(sorted(
            candidates, key=lambda point: (point[0] - building[0]) ** 2
            + (point[1] - building[1]) ** 2, reverse=True))

    def update(self):
        pass

    @staticmethod
    def _tint(image, color, alpha):
        _pico.SDL_SetTextureColorMod(image.texture, *color)
        _pico.SDL_SetTextureAlphaMod(image.texture, alpha)

    def _draw_marker(self, bounds, kind, active=False):
        left, bottom, right, top = bounds
        camera = self.camera
        sx, sy = camera.world_to_screen(left, bottom)
        ex, ey = camera.world_to_screen(right, top)
        if (ex <= camera.viewport_left or sx >= camera.viewport_left + camera.viewport_width
                or ey <= camera.viewport_bottom or sy >= camera.viewport_bottom + camera.viewport_height):
            return
        color = COMPLETE if kind == 'complete' else ACTIVE if active else NORMAL
        alpha = 95 if kind == 'complete' else 240 if active else 145
        frame = self.frames[(round(right - left), round(top - bottom))]
        self._tint(frame, color, alpha)
        frame.draw((sx + ex) / 2, (sy + ey) / 2, right - left, top - bottom)
        icon = self.icons[kind]
        self._tint(icon, color, alpha)
        for x, y in self.positions[tuple(bounds)]:
            # 차체에 가려지는 기호는 다른 모서리로 옮긴다.
            clearance = self.motorcycle.collision_radius + ICON_SIZE / 2 + 4
            if ((x - self.motorcycle.x) ** 2 + (y - self.motorcycle.y) ** 2
                    < clearance ** 2):
                continue
            ix, iy = camera.world_to_screen(x, y)
            if (ix - ICON_SIZE / 2 < camera.viewport_left
                    or ix + ICON_SIZE / 2 > camera.viewport_left + camera.viewport_width
                    or iy - ICON_SIZE / 2 < camera.viewport_bottom
                    or iy + ICON_SIZE / 2 > camera.viewport_bottom + camera.viewport_height):
                continue
            icon.draw(round(ix), round(iy), ICON_SIZE, ICON_SIZE)
            break

    def draw(self):
        state = self.controller.state
        left, bottom, right, top = self.pickup_bounds
        inside = left <= self.motorcycle.x <= right and bottom <= self.motorcycle.y <= top
        if state == StageState.WAITING:
            self._draw_marker(self.pickup_bounds, 'pickup', inside)
        elif state == StageState.RETURNING:
            self._draw_marker(self.pickup_bounds, 'return', inside)
        target = (select_delivery_target(self.delivery_houses, self.motorcycle.cargo_list,
                                        self.motorcycle.x, self.motorcycle.y)
                  if self.controller.can_deliver() else None)
        for house in self.delivery_houses:
            bounds = house.get_zone_bounds()
            if bounds is not None:
                self._draw_marker(bounds, 'complete' if house.delivered else 'delivery', house is target)
