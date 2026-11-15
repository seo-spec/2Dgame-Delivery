"""원형 오토바이와 단일 사각형 건물의 위치 제한."""

from math import ceil, hypot


def _separate_circle(x, y, radius, bounds):
    left, bottom, right, top = bounds
    nearest_x = max(left, min(right, x))
    nearest_y = max(bottom, min(top, y))
    dx, dy = x - nearest_x, y - nearest_y
    distance = hypot(dx, dy)
    if distance >= radius:
        return x, y
    if distance > 0.0:
        return nearest_x + dx * radius / distance, nearest_y + dy * radius / distance

    # 중심이 건물 안에 있는 경우에도 가장 가까운 면 바깥으로 복구한다.
    candidates = ((left - radius, y), (right + radius, y),
                  (x, bottom - radius), (x, top + radius))
    return min(candidates, key=lambda point: hypot(point[0] - x, point[1] - y))


def move_circle(start_x, start_y, target_x, target_y, radius, bounds):
    """이동을 잘게 나누고 겹침만 보정한다. 속도·각도는 변경하지 않는다."""
    dx, dy = target_x - start_x, target_y - start_y
    # 프레임 지연이나 고속 이동에서도 건물을 한 번에 관통하지 않게 한다.
    steps = max(1, ceil(hypot(dx, dy) / (radius / 2)))
    step_x, step_y = dx / steps, dy / steps
    x, y = _separate_circle(start_x, start_y, radius, bounds)
    for _ in range(steps):
        x, y = _separate_circle(x + step_x, y + step_y, radius, bounds)
    return x, y
