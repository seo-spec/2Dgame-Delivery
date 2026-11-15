"""뷰포트 중앙 추적과 월드→화면 좌표 변환을 담당하는 카메라."""

from game.config import settings
class Camera:
    def __init__(self, x=0.0, y=0.0):
        # 보이는 월드 영역의 왼쪽 아래 위치.
        self.x = x
        self.y = y
        self.viewport_left = settings.VIEWPORT_LEFT
        self.viewport_bottom = settings.VIEWPORT_BOTTOM
        self.viewport_width = settings.VIEWPORT_WIDTH
        self.viewport_height = settings.VIEWPORT_HEIGHT

    def follow(self, target_x, target_y):
        # 가장자리에서는 카메라만 멈춘다. 월드보다 큰 뷰포트의 축은 0에 고정한다.
        self.x = max(0.0, min(target_x - self.viewport_width / 2,
                             max(0.0, settings.WORLD_WIDTH - self.viewport_width)))
        self.y = max(0.0, min(target_y - self.viewport_height / 2,
                             max(0.0, settings.WORLD_HEIGHT - self.viewport_height)))

    def world_to_screen(self, world_x, world_y):
        return (
            self.viewport_left + world_x - self.x,
            self.viewport_bottom + world_y - self.y,
        )
