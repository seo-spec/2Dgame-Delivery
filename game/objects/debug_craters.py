"""2단계 수동 확인용 크레이터. 자동 생성·수명·착지 효과는 없다."""

from math import cos, sin, tau, hypot, sqrt, ceil, floor

from pico2d import draw_line, draw_rectangle

from game.systems.static_collision import CircleObstacle, circle_touches_bounds


class DebugCraters:
    def __init__(self, road_map):
        self.road_map = road_map
        self.obstacles = []
        # 수동 충돌 확인용 크기. 기획의 실제 운석 크기와는 별도로 둔다.
        # 현재 도로 폭 120에 기획 반경 74를 쓰면 직선 도로 생성이 전부 거부된다.
        self.radius = min(74.0, road_map.geometry.road_width * 0.35)
        self.message = 'F1 디버그: 좌클릭 생성 / 우클릭 삭제 / F2 전체 삭제'

    def create(self, x, y, motorcycle, protected_bounds, buildings):
        radius = self.radius
        if not self.road_map.is_circle_on_road(x, y, radius):
            self.message = f'생성 불가: 도로 중앙을 클릭하세요. (테스트 반경 {radius:g})'
        elif hypot(x - motorcycle.x, y - motorcycle.y) <= radius + motorcycle.collision_radius:
            self.message = '생성 불가: 오토바이와 겹칩니다.'
        elif any(circle_touches_bounds(x, y, radius, bounds)
                 for bounds in (*protected_bounds, *(item.bounds for item in buildings))):
            self.message = '생성 불가: 건물 또는 수령·복귀·배송 구역과 겹칩니다.'
        elif any(hypot(x - item.x, y - item.y) <= radius + item.radius
                 for item in self.obstacles):
            self.message = '생성 불가: 다른 크레이터와 겹칩니다.'
        else:
            obstacle = CircleObstacle(x, y, radius)
            self.obstacles.append(obstacle)
            self.message = f'크레이터 #{obstacle.obstacle_id} 생성 / 반경 {radius:g} / 총 {len(self.obstacles)}개'

    def remove_at(self, x, y):
        obstacle = next((item for item in reversed(self.obstacles)
                         if hypot(x - item.x, y - item.y) <= item.radius), None)
        if obstacle is None:
            self.message = '삭제할 크레이터 안을 우클릭하세요.'
            return set()
        self.obstacles.remove(obstacle)
        self.message = f'크레이터 #{obstacle.obstacle_id} 삭제'
        return {obstacle.obstacle_id}

    def clear(self):
        removed = {item.obstacle_id for item in self.obstacles}
        self.obstacles.clear()
        self.message = '임시 크레이터 전체 삭제'
        return removed

    def draw(self, camera, font, debug_enabled):
        left, bottom = camera.viewport_left, camera.viewport_bottom
        right, top = left + camera.viewport_width - 1, bottom + camera.viewport_height - 1
        for item in self.obstacles:
            x, y = camera.world_to_screen(item.x, item.y)
            # 원형 바닥 표시를 플레이 뷰포트 안에서만 그린다.
            for row in range(max(bottom, ceil(y - item.radius)), min(top, floor(y + item.radius)) + 1):
                half = sqrt(max(0, item.radius ** 2 - (row - y) ** 2))
                x1, x2 = max(left, ceil(x - half)), min(right, floor(x + half))
                if x1 <= x2:
                    draw_line(x1, row, x2, row, 79, 57, 48)
            color = (255, 85, 60) if debug_enabled else (150, 106, 75)
            for index in range(96):
                a, b = tau * index / 96, tau * (index + 1) / 96
                x1, y1 = round(x + cos(a) * item.radius), round(y + sin(a) * item.radius)
                x2, y2 = round(x + cos(b) * item.radius), round(y + sin(b) * item.radius)
                if left <= x1 <= right and left <= x2 <= right and bottom <= y1 <= top and bottom <= y2 <= top:
                    draw_line(x1, y1, x2, y2, *color)
            if debug_enabled and left + 5 <= x <= right - 100 and bottom + 20 <= y <= top - 20:
                font.draw(round(x - 20), round(y), f'#{item.obstacle_id}', (255, 225, 180))

    def draw_help(self, camera, font):
        left, bottom = camera.viewport_left, camera.viewport_bottom
        draw_rectangle(left + 12, bottom + 158, left + camera.viewport_width - 12,
                       bottom + 213, 25, 40, 57, filled=True)
        font.draw(left + 24, bottom + 192,
                  'F1 디버그: 좌클릭 생성 / 우클릭 삭제 / F2 전체 삭제', (255, 220, 140))
        font.draw(left + 24, bottom + 168,
                  self.message, (255, 220, 140))
