"""고유 ID를 가진 사각형·원형 장애물과 이동 원의 연속 충돌."""

from dataclasses import dataclass, field
from itertools import count
from math import hypot, sqrt

from game.systems.collision import CONTACT_MARGIN, _clamp_to_world, _separate_circle

_ids = count(1)
MAX_CONTACTS = 12


@dataclass(frozen=True)
class RectObstacle:
    bounds: tuple
    obstacle_id: int = field(default_factory=lambda: next(_ids))


@dataclass(frozen=True)
class CircleObstacle:
    x: float
    y: float
    radius: float
    obstacle_id: int = field(default_factory=lambda: next(_ids))


def circle_touches_bounds(x, y, radius, bounds):
    left, bottom, right, top = bounds
    return hypot(x - max(left, min(right, x)),
                 y - max(bottom, min(top, y))) <= radius


def _nearby(obstacles, ax, ay, bx, by, radius):
    """원판 이동 영역의 외접 상자와 겹친 장애물만 정밀 검사한다."""
    padding = radius + CONTACT_MARGIN * 4
    left, right = min(ax, bx) - padding, max(ax, bx) + padding
    bottom, top = min(ay, by) - padding, max(ay, by) + padding
    result = []
    for obstacle in obstacles:
        if isinstance(obstacle, CircleObstacle):
            l, b = obstacle.x - obstacle.radius, obstacle.y - obstacle.radius
            r, t = obstacle.x + obstacle.radius, obstacle.y + obstacle.radius
        else:
            l, b, r, t = obstacle.bounds
        if l <= right and r >= left and b <= top and t >= bottom:
            result.append(obstacle)
    return result


def _clearance(x, y, radius, obstacle):
    if isinstance(obstacle, CircleObstacle):
        return hypot(x - obstacle.x, y - obstacle.y) - radius - obstacle.radius
    l, b, r, t = obstacle.bounds
    return hypot(x - max(l, min(r, x)), y - max(b, min(t, y))) - radius


def _sweep_round(x, y, dx, dy, cx, cy, radius):
    ox, oy = x - cx, y - cy
    a = dx * dx + dy * dy
    dot = ox * dx + oy * dy
    if a == 0 or dot >= 0:
        return None
    discriminant = dot * dot - a * (ox * ox + oy * oy - radius * radius)
    if discriminant < 0:
        return None
    time = (-dot - sqrt(discriminant)) / a
    if not -1e-10 <= time <= 1:
        return None
    time = max(0.0, time)
    nx, ny = ox + dx * time, oy + dy * time
    length = hypot(nx, ny)
    if length == 0:
        return None
    return time, nx / length, ny / length


def _sweep(x, y, dx, dy, radius, obstacle):
    if isinstance(obstacle, CircleObstacle):
        return _sweep_round(x, y, dx, dy, obstacle.x, obstacle.y,
                            radius + obstacle.radius)
    l, b, r, t = obstacle.bounds
    candidates = []
    # 둥근 모서리를 포함한 확장 사각형과 선분의 최초 접촉.
    for edge, velocity, origin, lo, hi, other, delta, nx, ny in (
        (l - radius, dx, x, b, t, y, dy, -1, 0),
        (r + radius, dx, x, b, t, y, dy, 1, 0),
        (b - radius, dy, y, l, r, x, dx, 0, -1),
        (t + radius, dy, y, l, r, x, dx, 0, 1),
    ):
        if velocity and dx * nx + dy * ny < 0:
            time = (edge - origin) / velocity
            if 0 <= time <= 1 and lo <= other + delta * time <= hi:
                candidates.append((time, nx, ny))
    for cx, cy in ((l, b), (l, t), (r, b), (r, t)):
        result = _sweep_round(x, y, dx, dy, cx, cy, radius)
        if result is not None:
            candidates.append(result)
    return min(candidates, key=lambda hit: hit[0], default=None)


def is_circle_position_clear(x, y, radius, obstacles, world_size):
    """위치의 원 전체를 검사한다. 접촉·관통 위치를 보정 없이 거부한다."""
    width, height = world_size
    return (radius <= x <= width - radius and radius <= y <= height - radius
            and all(_clearance(x, y, radius, obstacle) > 0
                    for obstacle in _nearby(obstacles, x, y, x, y, radius)))


def is_circle_path_clear(x, y, target_x, target_y, radius, obstacles, world_size):
    """직선 보정 경로를 조회한다. 벽 건너 도착점은 허용하지 않는다."""
    width, height = world_size
    if not all(radius <= px <= width - radius and radius <= py <= height - radius
               for px, py in ((x, y), (target_x, target_y))):
        return False
    dx, dy = target_x - x, target_y - y
    return all(_clearance(x, y, radius, obstacle) >= -CONTACT_MARGIN / 2
               and _clearance(target_x, target_y, radius, obstacle) > 0
               and _sweep(x, y, dx, dy, radius, obstacle) is None
               for obstacle in _nearby(obstacles, x, y, target_x, target_y, radius))


def _recover(x, y, radius, obstacles, world_size, hits):
    """기존 건물 초기 겹침 복구용. 운석 착지 밀어내기 기능과는 별개."""
    original = _clamp_to_world(x, y, radius, world_size)
    x, y = original
    for _ in range(8):
        for obstacle in _nearby(obstacles, x, y, x, y, radius):
            if isinstance(obstacle, RectObstacle):
                corrected = _separate_circle(x, y, radius, obstacle.bounds)
            elif _clearance(x, y, radius, obstacle) < 0:
                vx, vy = x - obstacle.x, y - obstacle.y
                distance = hypot(vx, vy)
                nx, ny = (vx / distance, vy / distance) if distance else (1, 0)
                gap = radius + obstacle.radius + CONTACT_MARGIN
                corrected = obstacle.x + nx * gap, obstacle.y + ny * gap
            else:
                corrected = x, y
            if corrected != (x, y):
                hits.add(obstacle.obstacle_id)
            x, y = corrected
        x, y = _clamp_to_world(x, y, radius, world_size)
        # 보정으로 옮겨진 위치에서 후보를 다시 선정해 새 장애물을 놓치지 않는다.
        if all(_clearance(x, y, radius, obstacle) >= -CONTACT_MARGIN / 2
               for obstacle in _nearby(obstacles, x, y, x, y, radius)):
            return x, y
    return original


def move_circle(start_x, start_y, target_x, target_y, radius, obstacles, world_size=None):
    """안전 위치, 이동 중 접촉 ID 집합, 최종 접촉 ID 집합을 반환한다.

    각 이동 구간의 가장 이른 충돌에서 멈춘 뒤 남은 이동을 접선에 투영한다.
    반복 한도 도달 시 남은 이동을 버려 복합 장애물 관통을 방지한다.
    """
    obstacles = tuple(obstacles)
    if world_size is not None:
        width, height = world_size
        # 접선 이동도 월드 밖으로 나가지 않게 경계를 같은 연속 검사에 포함.
        # 음수 ID는 내부 경계 전용이며 게임의 충돌 피해 대상으로 반환하지 않는다.
        span = max(width, height) + radius * 2
        obstacles += (
            RectObstacle((-span, -span, 0, height + span), -1),
            RectObstacle((width, -span, width + span, height + span), -2),
            RectObstacle((-span, -span, width + span, 0), -3),
            RectObstacle((-span, height, width + span, height + span), -4),
        )
    hits = set()
    x, y = _recover(start_x, start_y, radius, obstacles, world_size, hits)
    target_x, target_y = _clamp_to_world(target_x, target_y, radius, world_size)
    dx, dy = target_x - x, target_y - y
    for _ in range(MAX_CONTACTS):
        if hypot(dx, dy) < 1e-10:
            break
        earliest = None
        for obstacle in _nearby(obstacles, x, y, x + dx, y + dy, radius):
            result = _sweep(x, y, dx, dy, radius, obstacle)
            if result is not None and (earliest is None or result[0] < earliest[0]):
                earliest = (*result, obstacle.obstacle_id)
        if earliest is None:
            x, y = x + dx, y + dy
            break
        time, nx, ny, obstacle_id = earliest
        hits.add(obstacle_id)
        # 접촉점보다 이동 경로를 따라 조금 앞에서 멈춰 수치적 겹침을 방지.
        safe_time = max(0.0, time - CONTACT_MARGIN / hypot(dx, dy))
        x, y = x + dx * safe_time, y + dy * safe_time
        dx, dy = dx * (1 - time), dy * (1 - time)
        inward = min(0.0, dx * nx + dy * ny)
        dx, dy = dx - inward * nx, dy - inward * ny
        # 모서리 동시 접촉 등은 다음 반복에서 남은 모든 장애물과 재검사.
    contacts = {obstacle.obstacle_id for obstacle in _nearby(obstacles, x, y, x, y, radius)
                if obstacle.obstacle_id > 0
                and _clearance(x, y, radius, obstacle) <= CONTACT_MARGIN * 4}
    return x, y, {obstacle_id for obstacle_id in hits if obstacle_id > 0}, contacts
