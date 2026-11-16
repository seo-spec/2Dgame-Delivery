"""교차로 입구의 이동 경로를 검사하고 진입 한 번당 벌금을 부과한다."""

from math import cos, sin

from game.core import debug_view
from game.systems.static_collision import circle_touches_bounds, sweep_circle_bounds

FINE_AMOUNT = 100
NOTICE_DURATION = 3.0


class TrafficPenalties:
    def __init__(self, signals):
        self.signals = signals
        self.intersections = {}
        for signal in signals:
            self.intersections.setdefault(signal.center, []).append(signal)
        self.entered = set()
        self.notice_remaining = 0.0
        self.violation_count = 0
        self.total_fines = 0
        self.last_decision = '통과 기록 없음'
        self.delivering = False

    def update(self, dt, previous, motorcycle, delivering):
        self.delivering = delivering
        self.notice_remaining = max(0.0, self.notice_remaining - dt)
        x, y = motorcycle.x, motorcycle.y
        radius = motorcycle.collision_radius
        crossings = []
        for center, signals in self.intersections.items():
            half = signals[0].entry_distance
            bounds = (center[0] - half, center[1] - half,
                      center[0] + half, center[1] + half)
            if not circle_touches_bounds(x, y, radius + 8, bounds):
                self.entered.discard(center)
            if center in self.entered:
                continue
            if circle_touches_bounds(*previous, radius, bounds):
                # 시작·위치 보정으로 이미 안에 있으면 새 진입으로 과금하지 않는다.
                if circle_touches_bounds(x, y, radius, bounds):
                    self.entered.add(center)
                continue
            hit = sweep_circle_bounds(*previous, x, y, radius, bounds)
            if hit is None:
                continue
            fraction, normal_x, normal_y = hit
            signal = max(signals, key=lambda item: (
                -normal_x * item.forward_x - normal_y * item.forward_y))
            crossings.append((fraction, signal))

        fines = 0
        for fraction, signal in sorted(crossings, key=lambda item: item[0]):
            crossing_time = signal.elapsed - dt + fraction * dt
            state = signal.state_at(crossing_time)
            if not delivering:
                self.last_decision = f'{state} / 배송 대기·복귀'
            elif state == 'red':
                self.last_decision = 'red / 100원 부과'
            else:
                self.last_decision = 'green / 정상 통과'
            if debug_view.enabled:
                print(f'[교차로 진입] 교차로={signal.center}, '
                      f'진입 방향=({signal.forward_x}, {signal.forward_y}), '
                      f'신호={state}, 배송 가능={delivering}')
            # 초록불 진입도 기록해 진입 후 빨간불로 바뀌어도 추가로 판정하지 않는다.
            self.entered.add(signal.center)
            if delivering and state == 'red':
                fines += FINE_AMOUNT
                self.violation_count += 1
                self.total_fines += FINE_AMOUNT
                self.notice_remaining = NOTICE_DURATION
                print(f'[신호 위반] 교차로={signal.center}, 방향={signal.axis}, '
                      f'벌금={FINE_AMOUNT}원, 누적={self.total_fines}원')
        return fines

    def diagnostics(self, motorcycle):
        lines = [f'벌금 신호 {len(self.signals)}개 / 배송 판정 {self.delivering}',
                 f'최근 교차로 진입: {self.last_decision}']
        if not self.signals:
            return lines
        sign = -1 if motorcycle.speed < 0 else 1
        dx, dy = cos(motorcycle.angle) * sign, sin(motorcycle.angle) * sign
        incoming = [signal for signal in self.signals
                    if dx * signal.forward_x + dy * signal.forward_y > 0.5]
        if incoming:
            signal = min(incoming, key=lambda item: (
                (motorcycle.x - item.center[0]) ** 2 + (motorcycle.y - item.center[1]) ** 2))
            distance = -((motorcycle.x - signal.center[0]) * signal.forward_x
                         + (motorcycle.y - signal.center[1]) * signal.forward_y
                         + signal.entry_distance + motorcycle.collision_radius)
            lines.append(f'진행 신호 {signal.state} / 교차로 입구 앞 {distance:.0f}px')
        return lines
