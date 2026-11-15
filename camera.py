"""월드 좌표를 화면 좌표로 변환하는 카메라."""

import settings


class Camera:
    def __init__(self, x=0.0, y=0.0):
        # 보이는 월드 영역의 왼쪽 아래 위치.
        self.x = x
        self.y = y
        self.viewport_left = settings.VIEWPORT_LEFT
        self.viewport_bottom = settings.VIEWPORT_BOTTOM

    def world_to_screen(self, world_x, world_y):
        return (
            self.viewport_left + world_x - self.x,
            self.viewport_bottom + world_y - self.y,
        )
