"""시뮬레이션 시간으로 움직이는 가벼운 부스터 불꽃·속도선."""

from math import cos, sin, tau

from pico2d import draw_line


class BoostEffect:
    def __init__(self):
        self.elapsed = 0.0
        self.active = False

    def update(self, dt, active):
        self.active = active
        self.elapsed = (self.elapsed + dt) % 10.0 if active else 0.0

    def draw(self, motorcycle, display_angle):
        if not self.active or motorcycle.speed <= 1.0:
            return
        x, y = motorcycle.camera.world_to_screen(motorcycle.x, motorcycle.y)
        forward_x, forward_y = cos(display_angle), sin(display_angle)
        side_x, side_y = -forward_y, forward_x
        strength = max(0.0, min(1.0, (motorcycle.boost_multiplier - 1.0) / 0.8))
        pulse = sin(self.elapsed * tau * 14)
        length = 22 + 22 * strength + 4 * pulse
        rear = motorcycle.collision_radius - 9

        def point(distance, side):
            return (round(x - forward_x * (rear + distance) + side_x * side),
                    round(y - forward_y * (rear + distance) + side_y * side))

        # 세 겹 불꽃을 차체보다 먼저 그려 뿌리가 뒷바퀴 아래로 자연스럽게 숨는다.
        for spread, ratio, color in (
                (8, 1.0, (255, 133, 50)),
                (5, 0.78, (255, 218, 100)),
                (2, 0.53, (220, 247, 255))):
            tip = point(length * ratio, pulse * spread * 0.15)
            for side in (-spread, 0, spread):
                draw_line(*point(0, side), *tip, *color)
        # 입자 목록을 계속 쌓지 않고 두 줄의 짧은 속도선만 재사용한다.
        travel = (self.elapsed * 8) % 1.0
        for side in (-1, 1):
            start = 10 + travel * 22
            offset = side * (15 + travel * 5)
            draw_line(*point(start, offset), *point(start + 9, offset), 132, 221, 245)
