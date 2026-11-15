"""화물별 독립 상태와 회전 주행에 따른 흔들림 증가."""


# 개발 확인용 초기값이며 확정된 게임 밸런스 수치가 아니다.
INITIAL_MAX_DURABILITY = 100.0
INITIAL_SHAKE = 0.0
INITIAL_SENSITIVITY = 1.0
INITIAL_DAMAGE_THRESHOLD = 50.0
MAX_SHAKE = 100.0
SHAKE_INCREASE_FACTOR = 0.1


class Cargo:
    def __init__(self, cargo_id, max_durability=INITIAL_MAX_DURABILITY,
                 sensitivity=INITIAL_SENSITIVITY,
                 damage_threshold=INITIAL_DAMAGE_THRESHOLD):
        self.cargo_id = cargo_id
        self.max_durability = max_durability
        self.current_durability = max_durability
        self.shake = INITIAL_SHAKE
        self.sensitivity = sensitivity
        self.damage_threshold = damage_threshold
        self.delivered = False

    def increase_shake(self, speed, turn_input, dt):
        if self.delivered or self.current_durability <= 0.0:
            return
        increase = abs(speed) * abs(turn_input) * self.sensitivity * SHAKE_INCREASE_FACTOR * dt
        self.shake = min(MAX_SHAKE, max(0.0, self.shake + increase))
