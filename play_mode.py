"""플레이 객체 구성, 게임 월드 호출, 종료 입력 처리."""

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_SPACE,
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
from delivery import DeliveryHouse, INITIAL_DELIVERY_SETTINGS, select_delivery_buildings
from motorcycle import Motorcycle
from road_map import RoadMap, create_decorations
from settings import STAGE_1_TIME_LIMIT
from ui import CargoDebugText


motorcycle = None
camera = None
cargo_debug_text = None
solid_obstacles = []
contact_obstacles = set()
delivery_houses = []
space_pressed = False
delivery_requested = False
elapsed_time = 0.0
total_revenue = 0
cargo_received = False
pickup_bounds = None


def init():
    global motorcycle, camera, cargo_debug_text, space_pressed, delivery_requested
    global elapsed_time, total_revenue
    global cargo_received, pickup_bounds
    cargo_received = False
    elapsed_time = 0.0
    total_revenue = 0
    space_pressed = False
    delivery_requested = False
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
    # 기존 건물 위치·구역은 맵에서, 화물·요금·마감은 배송 설정에서 읽는다.
    buildings_by_id = {
        building['id']: building for building in road_map.config['buildings']
        if 'id' in building
    }
    depot = buildings_by_id['delivery_depot']
    offset_x, offset_y = depot['pickup_zone']['offset']
    width, height = depot['pickup_zone']['size']
    center_x, center_y = depot['position'][0] + offset_x, depot['position'][1] + offset_y
    pickup_bounds = (center_x - width / 2, center_y - height / 2,
                     center_x + width / 2, center_y + height / 2)
    selected_buildings = select_delivery_buildings(
        road_map.config['buildings'], len(INITIAL_DELIVERY_SETTINGS),
    )
    for building, (label, cargo_id, base_fee, deadline) in zip(
            selected_buildings, INITIAL_DELIVERY_SETTINGS):
        house = DeliveryHouse(
            building['id'], *building['position'], cargo_id,
            zone_offset=building['delivery_zone']['offset'],
            zone_size=building['delivery_zone']['size'],
            base_fee=base_fee, deadline=deadline, label=label,
        )
        delivery_houses.append(house)
        print(
            f'[배송지 연결] PRD={label}, ID={house.house_id}, '
            f'월드 위치=({house.x}, {house.y}), 지정 화물={house.cargo_id}, '
            f'기본비={house.base_fee}원, 마감={house.deadline}초'
        )
    game_world.add_object(motorcycle, game_world.ACTORS)
    camera.follow(motorcycle.x, motorcycle.y)
    cargo_debug_text = CargoDebugText()


def finish():
    global motorcycle, camera, cargo_debug_text, space_pressed, delivery_requested
    global elapsed_time, total_revenue
    global cargo_received, pickup_bounds
    cargo_received = False
    pickup_bounds = None
    elapsed_time = 0.0
    total_revenue = 0
    space_pressed = False
    delivery_requested = False
    game_world.clear()
    motorcycle = None
    camera = None
    cargo_debug_text = None
    solid_obstacles.clear()
    contact_obstacles.clear()
    delivery_houses.clear()


def handle_events():
    global space_pressed, delivery_requested
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            # 구역 밖에서도 눌림을 기록해, 유지한 채 진입하는 입력을 배제한다.
            if not space_pressed:
                space_pressed = True
                delivery_requested = True
        elif event.type == SDL_KEYUP and event.key == SDLK_SPACE:
            space_pressed = False
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):
            motorcycle.handle_event(event)


def update():
    global delivery_requested, elapsed_time, total_revenue, cargo_received
    # 출발부터의 시뮬레이션 시간. 배송은 이번 프레임의 갱신된 시간으로 판정한다.
    if cargo_received:
        elapsed_time += game_framework.frame_time
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
    # 입력은 이번 프레임의 이동·충돌·손상 결과로 판정하고, 실패해도 소비한다.
    if delivery_requested:
        delivery_requested = False
        was_received = cargo_received
        if not cargo_received and in_pickup_zone():
            motorcycle.cargo_list.extend(Cargo(house.cargo_id) for house in delivery_houses)
            cargo_received = True
            elapsed_time = 0.0
            print(f'[화물 수령 완료] 적재={len(motorcycle.cargo_list)}개, 배송 시작')
        for house in delivery_houses:
            if not was_received or not is_delivery_time_available():
                break
            if house.try_deliver(motorcycle.x, motorcycle.y, motorcycle.cargo_list,
                                 elapsed_time):
                # 배송 성공 전환에서만 확정 보상을 반영한다. 0원도 정상 정산이다.
                total_revenue += house.reward
                print(
                    f'[배송 완료] 배송지={house.house_id}, 화물={house.cargo_id}, '
                    f'경과시간={elapsed_time:.3f}초, '
                    f'고객 기분={house.delivered_mood}, 보상={house.reward}원, '
                    f'누적 수익={total_revenue}원'
                )
                break
    # 이번 프레임의 이동을 반영한 뒤 출력할 카메라 위치를 결정한다.
    camera.follow(motorcycle.x, motorcycle.y)


def draw():
    clear_canvas()
    game_world.render()
    if not cargo_received:
        left, bottom, right, top = pickup_bounds
        left, bottom = camera.world_to_screen(left, bottom)
        right, top = camera.world_to_screen(right, top)
        draw_rectangle(round(left), round(bottom), round(right), round(top), 255, 200, 60)
    for house in delivery_houses:
        bounds = house.get_zone_bounds()
        if bounds is None:
            continue
        left, bottom, right, top = bounds
        screen_left, screen_bottom = camera.world_to_screen(left, bottom)
        screen_right, screen_top = camera.world_to_screen(right, top)
        # 청록색 충돌 영역과 구분되는 분홍색 배송 구역. 통행을 막지 않는다.
        draw_rectangle(round(screen_left), round(screen_bottom),
                       round(screen_right), round(screen_top), 255, 100, 220)
        cargo_debug_text.draw_house_label(house, round(screen_left), round(screen_top) + 8)
    cargo_debug_text.draw(motorcycle.cargo_list, total_revenue, delivery_houses, elapsed_time,
                          cargo_received, STAGE_1_TIME_LIMIT)
    show_delivery_hint = is_delivery_time_available() and any(
        not house.delivered and house.contains_position(motorcycle.x, motorcycle.y)
        for house in delivery_houses
    )
    cargo_debug_text.draw_delivery_hint(show_delivery_hint)
    cargo_debug_text.draw_pickup_hint(not cargo_received and in_pickup_zone())
    update_canvas()


def in_pickup_zone():
    left, bottom, right, top = pickup_bounds
    return left <= motorcycle.x <= right and bottom <= motorcycle.y <= top


def is_delivery_time_available():
    # 표시용 반올림·0 하한 대신 갱신된 실제 경과시간으로 경계를 비교한다.
    return cargo_received and elapsed_time <= STAGE_1_TIME_LIMIT
