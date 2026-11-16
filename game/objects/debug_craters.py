"""수동 크레이터 편집과 단일 운석의 예고·착지·차단 확인 도구."""

from math import hypot

from pico2d import draw_rectangle

from game.systems.static_collision import CircleObstacle, RectObstacle
from game.systems.meteor_placement import interaction_bounds, placement_rejection
from game.systems.meteor_impact import find_push_out
from game.config import meteor as config
from game.config.meteor import MIN_RADIUS, MAX_RADIUS, sample_radius
from game.objects.meteor import Meteor
from game.world.effect_shapes import EffectShapes


class DebugCraters:
    def __init__(self, road_map):
        self.road_map = road_map
        self.obstacles = []
        self.meteor = None
        self.tool = 'crater'
        self.clock = 0.0
        self.expires_at = {}
        self.grace_until = 0.0
        self.landed_on_player = False
        self.landing_contacts = set()
        self.protected_bounds = interaction_bounds(road_map.config)
        self.building_footprints = []
        for index, building in enumerate(road_map.config['buildings']):
            x, y = building['position']
            width, height = building['size']
            self.building_footprints.append(RectObstacle(
                (x - width / 2, y - height / 2, x + width / 2, y + height / 2),
                -(index + 10)))
        self.message = f'반경 {MIN_RADIUS}~{MAX_RADIUS} 무작위 / F3으로 운석 도구 선택'

    def toggle_tool(self):
        self.tool = 'meteor' if self.tool == 'crater' else 'crater'
        self.message = ('운석 도구: 2초 예고 → 착지 피해·크레이터 → 3초 후 해제'
                        if self.tool == 'meteor' else '크레이터 도구: 즉시 생성 (수동 삭제까지 유지)')

    def create(self, x, y, motorcycle, buildings):
        if self.tool == 'meteor' and self.meteor is not None:
            self.message = '운석 한 개 확인 중입니다. 착지까지 기다리거나 우클릭으로 취소하세요.'
            return
        radius = sample_radius()
        existing = (*self.obstacles, *((self.meteor,) if self.meteor is not None else ()))
        reason = placement_rejection(x, y, radius, self.road_map, motorcycle,
                                     self.protected_bounds, buildings, existing)
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
        self.expires_at.pop(obstacle.obstacle_id, None)
        self.message = f'크레이터 #{obstacle.obstacle_id} 삭제'
        return {obstacle.obstacle_id}

    def clear(self):
        removed = {item.obstacle_id for item in self.obstacles}
        self.obstacles.clear()
        self.meteor = None
        self.expires_at.clear()
        self.landing_contacts.clear()
        self.grace_until = 0.0
        self.message = '임시 크레이터·운석 전체 삭제'
        return removed

    def suppress_crater_contacts(self, new_contacts):
        if self.clock < self.grace_until:
            return new_contacts - {item.obstacle_id for item in self.obstacles}
        return new_contacts

    def update(self, dt, motorcycle, buildings, *, apply_damage):
        dt = max(0.0, dt)
        previous_clock = self.clock
        self.clock += dt
        self.landed_on_player = False
        self.landing_contacts.clear()
        expired = {key for key, end in self.expires_at.items() if end <= self.clock}
        if expired:
            self.obstacles[:] = [item for item in self.obstacles if item.obstacle_id not in expired]
            for key in expired:
                del self.expires_at[key]
            self.message = '운석 크레이터 해제: 다시 통행할 수 있습니다.'
        if self.meteor is not None:
            remaining = self.meteor.remaining
            self.meteor.update(dt)
            if self.meteor.state == 'LANDED':
                meteor = self.meteor
                self.meteor = None
                # 프레임 경과분을 반영하여 착지에서 정확히 3초 뒤 해제한다.
                self._land(meteor, motorcycle, buildings, apply_damage,
                           previous_clock + remaining)
        return expired

    def _land(self, meteor, motorcycle, buildings, apply_damage, landing_time):
        reason = placement_rejection(
            meteor.x, meteor.y, meteor.radius, self.road_map, motorcycle,
            self.protected_bounds, buildings, self.obstacles, reject_player=False)
        impacted = hypot(motorcycle.x - meteor.x, motorcycle.y - meteor.y) <= meteor.radius + motorcycle.collision_radius
        target = None
        if reason is None and impacted:
            # 예고·낙하 위험을 인자로 받는 탐색 함수이며 현재는 단일 운석이다.
            # 향후 묶음 개발에서 자기 자신 외의 예고·낙하 원도 함께 전달한다.
            target = find_push_out(
                meteor, motorcycle, (*buildings, *self.building_footprints, *self.obstacles), (),
                (self.road_map.width, self.road_map.height))
            if target is None:
                reason = '벽을 넘지 않는 안전한 밀어내기 위치가 없습니다.'
        if reason is not None:
            self.message = f'착지 취소 (피해 없음): {reason}'
            print(f'[운석 착지 취소] 위치=({meteor.x:.1f}, {meteor.y:.1f}), 사유={reason}')
            return

        # 모든 안전 검사가 끝난 뒤에만 충돌체·속도·위치·화물을 변경한다.
        crater = CircleObstacle(meteor.x, meteor.y, meteor.radius)
        expires = landing_time + config.BLOCK_DURATION
        if expires > self.clock:
            self.obstacles.append(crater)
            self.expires_at[crater.obstacle_id] = expires
        if impacted:
            motorcycle.x, motorcycle.y = target
            motorcycle.speed = 0.0
            self.landed_on_player = True
            self.landing_contacts.add(crater.obstacle_id)
            self.grace_until = landing_time + config.CONTACT_GRACE_DURATION
            if apply_damage:
                for cargo in motorcycle.cargo_list:
                    cargo.apply_meteor_damage()
        self.message = ('운석 피격: 안전 위치 보정·정지 / 크레이터 3초 차단'
                        if impacted else '운석 착지: 크레이터 3초 차단')
        if expires <= self.clock:
            self.message += ' (프레임 경과로 이미 해제됨)'
        print(f'[운석 착지] ID={crater.obstacle_id}, 반경={meteor.radius}, '
              f'피격={impacted}, 화물피해={impacted and apply_damage}, 해제={expires:.3f}초')

    def draw(self, camera, font, debug_enabled):
        shapes = EffectShapes(camera)
        for item in self.obstacles:
            shapes.disk(item.x, item.y, item.radius, (79, 57, 48))
            shapes.disk(item.x, item.y, item.radius * 0.73, (55, 43, 39))
            color = (255, 85, 60) if debug_enabled else (150, 106, 75)
            shapes.ring(item.x, item.y, item.radius, color)
            if item.obstacle_id in self.expires_at:
                remaining = max(0.0, self.expires_at[item.obstacle_id] - self.clock)
                sign_y = item.y + item.radius + 20
                shapes.disk(item.x, sign_y, 12, (230, 65, 55))
                shapes.ring(item.x, sign_y, 12, (255, 205, 190))
                shapes.world_line(item.x - 7, sign_y, item.x + 7, sign_y, (255, 245, 235))
                shapes.world_line(item.x, sign_y - 12, item.x, item.y + item.radius, (220, 220, 215))
                shapes.text(font, item.x + 18, sign_y - 4,
                            f'통행 불가 {remaining:.1f}s', (255, 220, 170))
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
