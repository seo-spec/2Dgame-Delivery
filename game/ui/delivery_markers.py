"""투명 PNG로 표시하는 적재·배송·복귀 바닥 마커. 오토바이 아래에 그린다."""

from pico2d import load_image, SDL_SetTextureAlphaMod

from game.config.delivery_markers import MARKER_DIRECTORY, MARKER_SPRITES
from game.systems.delivery import select_delivery_target
from game.systems.stage import StageState


class ZoneMarkers:
    def __init__(self, camera, motorcycle, controller, delivery_houses, pickup_bounds):
        self.camera = camera
        self.motorcycle = motorcycle
        self.controller = controller
        self.delivery_houses = delivery_houses
        self.pickup_bounds = pickup_bounds
        # 네 장을 한 번만 로드하고 모든 배송지와 상태가 공유한다.
        self.images = {kind: load_image(str(MARKER_DIRECTORY / filename))
                       for kind, (filename, _) in MARKER_SPRITES.items()}

    def update(self):
        pass

    def _draw_marker(self, bounds, kind, active=False):
        left, bottom, right, top = bounds
        camera = self.camera
        sx, sy = camera.world_to_screen(left, bottom)
        ex, ey = camera.world_to_screen(right, top)
        if (ex < camera.viewport_left or sx > camera.viewport_left + camera.viewport_width
                or ey < camera.viewport_bottom or sy > camera.viewport_bottom + camera.viewport_height):
            return
        image = self.images[kind]
        alpha = 145 if kind == 'complete' else 255 if active else 215
        SDL_SetTextureAlphaMod(image.texture, alpha)
        clip = MARKER_SPRITES[kind][1]
        # 세로로 긴 배송 구역에서도 원형 아이콘과 모서리가 눌리지 않게 비율을 유지한다.
        scale = min((right - left) / clip[2], (top - bottom) / clip[3])
        image.clip_draw(*clip, (sx + ex) / 2, (sy + ey) / 2,
                        clip[2] * scale, clip[3] * scale)

    def draw(self):
        state = self.controller.state
        if state == StageState.WAITING:
            left, bottom, right, top = self.pickup_bounds
            active = left <= self.motorcycle.x <= right and bottom <= self.motorcycle.y <= top
            self._draw_marker(self.pickup_bounds, 'pickup', active)
        elif state == StageState.RETURNING:
            self._draw_marker(self.pickup_bounds, 'return', True)
        target = (select_delivery_target(self.delivery_houses, self.motorcycle.cargo_list,
                                        self.motorcycle.x, self.motorcycle.y)
                  if self.controller.can_deliver() else None)
        for house in self.delivery_houses:
            bounds = house.get_zone_bounds()
            if bounds is not None:
                self._draw_marker(bounds, 'complete' if house.delivered else 'delivery', house is target)
