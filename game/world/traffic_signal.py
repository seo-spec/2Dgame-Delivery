"""십자 교차로 차선 위에 걸린 탑뷰 신호등. 기둥과 암에는 충돌이 없다."""

from pico2d import draw_rectangle

from game.core import game_framework
from game.world.effect_shapes import EffectShapes


class TrafficSignal:
    GREEN_DURATION = 4.0

    def __init__(self, camera, center, direction, road_width, sidewalk_width):
        self.camera = camera
        self.center = tuple(center)
        self.road_width = road_width
        self.entry_distance = road_width / 2
        self.forward_x, self.forward_y = direction
        self.right_x, self.right_y = self.forward_y, -self.forward_x
        self.axis = 'horizontal' if self.forward_x else 'vertical'
        self.elapsed = 0.0
        self.state = 'green' if self.axis == 'horizontal' else 'red'
        corner = road_width / 2 + sidewalk_width / 2
        self.x = center[0] + (self.forward_x + self.right_x) * corner
        self.y = center[1] + (self.forward_y + self.right_y) * corner
        self.head_x = center[0] + self.forward_x * corner + self.right_x * road_width / 4
        self.head_y = center[1] + self.forward_y * corner + self.right_y * road_width / 4

    def get_collision_bounds(self):
        return None

    def update(self):
        self.elapsed = (self.elapsed + game_framework.frame_time) % (self.GREEN_DURATION * 2)
        self.state = self.state_at(self.elapsed)

    def state_at(self, elapsed):
        horizontal_green = elapsed % (self.GREEN_DURATION * 2) < self.GREEN_DURATION
        green = horizontal_green if self.axis == 'horizontal' else not horizontal_green
        return 'green' if green else 'red'

    def _bar(self, shapes, x1, y1, x2, y2, thickness, color):
        x1, y1 = self.camera.world_to_screen(x1, y1)
        x2, y2 = self.camera.world_to_screen(x2, y2)
        half = thickness / 2
        left, right = max(shapes.left, min(x1, x2) - half), min(shapes.right, max(x1, x2) + half)
        bottom, top = max(shapes.bottom, min(y1, y2) - half), min(shapes.top, max(y1, y2) + half)
        if left <= right and bottom <= top:
            draw_rectangle(round(left), round(bottom), round(right), round(top), *color, filled=True)

    def draw(self):
        shapes = EffectShapes(self.camera)
        sx, sy = self.camera.world_to_screen(self.head_x, self.head_y)
        if (sx + 60 < shapes.left or sx - 60 > shapes.right
                or sy + 60 < shapes.bottom or sy - 60 > shapes.top):
            return
        # 작은 그림자와 금속 하이라이트로 차도 위에 떠 있는 암을 표현한다.
        self._bar(shapes, self.x + 3, self.y - 4, self.head_x + 3, self.head_y - 4, 9, (38, 43, 45))
        shapes.disk(self.x, self.y, 8, (43, 48, 51))
        shapes.disk(self.x - 1, self.y + 1, 5, (157, 166, 169))
        self._bar(shapes, self.x, self.y, self.head_x, self.head_y, 6, (78, 88, 94))
        self._bar(shapes, self.x - 1, self.y + 1, self.head_x - 1, self.head_y + 1, 2, (177, 187, 190))
        # 3구 본체는 암을 따라 놓이고, 진입 차량을 향한 챙이 아래쪽에 붙는다.
        for depth, thickness, color in ((0, 15, (23, 29, 33)), (-6, 3, (8, 12, 15))):
            x = self.head_x + self.forward_x * depth
            y = self.head_y + self.forward_y * depth
            self._bar(shapes, x - self.right_x * 14, y - self.right_y * 14,
                      x + self.right_x * 14, y + self.right_y * 14, thickness, color)
        for offset, lamp in ((-10, 'red'), (0, 'yellow'), (10, 'green')):
            x = self.head_x + self.right_x * offset
            y = self.head_y + self.right_y * offset
            color = ((255, 75, 61) if lamp == 'red' else (65, 250, 142)) if lamp == self.state else (49, 55, 58)
            shapes.disk(x, y, 4, color)
            if lamp == self.state:
                shapes.disk(x - 1, y + 1, 1, (255, 246, 211))
