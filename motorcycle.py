"""오른쪽을 바라보는 임시 오토바이 도형."""

from pico2d import draw_rectangle


class Motorcycle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        pass

    def draw(self):
        # 긴 차체와 오른쪽으로 돌출된 앞부분으로 정면을 구분한다.
        draw_rectangle(self.x - 24, self.y - 12, self.x + 24, self.y + 12)
        draw_rectangle(self.x + 24, self.y - 6, self.x + 36, self.y + 6)
