"""단일 운석의 예고·낙하. 착지 확정과 크레이터 전환은 관리 객체가 처리한다."""

from random import uniform
from itertools import count

from game.config import meteor as config
from game.world.effect_shapes import EffectShapes

_creation_ids = count(1)


class Meteor:
    def __init__(self, x, y, radius, *, started_at=0.0, wave_id=None, fall_duration=None):
        self.creation_id = next(_creation_ids)
        self.wave_id = wave_id
        self.started_at = started_at
        self.x = x
        self.y = y
        self.radius = radius
        # 예고 전에 추첨하여 동심원이 처음부터 실제 착지 시각을 가리킨다.
        self.fall_duration = (uniform(config.MIN_FALL_DURATION, config.MAX_FALL_DURATION)
                              if fall_duration is None else fall_duration)
        self.warning_duration = config.WARNING_DURATION
        self.elapsed = 0.0

    @property
    def total_duration(self):
        return self.warning_duration + self.fall_duration

    @property
    def landing_time(self):
        return self.started_at + self.total_duration

    @property
    def remaining(self):
        return max(0.0, self.total_duration - self.elapsed)

    @property
    def warning_bright(self):
        return int(self.elapsed * 6) % 2 == 0

    @property
    def state(self):
        if self.elapsed >= self.total_duration:
            return 'LANDED'
        if self.elapsed >= self.warning_duration:
            return 'FALLING'
        return 'WARNING'

    def update(self, dt):
        self.elapsed = min(self.total_duration, self.elapsed + max(0.0, dt))

    def update_to(self, clock):
        self.elapsed = min(self.total_duration, max(0.0, clock - self.started_at))

    def draw(self, camera, font, debug_enabled, labels=None):
        shapes = EffectShapes(camera)
        # 위험 외곽은 끝까지 같은 반경. 줄어드는 안쪽 원은 착지까지의 시간.
        color = (255, 75, 65) if self.warning_bright else (185, 65, 60)
        shapes.ring(self.x, self.y, self.radius, color)
        shapes.ring(self.x, self.y, self.radius - 2, color)
        fraction = self.remaining / self.total_duration
        shapes.ring(self.x, self.y, self.radius * fraction, (255, 220, 135))
        if labels is not None:
            labels.add(self.x, self.y + self.radius + 15,
                       f'{self.remaining:.1f}초', (255, 220, 170), (0, self.remaining))
        else:
            shapes.text(font, self.x - 32, self.y + self.radius + 15,
                        f'{self.remaining:.1f}s', (255, 220, 170))
        if self.state == 'FALLING':
            progress = min(1.0, (self.elapsed - self.warning_duration) / self.fall_duration)
            height = config.FALL_HEIGHT * (1 - progress * progress)
            body_y = self.y + height
            # 위에서 수직 낙하한다. 높이는 표시용이며 지상 목표는 변하지 않는다.
            shapes.disk(self.x, body_y + self.radius * 0.65, self.radius * 0.8, (230, 93, 35))
            shapes.disk(self.x, body_y + self.radius * 0.3, self.radius * 0.95, (255, 155, 45))
            shapes.disk(self.x, body_y, self.radius, (106, 78, 63))
            shapes.ring(self.x, body_y, self.radius, (255, 186, 80))
            shapes.disk(self.x - self.radius * 0.3, body_y + self.radius * 0.2,
                        self.radius * 0.2, (62, 50, 46))
            shapes.disk(self.x + self.radius * 0.25, body_y - self.radius * 0.3,
                        self.radius * 0.15, (72, 56, 48))
        if debug_enabled:
            if labels is not None:
                labels.add(self.x, self.y - self.radius - 22,
                           f'#{self.creation_id} R{self.radius}', (235, 195, 155), (9, 0))
            else:
                shapes.text(font, self.x - 32, self.y - self.radius - 22,
                            f'R{self.radius} / {self.fall_duration:.2f}s', (255, 220, 170))
