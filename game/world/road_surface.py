"""도로 사각형 합집합의 월드 좌표 판정. 렌더러나 화면 색상에 의존하지 않는다."""

from math import isfinite, sqrt


class RoadSurface:
    """닫힌 픽셀 셀 영역 [left, right] × [bottom, top]의 합집합.

    렌더링의 양 끝 포함 정수 사각형은 (right + 1, top + 1)로 변환한다.
    경계 접촉은 포함한다. 건물 등 장애물 제외는 호출자가 별도로 처리한다.
    """

    def __init__(self, rectangles):
        self.rectangles = tuple(rectangles)

    def contains_point(self, x, y):
        if not (isfinite(x) and isfinite(y)):
            return False
        return any(left <= x <= right and bottom <= y <= top
                   for left, bottom, right, top in self.rectangles)

    def contains_circle(self, x, y, radius):
        """원 둘레 표본이 아닌 전체 원판의 포함을 수평 띠별로 검사한다.

        사각형 경계 사이에서는 도로의 수평 단면이 일정하다. 각 띠에서
        원판 단면이 가장 넓은 높이를 검사하면 띠 전체 포함을 판정할 수 있다.
        """
        if not all(isfinite(value) for value in (x, y, radius)) or radius < 0:
            return False
        if radius == 0:
            return self.contains_point(x, y)
        low, high = y - radius, y + radius
        rectangles = [rect for rect in self.rectangles
                      if rect[0] <= x + radius and rect[2] >= x - radius
                      and rect[1] < high and rect[3] > low]
        cuts = sorted({low, high} | {max(low, min(high, edge))
                                    for rect in rectangles for edge in (rect[1], rect[3])})
        for bottom, top in zip(cuts, cuts[1:]):
            middle = (bottom + top) / 2
            nearest_y = max(bottom, min(top, y))
            half_width = sqrt(max(0.0, radius * radius - (nearest_y - y) ** 2))
            required_left, required_right = x - half_width, x + half_width
            intervals = sorted((left, right) for left, b, right, t in rectangles
                               if b < middle < t)
            covered_to = required_left
            for left, right in intervals:
                if right < covered_to:
                    continue
                if left > covered_to:
                    return False
                covered_to = max(covered_to, right)
                if covered_to >= required_right:
                    break
            if covered_to < required_right:
                return False
        return True
