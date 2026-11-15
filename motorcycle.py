"""위쪽을 바라보는 임시 오토바이 도형과 Y축 주행."""

from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_s, SDLK_w, draw_rectangle

import game_framework


# 초기 주행 확인용 수치. 속도는 픽셀/초, 가감속은 픽셀/초².
FORWARD_MAX_SPEED = 180.0
REVERSE_MAX_SPEED = 90.0
FORWARD_ACCEL = 120.0
BRAKE_ACCEL = 180.0
NATURAL_DECEL = 100.0


class Motorcycle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.0
        self.pressed_keys = set()

    def handle_event(self, event):
        if event.key not in (SDLK_w, SDLK_s):
            return
        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == SDL_KEYUP:
            self.pressed_keys.discard(event.key)

    def update(self):
        dt = game_framework.frame_time
        forward_pressed = SDLK_w in self.pressed_keys
        reverse_pressed = SDLK_s in self.pressed_keys

        if forward_pressed and not reverse_pressed:
            self.speed += FORWARD_ACCEL * dt
        elif reverse_pressed and not forward_pressed:
            self.speed -= BRAKE_ACCEL * dt
        elif self.speed > 0.0:
            self.speed = max(0.0, self.speed - NATURAL_DECEL * dt)
        elif self.speed < 0.0:
            self.speed = min(0.0, self.speed + NATURAL_DECEL * dt)

        self.speed = max(-REVERSE_MAX_SPEED, min(FORWARD_MAX_SPEED, self.speed))
        self.y += self.speed * dt

    def draw(self):
        # 긴 차체와 위쪽으로 돌출된 앞부분으로 정면을 구분한다.
        draw_rectangle(self.x - 12, self.y - 24, self.x + 12, self.y + 24)
        draw_rectangle(self.x - 6, self.y + 24, self.x + 6, self.y + 36)
