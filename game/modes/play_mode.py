"""플레이 객체 구성, 게임 월드 호출, 종료 입력 처리."""

from random import sample

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEMOTION,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_F1,
    SDLK_F2,
    SDLK_F3,
    SDLK_SPACE,
    SDLK_r,
    SDLK_UP,
    SDLK_DOWN,
    SDLK_RETURN,
    clear_canvas,
    draw_rectangle,
    get_events,
    get_canvas_height,
    update_canvas,
)

from game.core import game_framework
from game.core import debug_view
from game.core import game_world
from game.world.camera import Camera
from game.objects.cargo import Cargo
from game.config.cargo_types import CARGO_TYPES
from game.systems.static_collision import RectObstacle, move_circle
from game.systems.meteor_system import MeteorSystem
from game.systems.delivery import (
    DeliveryHouse, INITIAL_DELIVERY_SETTINGS, select_delivery_buildings, select_delivery_target,
)
from game.objects.motorcycle import Motorcycle
from game.ui.minimap import MiniMap
from game.world.road_map import RoadMap, create_decorations
from game.config.settings import WORLD_WIDTH, WORLD_HEIGHT
from game.systems.stage import GameController, StageState
from game.ui.hud import CargoDebugText


motorcycle = None
camera = None
cargo_debug_text = None
minimap = None
solid_obstacles = []
static_colliders = []
meteor_system = None
contact_obstacles = set()
delivery_houses = []
space_pressed = False
delivery_requested = False
controller = None
total_revenue = 0

pickup_bounds = None
held_keys = set()
blocked_keys = set()
restart_frame = False
paused = False
pause_selection = 0


def init():
    global meteor_system
    global minimap
    global motorcycle, camera, cargo_debug_text, space_pressed, delivery_requested
    global controller, total_revenue
    global pickup_bounds
    global restart_frame, paused, pause_selection
    paused = False
    pause_selection = 0
    held_keys.clear()
    blocked_keys.clear()
    restart_frame = False
    controller = GameController()
    debug_view.enabled = False
    total_revenue = 0
    space_pressed = False
    delivery_requested = False
    game_world.clear()
    solid_obstacles.clear()
    static_colliders.clear()
    contact_obstacles.clear()
    delivery_houses.clear()
    camera = Camera()
    road_map = RoadMap(camera)
    meteor_system = MeteorSystem(road_map)
    game_world.add_object(road_map, game_world.BACKGROUND)
    for decoration in create_decorations(camera, road_map.config):
        game_world.add_object(decoration, game_world.BACKGROUND)
        # 충돌 영역을 명시한 건물·소품만 장애물로 등록한다.
        if decoration.get_collision_bounds() is not None:
            solid_obstacles.append(decoration)
            static_colliders.append(RectObstacle(decoration.get_collision_bounds()))
    motorcycle = Motorcycle(*road_map.spawn, camera)
    meteor_system.waves.prepare_navigation(motorcycle, static_colliders)
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
    minimap = MiniMap(road_map, cargo_debug_text.font)


def finish():
    global meteor_system
    meteor_system = None
    static_colliders.clear()
    global minimap
    minimap = None
    global motorcycle, camera, cargo_debug_text, space_pressed, delivery_requested
    global controller, total_revenue
    global pickup_bounds
    pickup_bounds = None
    controller = None
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
    global space_pressed, delivery_requested, restart_frame, paused, pause_selection
    restart_requested = False
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if paused and not restart_requested and event.type in (SDL_MOUSEMOTION, SDL_MOUSEBUTTONDOWN):
            selected = cargo_debug_text.pause_button_at(event.x, get_canvas_height() - 1 - event.y)
            if selected is not None:
                pause_selection = selected
                if event.type == SDL_MOUSEBUTTONDOWN and event.button == 1:
                    restart_requested = activate_pause_selection()
            continue
        if (event.type == SDL_MOUSEBUTTONDOWN and debug_view.enabled and not restart_requested
                and not paused and controller.state not in (StageState.FAILED, StageState.CLEAR)):
            screen_y = get_canvas_height() - 1 - event.y
            if (camera.viewport_left <= event.x < camera.viewport_left + camera.viewport_width
                    and camera.viewport_bottom <= screen_y < camera.viewport_bottom + camera.viewport_height):
                x = event.x - camera.viewport_left + camera.x
                y = screen_y - camera.viewport_bottom + camera.y
                if event.button == 1:
                    meteor_system.create(x, y, motorcycle, static_colliders)
                elif event.button == 3:
                    contact_obstacles.difference_update(meteor_system.remove_at(x, y))
            continue
        # 결과 상태에서도 눌림을 추적해, 이전부터 유지한 키의 반복 입력을 배제한다.
        if event.type == SDL_KEYDOWN:
            fresh_press = event.key not in held_keys
            held_keys.add(event.key)
        elif event.type == SDL_KEYUP:
            held_keys.discard(event.key)
        else:
            continue
        if restart_requested:
            continue
        if event.key in blocked_keys:
            if event.type == SDL_KEYUP:
                blocked_keys.discard(event.key)
            continue
        if event.key == SDLK_ESCAPE:
            if event.type == SDL_KEYDOWN and fresh_press:
                set_paused(not paused)
            continue
        if paused:
            if event.type == SDL_KEYDOWN and fresh_press:
                if event.key == SDLK_UP:
                    pause_selection = (pause_selection - 1) % 3
                elif event.key == SDLK_DOWN:
                    pause_selection = (pause_selection + 1) % 3
                elif event.key == SDLK_RETURN:
                    restart_requested = activate_pause_selection()
            continue
        if event.key == SDLK_F1:
            if event.type == SDL_KEYDOWN and fresh_press:
                debug_view.enabled = not debug_view.enabled
            continue
        if event.key == SDLK_r:
            if (event.type == SDL_KEYDOWN and fresh_press
                    and controller.state in (StageState.FAILED, StageState.CLEAR)):
                restart_requested = True
            continue
        if controller.state in (StageState.FAILED, StageState.CLEAR):
            continue
        if event.key == SDLK_F2:
            if debug_view.enabled and event.type == SDL_KEYDOWN and fresh_press:
                contact_obstacles.difference_update(meteor_system.clear())
            continue
        if event.key == SDLK_F3:
            if debug_view.enabled and event.type == SDL_KEYDOWN and fresh_press:
                meteor_system.toggle_tool()
            continue
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            # 구역 밖에서도 눌림을 기록해, 유지한 채 진입하는 입력을 배제한다.
            if not space_pressed:
                space_pressed = True
                delivery_requested = True
        elif event.type == SDL_KEYUP and event.key == SDLK_SPACE:
            space_pressed = False
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):
            motorcycle.handle_event(event)
    if restart_requested:
        # 남은 이벤트까지 소비한 뒤 재구성한다. 유지 중인 키는 해제 후 다시 눌러야 한다.
        previous_held_keys = held_keys.copy()
        finish()
        init()
        held_keys.update(previous_held_keys)
        blocked_keys.update(previous_held_keys)
        restart_frame = True
        print('[다시 시작] 화물 수령 대기')


def update():
    global delivery_requested, total_revenue, restart_frame
    if restart_frame:
        # 리소스 재초기화에 걸린 시간을 새 플레이의 이동에 적용하지 않는다.
        restart_frame = False
        return
    if paused:
        return
    # 출발부터의 시뮬레이션 시간. 배송은 이번 프레임의 갱신된 시간으로 판정한다.
    if controller.state in (StageState.FAILED, StageState.CLEAR):
        delivery_requested = False
        return
    controller.advance_time(game_framework.frame_time)
    # 자동·수동 운석 모두 시뮬레이션 시간을 따르며 정지·결과에서는 갱신하지 않는다.
    expired_craters = meteor_system.update(
        game_framework.frame_time, motorcycle, static_colliders,
        apply_damage=controller.state == StageState.DELIVERING)
    contact_obstacles.difference_update(expired_craters)
    # 착지 접촉을 미리 소비하여 일반 충돌 피해와 중복되지 않게 한다.
    contact_obstacles.update(meteor_system.landing_contacts)
    previous_x, previous_y = motorcycle.x, motorcycle.y
    previous_speed = motorcycle.speed
    game_world.update()
    # 충돌 감속을 제외한 조작·자연 감속에 의한 빠르기 감소만 판단한다.
    is_decelerating = abs(motorcycle.speed) < abs(previous_speed)
    motorcycle.x, motorcycle.y, hits, contacts = move_circle(
        previous_x, previous_y, motorcycle.x, motorcycle.y,
        motorcycle.collision_radius,
        (*static_colliders, *meteor_system.obstacles),
        world_size=(WORLD_WIDTH, WORLD_HEIGHT),
    )
    collided = bool(hits) or meteor_system.landed_on_player
    fresh_contacts = meteor_system.suppress_crater_contacts(hits - contact_obstacles)
    if fresh_contacts:
        # 직접 피해는 충돌 감속 전 속도로 화물마다 한 번만 계산한다.
        impact_speed = motorcycle.speed
        if controller.state == StageState.DELIVERING:
            for cargo in motorcycle.cargo_list:
                cargo.apply_collision_damage(impact_speed)
        # 같은 프레임에 여러 장애물을 처음 접촉해도 감속은 한 번만 적용한다.
        motorcycle.apply_collision_slowdown()
        if debug_view.enabled:
            print(f'[새 충돌] 장애물 ID={sorted(fresh_contacts)}, '
                  f'충돌 속도={impact_speed:.2f}, 감속 후={motorcycle.speed:.2f}')
    # 이미 충돌한 장애물은 실제로 떨어질 때까지 접촉 상태를 유지한다.
    contact_obstacles.update(hits)
    contact_obstacles.intersection_update(contacts)
    # 이동·충돌 후 속도를 사용해 화물을 프레임당 한 번만 갱신한다.
    if controller.state == StageState.DELIVERING:
        for cargo in motorcycle.cargo_list:
            cargo.update_shake(
                motorcycle.speed, motorcycle.turn_input, game_framework.frame_time,
                is_decelerating=is_decelerating, collided=collided,
            )
            cargo.apply_shake_damage(game_framework.frame_time)
    # 입력은 이번 프레임의 이동·충돌·손상 결과로 판정하고, 실패해도 소비한다.
    if delivery_requested:
        delivery_requested = False
        was_delivering = controller.state == StageState.DELIVERING
        if controller.state == StageState.WAITING and in_pickup_zone():
            selected_types = sample(CARGO_TYPES, len(delivery_houses))
            motorcycle.cargo_list.extend(
                Cargo(house.cargo_id, cargo_type=cargo_type)
                for house, cargo_type in zip(delivery_houses, selected_types)
            )
            for house, cargo in zip(delivery_houses, motorcycle.cargo_list):
                print(f'[화물 종류] {house.label}: {cargo.cargo_type.name} ({cargo.cargo_id})')
            cargo_debug_text.prepare_cargo_icons(motorcycle.cargo_list)
            if controller.start_delivery():
                meteor_system.start_waves()
            print(f'[화물 수령 완료] 적재={len(motorcycle.cargo_list)}개, 배송 시작')
        house = current_delivery_target() if was_delivering else None
        if house is not None and house.try_deliver(
                motorcycle.x, motorcycle.y, motorcycle.cargo_list, controller.elapsed_time):
            # 선택한 한 집만 완료·정산한다. 완료된 집은 다음 선택에서 제외한다.
            total_revenue += house.reward
            print(
                f'[배송 완료] 배송지={house.house_id}, 화물={house.cargo_id}, '
                f'경과시간={controller.elapsed_time:.3f}초, '
                f'고객 기분={house.delivered_mood}, 보상={house.reward}원, '
                f'누적 수익={total_revenue}원'
            )
    previous_state = controller.state
    controller.evaluate(delivery_houses, total_revenue, motorcycle.cargo_list)
    if controller.state != StageState.DELIVERING:
        meteor_system.stop_waves()
    if controller.state != previous_state:
        print(f'[진행 상태] {controller.state.value}'
              + (f': {controller.failure_reason}' if controller.failure_reason else ''))
    # 이동·충돌과 배송 상태 판정 후, 복귀 중일 때만 중심 좌표로 도착을 판정한다.
    if controller.check_return(motorcycle.x, motorcycle.y, pickup_bounds):
        completed = sum(house.delivered for house in delivery_houses)
        print(f'[STAGE CLEAR] 배송={completed}/{len(delivery_houses)}, '
              f'최종 수익={total_revenue}원, 목표={controller.target_revenue}원')
    # 이번 프레임의 이동을 반영한 뒤 출력할 카메라 위치를 결정한다.
    camera.follow(motorcycle.x, motorcycle.y)


def draw():
    clear_canvas()
    game_world.render()
    meteor_system.draw(camera, cargo_debug_text.font, debug_view.enabled)
    if controller.state == StageState.WAITING:
        left, bottom, right, top = pickup_bounds
        left, bottom = camera.world_to_screen(left, bottom)
        right, top = camera.world_to_screen(right, top)
        draw_rectangle(round(left), round(bottom), round(right), round(top), 255, 200, 60)
    elif controller.state == StageState.RETURNING:
        left, bottom, right, top = pickup_bounds
        left, bottom = camera.world_to_screen(left, bottom)
        right, top = camera.world_to_screen(right, top)
        draw_rectangle(round(left), round(bottom), round(right), round(top), 100, 255, 120)
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
    cargo_debug_text.draw(motorcycle.cargo_list, total_revenue, delivery_houses, controller)
    target = current_delivery_target()
    cargo_debug_text.draw_delivery_hint(target)
    cargo_debug_text.draw_pickup_hint(controller.state == StageState.WAITING and in_pickup_zone())
    if controller.state == StageState.CLEAR:
        cargo_debug_text.draw_clear_result(delivery_houses, total_revenue, controller.target_revenue)
    if controller.state in (StageState.CLEAR, StageState.FAILED):
        cargo_debug_text.draw_restart_hint()
    minimap.draw(motorcycle, delivery_houses)
    if debug_view.enabled:
        meteor_system.draw_help(camera, cargo_debug_text.font)
    if paused:
        cargo_debug_text.draw_pause_menu(pause_selection)
    update_canvas()


def in_pickup_zone():
    left, bottom, right, top = pickup_bounds
    return left <= motorcycle.x <= right and bottom <= motorcycle.y <= top


def is_delivery_time_available():
    # 표시용 반올림·0 하한 대신 갱신된 실제 경과시간으로 경계를 비교한다.
    return controller.can_deliver()


def current_delivery_target():
    if not is_delivery_time_available():
        return None
    return select_delivery_target(
        delivery_houses, motorcycle.cargo_list, motorcycle.x, motorcycle.y,
    )


def set_paused(value):
    global paused, pause_selection, delivery_requested, space_pressed, restart_frame
    paused = value
    delivery_requested = False
    space_pressed = False
    motorcycle.pressed_keys.clear()
    if value:
        pause_selection = 0
    else:
        # 메뉴에서 유지한 주행·배달 키는 해제 후 다시 눌러야 적용한다.
        blocked_keys.update(held_keys)
        restart_frame = True


def activate_pause_selection():
    if pause_selection == 0:
        set_paused(False)
    elif pause_selection == 1:
        return True
    else:
        game_framework.quit()
    return False
