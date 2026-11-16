"""운석 묶음의 보수적인 탈출 경로 검사. 안전한 지면에서 실제 도로 통로까지 탐색."""

from collections import defaultdict, deque
from dataclasses import dataclass
from math import ceil, floor, hypot, sqrt

from game.config import meteor as config
from game.systems.static_collision import (
    CircleObstacle, RectObstacle, circle_touches_bounds, is_circle_path_clear,
)
from game.world.road_surface import RoadSurface


@dataclass
class EscapeBudget:
    calls: int = 0
    nodes: int = 0

    @property
    def exhausted(self):
        return self.calls >= config.MAX_ESCAPE_SEARCHES or self.nodes >= config.MAX_ESCAPE_NODES


def _segment_distance(ax, ay, bx, by, cx, cy):
    dx, dy = bx - ax, by - ay
    length_squared = dx * dx + dy * dy
    amount = (max(0.0, min(1.0, ((cx - ax) * dx + (cy - ay) * dy) / length_squared))
              if length_squared else 0.0)
    return hypot(ax + dx * amount - cx, ay + dy * amount - cy)


class EscapeNavigation:
    """지도 수명 동안 정적 지면·도로·간선 판정을 재사용한다.

    격자 간격은 오토바이 반경/2. 매 연결은 원판의 이동 경로를 검사하며
    도로 구간은 확장 원판으로 덮어 보수적으로 포함 여부를 확인한다.
    """

    def __init__(self, road_map, buildings, player_radius):
        self.road_map = road_map
        self.player_radius = player_radius
        self.radius = player_radius * (1 + config.PUSH_OUT_MARGIN_RATIO)
        self.step = player_radius / 2
        self.world_size = road_map.width, road_map.height
        self.bin_size = road_map.tile_size
        self.static_bins = defaultdict(list)
        self.road_bins = defaultdict(list)
        self.local_roads = {}
        self.ground_cache = {}
        self.road_cache = {}
        self.edge_cache = {}
        self.portal_cache = {}
        static = list(buildings)
        for index, building in enumerate(road_map.config['buildings']):
            x, y = building['position']
            width, height = building['size']
            static.append(RectObstacle((x - width / 2, y - height / 2,
                                        x + width / 2, y + height / 2), -(index + 10)))
        for obstacle in static:
            for key in self._bins(*obstacle.bounds):
                self.static_bins[key].append(obstacle)
        for rect in road_map.road_surface.rectangles:
            for key in self._bins(*rect):
                self.road_bins[key].append(rect)
        self.portals = []
        size = road_map.tile_size
        # 실제 도로 연결 비트가 이어진 타일 경계만 통로 후보로 사용한다.
        for (column, row), mask in road_map.roads.items():
            for dx, dy, bit, reverse in ((1, 0, 2, 8), (0, 1, 1, 4)):
                if mask & bit and road_map.roads.get((column + dx, row + dy), 0) & reverse:
                    x = (column + 0.5 + dx / 2) * size
                    y = (row + 0.5 + dy / 2) * size
                    for sign in (-1, 1):
                        self.portals.append((x, y, x + dx * sign * player_radius * 2,
                                             y + dy * sign * player_radius * 2))

    def _bins(self, left, bottom, right, top):
        for column in range(floor(left / self.bin_size), floor(right / self.bin_size) + 1):
            for row in range(floor(bottom / self.bin_size), floor(top / self.bin_size) + 1):
                yield column, row

    def _near_static(self, ax, ay, bx, by, radius):
        found = {}
        for key in self._bins(min(ax, bx) - radius, min(ay, by) - radius,
                              max(ax, bx) + radius, max(ay, by) + radius):
            for obstacle in self.static_bins.get(key, ()):
                found[obstacle.obstacle_id] = obstacle
        return tuple(found.values())

    def _ground_point(self, x, y):
        radius = self.radius
        width, height = self.world_size
        return (radius <= x <= width - radius and radius <= y <= height - radius
                and not any(circle_touches_bounds(x, y, radius, item.bounds)
                            for item in self._near_static(x, y, x, y, radius)))

    def _road_circle(self, x, y, radius):
        # 원을 덮는 도로 사각형만 모은다. 원래 렌더링 도형의 합집합은 유지한다.
        keys = tuple(self._bins(x - radius, y - radius, x + radius, y + radius))
        if keys not in self.local_roads:
            rects = {rect for key in keys for rect in self.road_bins.get(key, ())}
            self.local_roads[keys] = RoadSurface(rects)
        return self.local_roads[keys].contains_circle(x, y, radius)

    def _road_line(self, ax, ay, bx, by):
        distance = hypot(bx - ax, by - ay)
        count = max(1, ceil(distance / (self.step / 2)))
        # 선분 위의 가장 가까운 표본까지 거리는 간격/2 이하이고 수직 거리는
        # 원 반경 이하다. 이 상한으로 원판 이동 영역을 보수적으로 모두 덮는다.
        cover_radius = sqrt(self.radius ** 2 + (distance / count / 2) ** 2)
        return all(self._road_circle(ax + (bx - ax) * i / count,
                                     ay + (by - ay) * i / count, cover_radius)
                   for i in range(count + 1))

    def _static_line(self, ax, ay, bx, by, road_only):
        return (is_circle_path_clear(ax, ay, bx, by, self.radius,
                                    self._near_static(ax, ay, bx, by, self.radius), self.world_size)
                and (not road_only or self._road_line(ax, ay, bx, by)))

    def _position(self, node):
        return (node[0] + 0.5) * self.step, (node[1] + 0.5) * self.step

    def _point(self, node, road_only):
        if node not in self.ground_cache:
            self.ground_cache[node] = self._ground_point(*self._position(node))
        if not self.ground_cache[node]:
            return False
        if road_only and node not in self.road_cache:
            self.road_cache[node] = self._road_circle(*self._position(node), self.radius)
        return not road_only or self.road_cache[node]

    def _edge(self, a, b, road_only):
        key = (*sorted((a, b)), road_only)
        if key not in self.edge_cache:
            self.edge_cache[key] = self._static_line(*self._position(a), *self._position(b), road_only)
        return self.edge_cache[key]

    def _near_nodes(self, x, y):
        column, row = floor(x / self.step), floor(y / self.step)
        nodes = [(column + dx, row + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        return sorted(nodes, key=lambda node: hypot(self._position(node)[0] - x,
                                                     self._position(node)[1] - y))

    def road_points_in_view(self, camera):
        """캐시된 정적 도로 격자에서 화면 안 후보 중심만 반환한다."""
        left, bottom = camera.x, camera.y
        right, top = left + camera.viewport_width, bottom + camera.viewport_height
        return [self._position((column, row))
                for column in range(floor(left / self.step), ceil(right / self.step))
                for row in range(floor(bottom / self.step), ceil(top / self.step))
                if self._point((column, row), True)
                and left <= self._position((column, row))[0] <= right
                and bottom <= self._position((column, row))[1] <= top]

    def _portal_anchors(self, portal):
        if portal not in self.portal_cache:
            x, y, end_x, end_y = portal
            anchors = []
            if self._static_line(x, y, end_x, end_y, True):
                for node in self._near_nodes(x, y):
                    if self._point(node, True) and self._static_line(*self._position(node), x, y, True):
                        anchors.append(node)
            self.portal_cache[portal] = tuple(anchors)
        return self.portal_cache[portal]

    def check(self, motorcycle, existing, planned, budget):
        """(안전 여부, 사유)를 반환. 모든 위험을 차단으로 가정한 공간 연결성 검사."""
        if budget.exhausted:
            return False, '탐색 한도 초과'
        budget.calls += 1
        start_x, start_y = motorcycle.x, motorcycle.y
        if not self._ground_point(start_x, start_y):
            return False, '출발 위치 안전 여유 부족'
        road_only = self._road_circle(start_x, start_y, self.radius)
        hazards = (*existing, *planned)
        initially_inside = {
            id(item) for item in hazards if not isinstance(item, CircleObstacle)
            and hypot(start_x - item.x, start_y - item.y) <= item.radius + self.radius
        }

        def dynamic_line(ax, ay, bx, by, allow_initial=True):
            for item in hazards:
                radius = item.radius + self.radius
                inside = hypot(ax - item.x, ay - item.y) <= radius
                if allow_initial and id(item) in initially_inside and inside:
                    # 최초 겹침에서 단조롭게 빠져나오는 구간만 허용. 밖에 나온 뒤
                    # 재진입은 아래 전체 선분 검사에서 거부한다.
                    if (ax - item.x) * (bx - ax) + (ay - item.y) * (by - ay) < -1e-8:
                        return False
                elif _segment_distance(ax, ay, bx, by, item.x, item.y) <= radius:
                    return False
            return True

        goals = defaultdict(list)
        portals = sorted((portal for portal in self.portals
                          if hypot(portal[0] - start_x, portal[1] - start_y) >= self.player_radius * 4),
                         key=lambda portal: hypot(portal[0] - start_x, portal[1] - start_y))
        for portal in portals[:config.MAX_ESCAPE_PORTALS]:
            x, y, end_x, end_y = portal
            if dynamic_line(x, y, end_x, end_y, False):
                for node in self._portal_anchors(portal):
                    if dynamic_line(*self._position(node), x, y, False):
                        goals[node].append(portal)
        if not goals:
            return False, '안전한 도로 통로 없음'
        queue = deque()
        visited = set()
        for node in self._near_nodes(start_x, start_y):
            x, y = self._position(node)
            if (self._point(node, road_only)
                    and self._static_line(start_x, start_y, x, y, road_only)
                    and dynamic_line(start_x, start_y, x, y)):
                queue.append(node)
                visited.add(node)
        while queue:
            if budget.nodes >= config.MAX_ESCAPE_NODES:
                return False, '탐색 한도 초과'
            node = queue.popleft()
            budget.nodes += 1
            x, y = self._position(node)
            if node in goals:
                # 위험 내부의 출발 예외가 목표 지점에까지 이어지지 않도록 재검사.
                for portal in goals[node]:
                    if dynamic_line(x, y, portal[0], portal[1], False):
                        return True, '탈출 경로 확보'
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)):
                neighbor = node[0] + dx, node[1] + dy
                if neighbor in visited or not self._point(neighbor, road_only):
                    continue
                nx, ny = self._position(neighbor)
                if self._edge(node, neighbor, road_only) and dynamic_line(x, y, nx, ny):
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False, '도로 통로 연결 경로 없음'
