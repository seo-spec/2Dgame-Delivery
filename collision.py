"""원형 오토바이와 여러 사각형 건물의 위치 제한."""

from math import ceil, hypot


CONTACT_MARGIN = 0.0001
MAX_SEPARATION_PASSES = 8


def _overlaps_circle(x, y, radius, bounds):
    left, bottom, right, top = bounds
    nearest_x = max(left, min(right, x))
    nearest_y = max(bottom, min(top, y))
    return hypot(x - nearest_x, y - nearest_y) < radius - CONTACT_MARGIN / 2


def _separate_circle(x, y, radius, bounds):
    left, bottom, right, top = bounds
    nearest_x = max(left, min(right, x))
    nearest_y = max(bottom, min(top, y))
    dx, dy = x - nearest_x, y - nearest_y
    distance = hypot(dx, dy)
    if distance >= radius:
        return x, y
    clearance = radius + CONTACT_MARGIN
    if distance > 0.0:
        return nearest_x + dx * clearance / distance, nearest_y + dy * clearance / distance

    # 중심이 건물 안에 있는 경우에도 가장 가까운 면 바깥으로 복구한다.
    candidates = ((left - clearance, y), (right + clearance, y),
                  (x, bottom - clearance), (x, top + clearance))
    return min(candidates, key=lambda point: hypot(point[0] - x, point[1] - y))


def _separate_from_buildings(x, y, radius, buildings, hits):
    # 한 건물의 보정으로 다른 건물과 겹칠 수 있으므로 전체를 다시 확인한다.
    for _ in range(MAX_SEPARATION_PASSES):
        for index, bounds in enumerate(buildings):
            corrected_x, corrected_y = _separate_circle(x, y, radius, bounds)
            if (corrected_x, corrected_y) != (x, y):
                hits.add(index)
            x, y = corrected_x, corrected_y
        if not any(_overlaps_circle(x, y, radius, bounds) for bounds in buildings):
            return x, y
    return None


def move_circle(start_x, start_y, target_x, target_y, radius, buildings):
    """보정 위치, 이동 중 충돌 건물 번호, 최종 접촉 건물 번호를 반환한다."""
    buildings = tuple(buildings)
    if not buildings:
        return target_x, target_y, set(), set()
    hits = set()
    dx, dy = target_x - start_x, target_y - start_y
    # 프레임 지연이나 고속 이동에서도 건물을 한 번에 관통하지 않게 한다.
    steps = max(1, ceil(hypot(dx, dy) / (radius / 2)))
    step_x, step_y = dx / steps, dy / steps
    x, y = _separate_from_buildings(start_x, start_y, radius, buildings, hits) or (start_x, start_y)
    for _ in range(steps):
        resolved = _separate_from_buildings(x + step_x, y + step_y, radius, buildings, hits)
        if resolved is not None:
            x, y = resolved
            continue
        # 원이 들어갈 수 없는 좁은 틈에서는 마지막 안전 위치를 유지한다.
        # 한 축만 이동할 수 있다면 벽을 따라 빠져나가는 것은 허용한다.
        candidates = ((x + step_x, y), (x, y + step_y))
        for candidate_x, candidate_y in candidates:
            if not any(_overlaps_circle(candidate_x, candidate_y, radius, bounds)
                       for bounds in buildings):
                x, y = candidate_x, candidate_y
                break
    contacts = set()
    for index, (left, bottom, right, top) in enumerate(buildings):
        nearest_x = max(left, min(right, x))
        nearest_y = max(bottom, min(top, y))
        # 겹침 보정용 미세 여백 때문에 접촉이 매 프레임 끊기지 않도록 한다.
        if hypot(x - nearest_x, y - nearest_y) <= radius + CONTACT_MARGIN * 2:
            contacts.add(index)
    return x, y, hits, contacts
