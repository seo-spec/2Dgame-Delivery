"""연속 각도로 주행하고 같은 차체 그림을 부드럽게 회전해 표시하는 오토바이."""

from math import cos, pi, sin, tau, radians

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LSHIFT, SDLK_RSHIFT,
    SDLK_a, SDLK_d, SDLK_s, SDLK_w, draw_line, load_image,
)

from game.core import game_framework
from game.core import debug_view
from game.ui.boost_effect import BoostEffect
from game.config.motorcycle_sprite import (
    SPRITE_PATH, SPRITE_COLUMNS, SPRITE_DIRECTION_COUNT,
    SPRITE_FRAME_WIDTH, SPRITE_FRAME_HEIGHT, SPRITE_DRAW_SIZE,
    SPRITE_CENTER_OFFSET, SPRITE_REFERENCE_RADIUS, SPRITE_FRAME_METRICS,
    SPRITE_RENDER_MODE, SPRITE_BASE_FRAME,
)
# 초기 주행 확인용 수치. 속도는 픽셀/초, 가감속은 픽셀/초².
FORWARD_MAX_SPEED = 210.0
REVERSE_MAX_SPEED = 60.0
FORWARD_ACCEL = 140.0
BOOST_MAX_MULTIPLIER = 1.8
BOOST_SPEED_MULTIPLIER = 1.6
BOOST_RAMP_TIME = 1.0  # 기본 배율에서 최대 배율까지 걸리는 초.
REVERSE_ACCEL = 40.0
BRAKE_ACCEL = 180.0
NATURAL_DECEL = 100.0
COLLISION_SPEED_REDUCTION = 0.5  # 새 건물 충돌 시 현재 속도 크기의 50% 감소.
# 라디안/초. 초기값은 초당 180도 회전이다.
TURN_RATE = pi
# 스프라이트 전체도 이 반경 안에 맞춘다. 기존 충돌 크기는 유지한다.
COLLISION_RADIUS = 37.0
COLLISION_CIRCLE_SEGMENTS = 32


class Motorcycle:
    def __init__(self, x, y, camera):
        self.camera = camera
        self.sprite_sheet = load_image(str(SPRITE_PATH))
        self.x = x
        self.y = y
        self.speed = 0.0
        self.boost_multiplier = 1.0
        self.boost_effect = BoostEffect()
        self.collision_radius = COLLISION_RADIUS
        # 0은 오른쪽, 양의 각도는 반시계 방향. 시작은 위쪽이다.
        self.angle = pi / 2
        self.pressed_keys = set()
        self.cargo_list = []
        self.turn_input = 0

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
        self.boost_effect.update(dt, boost_active)
        self.turn_input = int(SDLK_a in self.pressed_keys) - int(SDLK_d in self.pressed_keys)
        self.angle = (self.angle + self.turn_input * TURN_RATE * dt) % tau
        self.x += cos(self.angle) * self.speed * dt
        self.y += sin(self.angle) * self.speed * dt

    def apply_collision_slowdown(self):
        # 부호를 유지해 후진 충돌에서도 진행 방향이 뒤집히지 않게 한다.
        self.speed *= 1.0 - COLLISION_SPEED_REDUCTION

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
        step = tau / SPRITE_DIRECTION_COUNT
        if SPRITE_RENDER_MODE == 'continuous':
            index = SPRITE_BASE_FRAME
            display_angle = self.angle
        else:
            index = int((self.angle % tau) / step + 0.5) % SPRITE_DIRECTION_COUNT
            display_angle = index * step
        row, column = divmod(index, SPRITE_COLUMNS)
        center_x, center_y, source_degrees, source_radius = SPRITE_FRAME_METRICS[index]
        size = SPRITE_DRAW_SIZE * SPRITE_REFERENCE_RADIUS / source_radius
        scale = size / SPRITE_FRAME_WIDTH
        # 같은 그림과 중심을 유지하면 방향 전환 시 형태·크기가 바뀌지 않는다.
        # 후진도 차체 각도를 그대로 쓰며 주행 계산과는 독립적으로 출력한다.
        correction = display_angle - radians(source_degrees)
        local_x = (center_x - SPRITE_FRAME_WIDTH / 2) * scale
        local_y = (SPRITE_FRAME_HEIGHT / 2 - center_y) * scale
        screen_x, screen_y = self.camera.world_to_screen(self.x, self.y)
        draw_x = screen_x + SPRITE_CENTER_OFFSET[0] - local_x * cos(correction) + local_y * sin(correction)
        draw_y = screen_y + SPRITE_CENTER_OFFSET[1] - local_x * sin(correction) - local_y * cos(correction)
        self.boost_effect.draw(self, display_angle)
        self.sprite_sheet.clip_composite_draw(
            column * SPRITE_FRAME_WIDTH,
            self.sprite_sheet.h - (row + 1) * SPRITE_FRAME_HEIGHT,
            SPRITE_FRAME_WIDTH, SPRITE_FRAME_HEIGHT, correction, '',
            draw_x, draw_y, size, size,
        )
        if debug_view.enabled:
            self._draw_collision_circle()

    def _draw_collision_circle(self):
        center_x, center_y = self.camera.world_to_screen(self.x, self.y)
        points = [
            (round(center_x + cos(tau * index / COLLISION_CIRCLE_SEGMENTS) * self.collision_radius),
             round(center_y + sin(tau * index / COLLISION_CIRCLE_SEGMENTS) * self.collision_radius))
            for index in range(COLLISION_CIRCLE_SEGMENTS)
        ]
        for index, start in enumerate(points):
            end = points[(index + 1) % len(points)]
            draw_line(*start, *end, 255, 230, 80)
