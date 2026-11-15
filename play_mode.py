"""플레이 객체 구성, 게임 월드 호출, 종료 입력 처리."""

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    draw_rectangle,
    get_events,
    update_canvas,
)

import game_framework
import game_world
from camera import Camera
from cargo import Cargo
from collision import move_circle
from delivery import DeliveryHouse
from motorcycle import Motorcycle
from road_map import RoadMap, create_decorations
from ui import CargoDebugText


motorcycle = None
camera = None
cargo_debug_text = None
solid_obstacles = []
contact_obstacles = set()
delivery_houses = []


def init():
    global motorcycle, camera, cargo_debug_text
    game_world.clear()
    solid_obstacles.clear()
    contact_obstacles.clear()
    delivery_houses.clear()
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
    # 기존 건물 데이터를 참조해 위치를 중복 정의하지 않는다.
    house_config = next(
        house for house in road_map.config['buildings']
        if house.get('id') == 'collision_preview_house'
    )
    delivery_house = DeliveryHouse(
        house_config['id'], *house_config['position'], sample_cargo.cargo_id,
        zone_offset=house_config['delivery_zone']['offset'],
        zone_size=house_config['delivery_zone']['size'],
    )
    delivery_houses.append(delivery_house)
    print(
        f'[초기 확인용 화물] ID={sample_cargo.cargo_id}, '
        f'내구도={sample_cargo.current_durability}/{sample_cargo.max_durability}, '
        f'흔들림={sample_cargo.shake}, 민감도={sample_cargo.sensitivity}, '
        f'손상 임계치={sample_cargo.damage_threshold}, 배송 완료={sample_cargo.delivered}'
    )
    print(
        f'[배송지 연결] ID={delivery_house.house_id}, '
        f'월드 위치=({delivery_house.x}, {delivery_house.y}), '
        f'지정 화물={delivery_house.cargo_id}, 배송 완료={delivery_house.delivered}'
    )
    game_world.add_object(motorcycle, game_world.ACTORS)
    camera.follow(motorcycle.x, motorcycle.y)
    cargo_debug_text = CargoDebugText()


def finish():
    global motorcycle, camera, cargo_debug_text
    game_world.clear()
    motorcycle = None
    camera = None
    cargo_debug_text = None
    solid_obstacles.clear()
    contact_obstacles.clear()
    delivery_houses.clear()


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
    previous_speed = motorcycle.speed
    game_world.update()
    # 충돌 감속을 제외한 조작·자연 감속에 의한 빠르기 감소만 판단한다.
    is_decelerating = abs(motorcycle.speed) < abs(previous_speed)
    collided = False
    if solid_obstacles:
        motorcycle.x, motorcycle.y, hits, contacts = move_circle(
            previous_x, previous_y, motorcycle.x, motorcycle.y,
            motorcycle.collision_radius,
            (obstacle.get_collision_bounds() for obstacle in solid_obstacles),
        )
        collided = bool(hits)
        if hits - contact_obstacles:
            # 직접 피해는 충돌 감속 전 속도로 화물마다 한 번만 계산한다.
            impact_speed = motorcycle.speed
            for cargo in motorcycle.cargo_list:
                cargo.apply_collision_damage(impact_speed)
            # 같은 프레임에 여러 장애물을 처음 접촉해도 감속은 한 번만 적용한다.
            motorcycle.apply_collision_slowdown()
        # 이미 충돌한 장애물은 실제로 떨어질 때까지 접촉 상태를 유지한다.
        contact_obstacles.update(hits)
        contact_obstacles.intersection_update(contacts)
    # 이동·충돌 후 속도를 사용해 화물을 프레임당 한 번만 갱신한다.
    for cargo in motorcycle.cargo_list:
        cargo.update_shake(
            motorcycle.speed, motorcycle.turn_input, game_framework.frame_time,
            is_decelerating=is_decelerating, collided=collided,
        )
        cargo.apply_shake_damage(game_framework.frame_time)
    # 이번 프레임의 이동을 반영한 뒤 출력할 카메라 위치를 결정한다.
    camera.follow(motorcycle.x, motorcycle.y)


def draw():
    clear_canvas()
    game_world.render()
    for house in delivery_houses:
        left, bottom, right, top = house.get_zone_bounds()
        screen_left, screen_bottom = camera.world_to_screen(left, bottom)
        screen_right, screen_top = camera.world_to_screen(right, top)
        # 청록색 충돌 영역과 구분되는 분홍색 배송 구역. 통행을 막지 않는다.
        draw_rectangle(round(screen_left), round(screen_bottom),
                       round(screen_right), round(screen_top), 255, 100, 220)
    cargo_debug_text.draw(motorcycle.cargo_list)
    update_canvas()
