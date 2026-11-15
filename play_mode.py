"""플레이 객체 구성, 게임 월드 호출, 종료 입력 처리."""

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    get_events,
    update_canvas,
)

import game_framework
import game_world
from camera import Camera
from cargo import Cargo
from collision import move_circle
from motorcycle import Motorcycle
from road_map import RoadMap, create_decorations


motorcycle = None
camera = None
solid_obstacles = []
contact_obstacles = set()


def init():
    global motorcycle, camera
    game_world.clear()
    solid_obstacles.clear()
    contact_obstacles.clear()
    camera = Camera()
    road_map = RoadMap(camera)
    game_world.add_object(road_map, game_world.BACKGROUND)
    for decoration in create_decorations(camera, road_map.config):
        game_world.add_object(decoration, game_world.BACKGROUND)
        # 충돌 영역을 명시한 건물·소품만 장애물로 등록한다.
        if decoration.get_collision_bounds() is not None:
            solid_obstacles.append(decoration)
    motorcycle = Motorcycle(*road_map.spawn, camera)
    sample_cargo = Cargo('sample_cargo_01')
    motorcycle.cargo_list.append(sample_cargo)
    print(
        f'[초기 확인용 화물] ID={sample_cargo.cargo_id}, '
        f'내구도={sample_cargo.current_durability}/{sample_cargo.max_durability}, '
        f'흔들림={sample_cargo.shake}, 민감도={sample_cargo.sensitivity}, '
        f'손상 임계치={sample_cargo.damage_threshold}, 배송 완료={sample_cargo.delivered}'
    )
    game_world.add_object(motorcycle, game_world.ACTORS)
    camera.follow(motorcycle.x, motorcycle.y)


def finish():
    global motorcycle, camera
    game_world.clear()
    motorcycle = None
    camera = None
    solid_obstacles.clear()
    contact_obstacles.clear()


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):
            motorcycle.handle_event(event)


def update():
    previous_x, previous_y = motorcycle.x, motorcycle.y
    game_world.update()
    if solid_obstacles:
        motorcycle.x, motorcycle.y, hits, contacts = move_circle(
            previous_x, previous_y, motorcycle.x, motorcycle.y,
            motorcycle.collision_radius,
            (obstacle.get_collision_bounds() for obstacle in solid_obstacles),
        )
        if hits - contact_obstacles:
            # 같은 프레임에 여러 장애물을 처음 접촉해도 감속은 한 번만 적용한다.
            motorcycle.apply_collision_slowdown()
        # 이미 충돌한 장애물은 실제로 떨어질 때까지 접촉 상태를 유지한다.
        contact_obstacles.update(hits)
        contact_obstacles.intersection_update(contacts)
    # 이번 프레임의 이동을 반영한 뒤 출력할 카메라 위치를 결정한다.
    camera.follow(motorcycle.x, motorcycle.y)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()
