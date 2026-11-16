"""운석·크레이터의 공통 배치 제한. 도로 밖도 허용하되 건물·배송 접근을 보호."""

from math import hypot

from game.systems.static_collision import circle_touches_bounds


def placement_rejection(x, y, radius, road_map, motorcycle, protected_bounds,
                        buildings, existing):
    """거부 사유 또는 None. 낙하·피해·경로 탐색은 수행하지 않는다."""
    if not (radius <= x <= road_map.width - radius
            and radius <= y <= road_map.height - radius):
        return '크레이터 전체가 맵 안에 있어야 합니다.'
    if hypot(x - motorcycle.x, y - motorcycle.y) <= radius + motorcycle.collision_radius:
        return '오토바이와 겹칩니다.'
    # 건물 충돌 박스가 그림보다 작으므로 집 보호에는 전체 표시 영역도 사용.
    for building in road_map.config['buildings']:
        bx, by = building['position']
        width, height = building['size']
        if circle_touches_bounds(x, y, radius,
                                 (bx - width / 2, by - height / 2,
                                  bx + width / 2, by + height / 2)):
            return '집·건물의 표시 영역과 겹칩니다.'
    if any(circle_touches_bounds(x, y, radius, item.bounds) for item in buildings):
        return '기존 건물·고정 장애물과 겹칩니다.'
    # 구역 안에 오토바이 중심이 들어갈 수 있도록 몸체 크기와 안전 여유 확보.
    approach_margin = motorcycle.collision_radius * 1.1
    if any(circle_touches_bounds(x, y, radius + approach_margin, bounds)
           for bounds in protected_bounds):
        return '수령·복귀·배송 구역의 접근 공간과 겹칩니다.'
    if any(hypot(x - item.x, y - item.y) <= radius + item.radius for item in existing):
        return '다른 크레이터와 겹칩니다.'
    return None
