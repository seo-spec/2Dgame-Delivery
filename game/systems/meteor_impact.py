"""운석 착지 전 안전 위치 탐색. 객체를 변경하거나 피해를 주지 않는다."""

from math import atan2, cos, sin, sqrt, tau

from game.config import meteor as config
from game.systems.static_collision import is_circle_path_clear, is_circle_position_clear


def find_push_out(meteor, motorcycle, obstacles, hazards, world_size):
    """64방향의 짧은 직선 보정 중 가장 가까운 유효 위치, 없으면 None.

    새로 착지할 운석만 빠져나가는 경로에서 제외한다. 다른 예고·낙하
    영역은 hazards에 넣어 도착점뿐 아니라 이동 경로에서도 피한다.
    """
    x, y = motorcycle.x, motorcycle.y
    radius = motorcycle.collision_radius
    margin = radius * config.PUSH_OUT_MARGIN_RATIO
    clearance = meteor.radius + radius + margin
    vx, vy = x - meteor.x, y - meteor.y
    outward = atan2(vy, vx) if vx or vy else motorcycle.angle
    candidates = []
    for index in range(config.MAX_PUSH_OUT_CANDIDATES):
        angle = outward + tau * index / config.MAX_PUSH_OUT_CANDIDATES
        nx, ny = cos(angle), sin(angle)
        projection = vx * nx + vy * ny
        distance = -projection + sqrt(max(0.0, projection ** 2 + clearance ** 2 - vx ** 2 - vy ** 2))
        if 0 <= distance <= clearance + 1e-8:
            candidates.append((distance, index, x + nx * distance, y + ny * distance))
    for _, _, target_x, target_y in sorted(candidates):
        if (is_circle_position_clear(target_x, target_y, radius + margin, obstacles, world_size)
                and is_circle_path_clear(x, y, target_x, target_y, radius, obstacles, world_size)
                and is_circle_path_clear(x, y, target_x, target_y, radius + margin, hazards, world_size)):
            return target_x, target_y
    return None
