"""화물 수령 후의 운석 묶음 주기와 한도 있는 전체 맵 위치 추첨."""

from collections import Counter
from random import randint, uniform

from game.config import meteor as config
from game.objects.meteor import Meteor
from game.systems.meteor_placement import placement_rejection


class MeteorWaves:
    def __init__(self, road_map, protected_bounds):
        self.road_map = road_map
        self.protected_bounds = protected_bounds
        self.started_at = None
        self.next_wave_at = None
        self.wave_number = 0
        self.last_requested = 0
        self.last_count = 0
        self.last_attempts = 0
        self.running = False

    def start(self, clock):
        if self.started_at is not None:
            return
        self.started_at = clock
        self.running = True
        interval = config.sample_wave_interval()
        self.next_wave_at = clock + interval
        print(f'[운석 자동 시작] 첫 예고까지={interval:.3f}초')

    def stop(self):
        if self.running:
            print(f'[운석 자동 중단] 마지막 묶음={self.wave_number}, 기존 운석은 종료까지 진행')
        self.running = False
        self.next_wave_at = None

    def update(self, clock, motorcycle, buildings, existing):
        if not self.running or self.next_wave_at is None or clock < self.next_wave_at:
            return []
        # 밀린 주기를 반복 처리하지 않는다. 새 묶음은 현재부터 온전한 경고를 제공한다.
        scheduled_at = self.next_wave_at
        self.wave_number += 1
        requested = randint(config.MIN_WAVE_COUNT, config.MAX_WAVE_COUNT)
        durations = config.sample_fall_durations(requested)
        planned = []
        rejected = Counter()
        attempts = 0
        for attempts in range(1, config.MAX_WAVE_PLACEMENT_ATTEMPTS + 1):
            radius = config.sample_radius()
            x = uniform(radius, self.road_map.width - radius)
            y = uniform(radius, self.road_map.height - radius)
            reason = placement_rejection(
                x, y, radius, self.road_map, motorcycle, self.protected_bounds,
                buildings, (*existing, *planned), reject_player=False)
            if reason is not None:
                rejected[reason] += 1
                continue
            planned.append(Meteor(x, y, radius, started_at=clock, wave_id=self.wave_number,
                                  fall_duration=durations[len(planned)]))
            if len(planned) >= requested:
                break
        self.last_requested = requested
        self.last_count = len(planned)
        self.last_attempts = attempts
        interval = config.sample_wave_interval()
        self.next_wave_at = clock + interval
        print(f'[운석 묶음] 번호={self.wave_number}, 배송 경과={clock - self.started_at:.3f}초, '
              f'예고 시작={clock:.3f}, 예정 대비 지연={clock - scheduled_at:.3f}초, '
              f'생성={len(planned)}/{requested}, 후보 검사={attempts}, 다음 간격={interval:.3f}초')
        for meteor in planned:
            print(f'[운석 예고] 묶음={meteor.wave_id}, 운석={meteor.creation_id}, '
                  f'위치=({meteor.x:.1f}, {meteor.y:.1f}), 반경={meteor.radius}, '
                  f'낙하 시간={meteor.fall_duration:.3f}초, 예정 착지={meteor.landing_time:.3f}초')
        if len(planned) < requested:
            print(f'[운석 후보 부족] 묶음={self.wave_number}, 부족={requested - len(planned)}, '
                  f'검사 한도={config.MAX_WAVE_PLACEMENT_ATTEMPTS}, 거부 사유={dict(rejected)}')
        return planned

    def status(self, clock):
        if self.started_at is None:
            return '자동 운석: 화물 수령 대기'
        if not self.running:
            return f'자동 운석 중단 / 마지막 묶음 #{self.wave_number}'
        remaining = max(0.0, self.next_wave_at - clock)
        return (f'묶음 #{self.wave_number}: {self.last_count}/{self.last_requested}개 '
                f'/ 다음 예고 {remaining:.1f}초 / 후보 검사 {self.last_attempts}')
