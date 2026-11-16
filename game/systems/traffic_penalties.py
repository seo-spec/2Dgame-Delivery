"""정지선 진입을 이동 경로로 검사하고 교차로 진입 한 번당 벌금을 부과한다."""


FINE_AMOUNT = 100
NOTICE_DURATION = 2.0


class TrafficPenalties:
    def __init__(self, signals):
        self.signals = signals
        self.entered = set()
        self.notice_remaining = 0.0
        self.violation_count = 0
        self.total_fines = 0

    def update(self, dt, previous, motorcycle, delivering):
        self.notice_remaining = max(0.0, self.notice_remaining - dt)
        x, y = motorcycle.x, motorcycle.y
        radius = motorcycle.collision_radius
        for signal in self.signals:
            cx, cy = signal.center
            # 뒤로 살짝 물러나거나 교차로 안에서 회전해도 같은 진입에 재부과하지 않는다.
            if max(abs(x - cx), abs(y - cy)) > signal.tile_size / 2 + radius:
                self.entered.discard(signal.center)

        crossings = []
        for signal in self.signals:
            fx, fy = signal.forward_x, signal.forward_y
            # 진행 방향의 차체 앞 가장자리가 정지선을 넘는 순간을 검사한다.
            start = ((previous[0] - signal.center[0]) * fx
                     + (previous[1] - signal.center[1]) * fy + signal.stop_distance + radius)
            end = ((x - signal.center[0]) * fx
                   + (y - signal.center[1]) * fy + signal.stop_distance + radius)
            if not start < 0 <= end:
                continue
            fraction = -start / (end - start)
            cross_x = previous[0] + (x - previous[0]) * fraction
            cross_y = previous[1] + (y - previous[1]) * fraction
            lane_offset = ((cross_x - signal.center[0]) * signal.right_x
                           + (cross_y - signal.center[1]) * signal.right_y)
            if 0 < lane_offset <= signal.road_width / 2:
                crossings.append((fraction, signal))

        fines = 0
        for fraction, signal in sorted(crossings, key=lambda item: item[0]):
            if signal.center in self.entered:
                continue
            # 초록불 진입도 기록해 진입 후 빨간불로 바뀌어도 추가로 판정하지 않는다.
            self.entered.add(signal.center)
            crossing_time = signal.elapsed - dt + fraction * dt
            if delivering and signal.state_at(crossing_time) == 'red':
                fines += FINE_AMOUNT
                self.violation_count += 1
                self.total_fines += FINE_AMOUNT
                self.notice_remaining = NOTICE_DURATION
                print(f'[신호 위반] 교차로={signal.center}, 방향={signal.axis}, '
                      f'벌금={FINE_AMOUNT}원, 누적={self.total_fines}원')
        return fines
