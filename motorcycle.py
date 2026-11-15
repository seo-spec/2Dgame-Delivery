"""차체 방향에 따른 임시 오토바이 주행과 회전."""

from math import cos, pi, sin, tau

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LSHIFT, SDLK_RSHIFT,
    SDLK_a, SDLK_d, SDLK_s, SDLK_w, draw_line,
)

import game_framework


# 초기 주행 확인용 수치. 속도는 픽셀/초, 가감속은 픽셀/초².
FORWARD_MAX_SPEED = 180.0
REVERSE_MAX_SPEED = 60.0
FORWARD_ACCEL = 120.0
BOOST_MAX_MULTIPLIER = 1.5
BOOST_SPEED_MULTIPLIER = 1.4
BOOST_RAMP_TIME = 1.0  # 기본 배율에서 최대 배율까지 걸리는 초.
REVERSE_ACCEL = 40.0
BRAKE_ACCEL = 180.0
NATURAL_DECEL = 100.0
# 라디안/초. 초기값은 초당 180도 회전이다.
TURN_RATE = pi


class Motorcycle:
    def __init__(self, x, y, camera):
        self.camera = camera
        self.x = x
        self.y = y
        self.speed = 0.0
        self.boost_multiplier = 1.0
        # 0은 오른쪽, 양의 각도는 반시계 방향. 시작은 위쪽이다.
        self.angle = pi / 2
        self.pressed_keys = set()

    def handle_event(self, event):
        if event.key not in (SDLK_w, SDLK_s, SDLK_a, SDLK_d, SDLK_LSHIFT, SDLK_RSHIFT):
            return
        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == SDL_KEYUP:
            self.pressed_keys.discard(event.key)

    def update(self):
        dt = game_framework.frame_time
        previous_speed = self.speed
        forward_pressed = SDLK_w in self.pressed_keys
        reverse_pressed = SDLK_s in self.pressed_keys

        shift_pressed = bool(self.pressed_keys & {SDLK_LSHIFT, SDLK_RSHIFT})
        boost_active = shift_pressed and forward_pressed and not reverse_pressed and self.speed >= 0.0
        if boost_active:
            self.boost_multiplier = min(
                BOOST_MAX_MULTIPLIER,
                self.boost_multiplier + (BOOST_MAX_MULTIPLIER - 1.0) * dt / BOOST_RAMP_TIME,
            )
        else:
            self.boost_multiplier = 1.0

        if forward_pressed and not reverse_pressed:
            if not boost_active and self.speed > FORWARD_MAX_SPEED:
                # 부스트 해제 후 W를 유지해도 기본 최고속도까지 점차 감속한다.
                self.speed = max(FORWARD_MAX_SPEED, self.speed - NATURAL_DECEL * dt)
            else:
                self._accelerate(1, FORWARD_ACCEL * self.boost_multiplier, dt)
        elif reverse_pressed and not forward_pressed:
            self._accelerate(-1, REVERSE_ACCEL, dt)
        elif self.speed > 0.0:
            self.speed = max(0.0, self.speed - NATURAL_DECEL * dt)
        elif self.speed < 0.0:
            self.speed = min(0.0, self.speed + NATURAL_DECEL * dt)

        if boost_active:
            forward_limit = FORWARD_MAX_SPEED * BOOST_SPEED_MULTIPLIER
        else:
            # 이미 얻은 부스트 속도는 입력에 따른 감속으로 줄이고 순간 절단하지 않는다.
            forward_limit = max(FORWARD_MAX_SPEED, previous_speed)
        self.speed = max(-REVERSE_MAX_SPEED, min(forward_limit, self.speed))
        turn_input = int(SDLK_a in self.pressed_keys) - int(SDLK_d in self.pressed_keys)
        self.angle = (self.angle + turn_input * TURN_RATE * dt) % tau
        self.x += cos(self.angle) * self.speed * dt
        self.y += sin(self.angle) * self.speed * dt

    def _accelerate(self, direction, acceleration, dt):
        # 반대 방향으로 주행 중이면 먼저 제동한다. 정지 이후 남은 시간만
        # 새 방향의 가속에 사용해 후진에 제동 가속도가 적용되지 않게 한다.
        if self.speed * direction < 0.0:
            stop_time = abs(self.speed) / BRAKE_ACCEL
            if dt < stop_time:
                self.speed += direction * BRAKE_ACCEL * dt
                return
            self.speed = 0.0
            dt -= stop_time
        self.speed += direction * acceleration * dt

    def draw(self):
        # 도형 내부 좌표의 X 양의 방향을 차체 정면으로 사용한다.
        self._draw_outline(((-24, -12), (24, -12), (24, 12), (-24, 12)))
        self._draw_outline(((24, -6), (36, -6), (36, 6), (24, 6)))

    def _draw_outline(self, points):
        forward_x = cos(self.angle)
        forward_y = sin(self.angle)
        screen_x, screen_y = self.camera.world_to_screen(self.x, self.y)
        screen_points = [
            (
                round(screen_x + local_x * forward_x - local_y * forward_y),
                round(screen_y + local_x * forward_y + local_y * forward_x),
            )
            for local_x, local_y in points
        ]
        for index, start in enumerate(screen_points):
            end = screen_points[(index + 1) % len(screen_points)]
            draw_line(start[0], start[1], end[0], end[1])
