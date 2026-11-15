"""화물별 독립 상태와 주행에 따른 흔들림 증가·회복."""


# 개발 확인용 초기값이며 확정된 게임 밸런스 수치가 아니다.
INITIAL_MAX_DURABILITY = 100.0
INITIAL_SHAKE = 0.0
INITIAL_SENSITIVITY = 1.0
INITIAL_DAMAGE_THRESHOLD = 50.0
MAX_SHAKE = 100.0
SHAKE_INCREASE_FACTOR = 0.15  # 기존 대비 회전 중 흔들림 증가량 1.5배.
SHAKE_RECOVERY_RATE = 20.0  # 초당 회복량. 최대 흔들림 100에서 직진·정지 시 약 5초.
SHAKE_DAMAGE_FACTOR = 0.2  # 임계치 초과 흔들림 50에서 초당 내구도 10 감소.
COLLISION_DAMAGE_FACTOR = 0.05  # 충돌 속도 180픽셀/초에서 내구도 9 감소.


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

    def update_shake(self, speed, turn_input, dt, is_decelerating=False, collided=False):
        if self.delivered or self.current_durability <= 0.0:
            return
        increase = abs(speed) * abs(turn_input) * self.sensitivity * SHAKE_INCREASE_FACTOR * dt
        recovery = 0.0
        if not collided and (turn_input == 0 or is_decelerating):
            # 직진과 감속 조건을 모두 만족해도 회복은 한 번만 적용한다.
            recovery = SHAKE_RECOVERY_RATE * dt
        self.shake = min(MAX_SHAKE, max(0.0, self.shake + increase - recovery))

    def apply_shake_damage(self, dt):
        if self.delivered or self.current_durability <= 0.0:
            return
        excess_shake = max(0.0, self.shake - self.damage_threshold)
        damage = excess_shake * SHAKE_DAMAGE_FACTOR * dt
        self.current_durability = max(0.0, self.current_durability - damage)

    def apply_collision_damage(self, impact_speed):
        if self.delivered or self.current_durability <= 0.0:
            return
        # 접촉 시작 이벤트의 피해이므로 프레임 경과시간을 곱하지 않는다.
        damage = abs(impact_speed) * COLLISION_DAMAGE_FACTOR
        self.current_durability = max(0.0, self.current_durability - damage)
