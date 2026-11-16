"""수동 크레이터 편집과 3단계 단일 운석 예고·낙하 확인 도구."""

from math import hypot

from pico2d import draw_rectangle

from game.systems.static_collision import CircleObstacle
from game.systems.meteor_placement import placement_rejection
from game.config.meteor import MIN_RADIUS, MAX_RADIUS, sample_radius
from game.objects.meteor import Meteor
from game.world.effect_shapes import EffectShapes


class DebugCraters:
    def __init__(self, road_map):
        self.road_map = road_map
        self.obstacles = []
        self.meteor = None
        self.tool = 'crater'
        self.message = f'반경 {MIN_RADIUS}~{MAX_RADIUS} 무작위 / F3으로 운석 도구 선택'

    def toggle_tool(self):
        self.tool = 'meteor' if self.tool == 'crater' else 'crater'
        self.message = ('운석 도구: 클릭하면 2초 예고 후 낙하 (착지 충돌은 4단계)'
                        if self.tool == 'meteor' else '크레이터 도구: 클릭하면 즉시 충돌체 생성')

    def create(self, x, y, motorcycle, protected_bounds, buildings):
        if self.tool == 'meteor' and self.meteor is not None:
            self.message = '운석 한 개 확인 중입니다. 착지까지 기다리거나 우클릭으로 취소하세요.'
            return
        radius = sample_radius()
        existing = (*self.obstacles, *((self.meteor,) if self.meteor is not None else ()))
        reason = placement_rejection(x, y, radius, self.road_map, motorcycle,
                                     protected_bounds, buildings, existing)
        if reason:
            self.message = f'생성 불가: {reason}'
        elif self.tool == 'meteor':
            self.meteor = Meteor(x, y, radius)
            self.message = f'운석 예고 시작 / 반경 {radius} / 낙하 {self.meteor.fall_duration:.2f}초'
        else:
            obstacle = CircleObstacle(x, y, radius)
            self.obstacles.append(obstacle)
            self.message = f'크레이터 #{obstacle.obstacle_id} 생성 / 반경 {radius:g} / 총 {len(self.obstacles)}개'

    def remove_at(self, x, y):
        if self.meteor is not None and hypot(x - self.meteor.x, y - self.meteor.y) <= self.meteor.radius:
            self.meteor = None
            self.message = '진행 중인 운석 취소'
            return set()
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
        self.meteor = None
        self.message = '임시 크레이터·운석 전체 삭제'
        return removed

    def update(self, dt):
        if self.meteor is None:
            return
        self.meteor.update(dt)
        if self.meteor.state == 'LANDED':
            self.message = '운석 착지 연출 완료 (착지 피해·크레이터 전환은 4단계)'
            self.meteor = None

    def draw(self, camera, font, debug_enabled):
        shapes = EffectShapes(camera)
        for item in self.obstacles:
            shapes.disk(item.x, item.y, item.radius, (79, 57, 48))
            color = (255, 85, 60) if debug_enabled else (150, 106, 75)
            shapes.ring(item.x, item.y, item.radius, color)
            if debug_enabled:
                shapes.text(font, item.x - 20, item.y,
                            f'#{item.obstacle_id} R{item.radius}', (255, 225, 180))
        if self.meteor is not None:
            self.meteor.draw(camera, font, debug_enabled)

    def draw_help(self, camera, font):
        left, bottom = camera.viewport_left, camera.viewport_bottom
        draw_rectangle(left + 12, bottom + 158, left + camera.viewport_width - 12,
                       bottom + 213, 25, 40, 57, filled=True)
        font.draw(left + 24, bottom + 192,
                  f'F3 도구: {"운석" if self.tool == "meteor" else "크레이터"} / 좌클릭 생성 / 우클릭 삭제 / F2 전체 삭제',
                  (255, 220, 140))
        font.draw(left + 24, bottom + 168,
                  self.message, (255, 220, 140))
