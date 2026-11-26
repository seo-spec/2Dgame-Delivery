"""선정한 나무의 고정 가지 위에서 잎만 천천히 흔든다."""

from math import isfinite, pi, sin

from game.core import game_framework


class TreeSway:
    def __init__(self, branches, foliage, config):
        self.branches = branches
        self.foliage = foliage
        self.period = config['period']
        self.elapsed = self.period * config['phase']
        self.sway_pixels = config.get('sway_pixels', 0.0)

    def update(self):
        dt = game_framework.frame_time
        if isfinite(dt) and dt > 0:
            self.elapsed = (self.elapsed + dt) % self.period

    def draw(self, camera, x, y, width, height):
        # 잎의 좌우 이동 범위까지 포함해 검사한다.
        margin = self.sway_pixels + 1
        if (x + width / 2 + margin <= camera.viewport_left
                or x - width / 2 - margin >= camera.viewport_left + camera.viewport_width
                or y + height / 2 + margin <= camera.viewport_bottom
                or y - height / 2 - margin >= camera.viewport_bottom + camera.viewport_height):
            return
        wave = sin(2 * pi * self.elapsed / self.period)
        self.branches.draw(x, y, width, height)
        self.foliage.draw(x + self.sway_pixels * wave, y, width, height)
