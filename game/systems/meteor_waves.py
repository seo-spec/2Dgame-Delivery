"""운석 묶음 주기, 근처 도로 우선 배정과 탈출 검증을 거친 후보 확정."""

from collections import Counter
from dataclasses import dataclass
from math import cos, hypot, sin
from random import randint, shuffle, uniform
from time import perf_counter

from game.config import meteor as config
from game.objects.meteor import Meteor
from game.systems.meteor_placement import placement_rejection
from game.systems.meteor_escape import EscapeBudget, EscapeNavigation


@dataclass(frozen=True)
class PlacementCandidate:
    x: float
    y: float
    radius: int
    source: str


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
        self.navigation = None
        self.last_near_requested = 0
        self.last_near_count = 0
        self.last_front_count = 0
        self.last_searches = 0
        self.last_nodes = 0
        self.last_reason = '대기'
        self.last_duration_ms = 0.0

    def prepare_navigation(self, motorcycle, buildings):
        if self.navigation is None or self.navigation.player_radius != motorcycle.collision_radius:
            self.navigation = EscapeNavigation(self.road_map, buildings, motorcycle.collision_radius)

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
        started = perf_counter()
        self.wave_number += 1
        requested = randint(config.MIN_WAVE_COUNT, config.MAX_WAVE_COUNT)
        near_requested = min(requested, randint(config.MIN_NEAR_COUNT, config.MAX_NEAR_COUNT))
        self.prepare_navigation(motorcycle, buildings)
        camera = self.road_map.camera
        road_points = self.navigation.road_points_in_view(camera)
        sign = -1 if motorcycle.speed < -0.001 else 1
        forward_x, forward_y = cos(motorcycle.angle) * sign, sin(motorcycle.angle) * sign
        front_pool = [(x, y) for x, y in road_points
                      if (x - motorcycle.x) * forward_x + (y - motorcycle.y) * forward_y > 0]
        view_pool = list(road_points)
        shuffle(front_pool)
        shuffle(view_pool)
        planned = []
        rejected = Counter()
        attempts = 0

        def try_candidate(source, point=None):
            nonlocal attempts
            if attempts >= config.MAX_WAVE_PLACEMENT_ATTEMPTS:
                return None
            attempts += 1
            radius = config.sample_radius()
            if point is None:
                x = uniform(radius, self.road_map.width - radius)
                y = uniform(radius, self.road_map.height - radius)
            else:
                x, y = point
                if not (camera.x + radius <= x <= camera.x + camera.viewport_width - radius
                        and camera.y + radius <= y <= camera.y + camera.viewport_height - radius):
                    rejected['근처 원이 화면 밖으로 나감'] += 1
                    return None
                if not self.road_map.is_circle_on_road(x, y, radius):
                    rejected['근처 원 전체가 도로 내부가 아님'] += 1
                    return None
            reason = placement_rejection(
                x, y, radius, self.road_map, motorcycle, self.protected_bounds,
                buildings, (*existing, *planned), reject_player=False)
            if reason is not None:
                rejected[reason] += 1
                return None
            return PlacementCandidate(x, y, radius, source)

        # 우선 배정도 같은 500회 후보 예산을 쓴다. 실패하면 화면의 다른 도로로 확대.
        for pool, source, limit in ((front_pool, 'front', config.MAX_NEAR_FRONT_ATTEMPTS),
                                    (view_pool, 'view', config.MAX_NEAR_VIEW_ATTEMPTS)):
            phase_attempts = 0
            while (len(planned) < near_requested and pool and phase_attempts < limit
                   and attempts < config.MAX_WAVE_PLACEMENT_ATTEMPTS):
                candidate = try_candidate(source, pool.pop())
                phase_attempts += 1
                if candidate is not None:
                    planned.append(candidate)
        while len(planned) < requested and attempts < config.MAX_WAVE_PLACEMENT_ATTEMPTS:
            candidate = try_candidate('global')
            if candidate is not None:
                planned.append(candidate)

        budget = EscapeBudget()
        path_rejections = Counter()
        replacements = 0
        removed_count = 0
        route_reason = '후보 없음'
        safe = False
        while planned:
            safe, route_reason = self.navigation.check(motorcycle, existing, planned, budget)
            if safe:
                break
            path_rejections[route_reason] += 1
            if budget.exhausted or route_reason == '출발 위치 안전 여유 부족':
                break
            # 가장 가까운 위험부터 바꿔 보되, 교체 실패·반복 실패 시 수량을 줄인다.
            removed = min(planned, key=lambda item: hypot(item.x - motorcycle.x, item.y - motorcycle.y) - item.radius)
            planned.remove(removed)
            removed_count += 1
            if replacements < config.MAX_REPLACEMENTS and attempts < config.MAX_WAVE_PLACEMENT_ATTEMPTS:
                replacements += 1
                for _ in range(config.REPLACEMENT_ATTEMPTS):
                    if attempts >= config.MAX_WAVE_PLACEMENT_ATTEMPTS:
                        break
                    if removed.source != 'global' and (front_pool or view_pool):
                        pool = front_pool if front_pool else view_pool
                        source = 'front' if pool is front_pool else 'view'
                        replacement = try_candidate(source, pool.pop())
                    else:
                        replacement = try_candidate('global')
                    if replacement is not None:
                        planned.append(replacement)
                        break
        if not safe:
            planned.clear()
        durations = config.sample_fall_durations(len(planned))
        result = [Meteor(item.x, item.y, item.radius, started_at=clock,
                         wave_id=self.wave_number, fall_duration=duration)
                  for item, duration in zip(planned, durations)]
        self.last_requested = requested
        self.last_count = len(result)
        self.last_attempts = attempts
        self.last_near_requested = near_requested
        self.last_near_count = sum(item.source != 'global' for item in planned)
        self.last_front_count = sum(
            item.source != 'global'
            and (item.x - motorcycle.x) * forward_x + (item.y - motorcycle.y) * forward_y > 0
            for item in planned)
        self.last_searches = budget.calls
        self.last_nodes = budget.nodes
        self.last_reason = (f'생략: {route_reason}' if not result
                            else '축소: 탈출 경로' if len(result) < requested and removed_count
                            else '축소: 후보 부족' if len(result) < requested
                            else '교체: 탈출 경로' if removed_count else '근처 후보 부족' if self.last_near_count < near_requested
                            else '정상')
        self.last_duration_ms = (perf_counter() - started) * 1000
        interval = config.sample_wave_interval()
        self.next_wave_at = clock + interval
        print(f'[운석 묶음] 번호={self.wave_number}, 배송 경과={clock - self.started_at:.3f}초, '
              f'예고 시작={clock:.3f}, 예정 대비 지연={clock - scheduled_at:.3f}초, '
              f'생성={len(result)}/{requested}, 근처={self.last_near_count}/{near_requested}, '
              f'전방={self.last_front_count}, 후보={attempts}, 경로={budget.calls}, 확장={budget.nodes}, '
              f'처리={self.last_duration_ms:.1f}ms, 상태={self.last_reason}, 다음 간격={interval:.3f}초')
        print(f'[운석 안전 배치] 묶음={self.wave_number}, 경로 결과={route_reason}, '
              f'제거/교체 검사={removed_count}, 교체 시도={replacements}, '
              f'경로 거부={dict(path_rejections)}, 후보 거부={dict(rejected)}')
        for meteor in result:
            print(f'[운석 예고] 묶음={meteor.wave_id}, 운석={meteor.creation_id}, '
                  f'위치=({meteor.x:.1f}, {meteor.y:.1f}), 반경={meteor.radius}, '
                  f'낙하 시간={meteor.fall_duration:.3f}초, 예정 착지={meteor.landing_time:.3f}초')
        if len(result) < requested or self.last_near_count < near_requested:
            print(f'[운석 수량 조정] 묶음={self.wave_number}, 부족={requested - len(result)}, '
                  f'근처 부족={near_requested - self.last_near_count}, 사유={self.last_reason}, 경로={route_reason}')
        return result

    def status(self, clock):
        if self.started_at is None:
            return '자동 운석: 화물 수령 대기'
        if not self.running:
            return f'자동 운석 중단 / 마지막 묶음 #{self.wave_number}'
        remaining = max(0.0, self.next_wave_at - clock)
        return (f'묶음 #{self.wave_number}: {self.last_count}/{self.last_requested}개 '
                f'/ 근처 {self.last_near_count}/{self.last_near_requested}개 / 다음 예고 {remaining:.1f}초')

    def diagnostics(self):
        return (f'후보 {self.last_attempts}/{config.MAX_WAVE_PLACEMENT_ATTEMPTS} '
                f'/ 경로 {self.last_searches}/{config.MAX_ESCAPE_SEARCHES} '
                f'/ 확장 {self.last_nodes}/{config.MAX_ESCAPE_NODES} '
                f'/ {self.last_reason} ({self.last_duration_ms:.1f}ms)')
