"""플레이 뷰포트에 잘라 그리는 월드 효과용 기본 도형."""

from math import ceil, cos, floor, sin, sqrt, tau

from pico2d import draw_line


class EffectShapes:
    def __init__(self, camera):
        self.camera = camera
        self.left = camera.viewport_left
        self.bottom = camera.viewport_bottom
        self.right = self.left + camera.viewport_width - 1
        self.top = self.bottom + camera.viewport_height - 1

    def line(self, x1, y1, x2, y2, color):
        """화면 좌표 선분을 뷰포트와 교차하는 구간만 표시한다."""
        dx, dy = x2 - x1, y2 - y1
        low, high = 0.0, 1.0
        for p, q in ((-dx, x1 - self.left), (dx, self.right - x1),
                     (-dy, y1 - self.bottom), (dy, self.top - y1)):
            if p == 0:
                if q < 0:
                    return
                continue
            time = q / p
            if p < 0:
                low = max(low, time)
            else:
                high = min(high, time)
            if low > high:
                return
        draw_line(round(x1 + low * dx), round(y1 + low * dy),
                  round(x1 + high * dx), round(y1 + high * dy), *color)

    def ring(self, x, y, radius, color):
        x, y = self.camera.world_to_screen(x, y)
        if radius <= 0 or x + radius < self.left or x - radius > self.right or y + radius < self.bottom or y - radius > self.top:
            return
        for index in range(96):
            a, b = tau * index / 96, tau * (index + 1) / 96
            self.line(x + cos(a) * radius, y + sin(a) * radius,
                      x + cos(b) * radius, y + sin(b) * radius, color)

    def world_line(self, x1, y1, x2, y2, color):
        x1, y1 = self.camera.world_to_screen(x1, y1)
        x2, y2 = self.camera.world_to_screen(x2, y2)
        self.line(x1, y1, x2, y2, color)

    def disk(self, x, y, radius, color):
        x, y = self.camera.world_to_screen(x, y)
        for row in range(max(self.bottom, ceil(y - radius)), min(self.top, floor(y + radius)) + 1):
            half = sqrt(max(0, radius * radius - (row - y) ** 2))
            left, right = max(self.left, ceil(x - half)), min(self.right, floor(x + half))
            if left <= right:
                draw_line(left, row, right, row, *color)

    def text(self, font, x, y, text, color):
        x, y = self.camera.world_to_screen(x, y)
        # 글자를 잘라 그릴 수 없으므로 전체 문구가 들어오는 위치에서만 표시.
        if self.left <= x and x + len(text) * 18 <= self.right and self.bottom + 20 <= y <= self.top - 20:
            font.draw(round(x), round(y), text, color)


class EffectLabels:
    """효과 문구를 모아 HUD·서로의 문구를 피하는 가까운 위치에 표시한다."""

    def __init__(self, camera, font, reserved=()):
        self.camera = camera
        self.font = font
        self.reserved = list(reserved)
        self.requests = []

    def add(self, x, y, text, color, priority=(5, 0)):
        self.requests.append((priority, len(self.requests), x, y, text, color))

    def draw(self):
        left, bottom = self.camera.viewport_left, self.camera.viewport_bottom
        right, top = left + self.camera.viewport_width - 1, bottom + self.camera.viewport_height - 1
        occupied = list(self.reserved)
        for _, _, x, y, text, color in sorted(self.requests):
            sx, sy = self.camera.world_to_screen(x, y)
            if not (left - 60 <= sx <= right + 60 and bottom - 60 <= sy <= top + 60):
                continue
            width = sum(18 if ord(char) > 127 else 10 for char in text)
            if width > right - left - 8:
                continue
            for ox, oy in ((-width / 2, 0), (-width / 2, 26), (-width / 2, -26),
                           (18, 0), (-width - 18, 0), (-width / 2, 52), (-width / 2, -52)):
                px = max(left + 4, min(right - width - 4, sx + ox))
                py = max(bottom + 8, min(top - 24, sy + oy))
                bounds = px - 3, py - 5, px + width + 3, py + 21
                if any(bounds[0] < r and bounds[2] > l and bounds[1] < t and bounds[3] > b
                       for l, b, r, t in occupied):
                    continue
                self.font.draw(round(px + 1), round(py - 1), text, (10, 15, 18))
                self.font.draw(round(px), round(py), text, color)
                occupied.append(bounds)
                break
