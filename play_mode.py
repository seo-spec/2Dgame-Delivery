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
from collision import move_circle
from motorcycle import Motorcycle
from road_map import RoadMap, create_decorations


motorcycle = None
camera = None
collision_preview_house = None


def init():
    global motorcycle, camera, collision_preview_house
    game_world.clear()
    collision_preview_house = None
    camera = Camera()
    road_map = RoadMap(camera)
    game_world.add_object(road_map, game_world.BACKGROUND)
    for decoration in create_decorations(camera, road_map.config):
        game_world.add_object(decoration, game_world.BACKGROUND)
        if decoration.object_id == 'collision_preview_house':
            collision_preview_house = decoration
    motorcycle = Motorcycle(*road_map.spawn, camera)
    game_world.add_object(motorcycle, game_world.ACTORS)
    camera.follow(motorcycle.x, motorcycle.y)


def finish():
    global motorcycle, camera, collision_preview_house
    game_world.clear()
    motorcycle = None
    camera = None
    collision_preview_house = None


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
    if collision_preview_house is not None:
        bounds = collision_preview_house.get_collision_bounds()
        if bounds is not None:
            motorcycle.x, motorcycle.y = move_circle(
                previous_x, previous_y, motorcycle.x, motorcycle.y,
                motorcycle.collision_radius, bounds,
            )
    # 이번 프레임의 이동을 반영한 뒤 출력할 카메라 위치를 결정한다.
    camera.follow(motorcycle.x, motorcycle.y)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()
