"""플레이 객체 구성, 게임 월드 호출, 종료 입력 처리."""

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    get_events,
    get_canvas_width,
    get_canvas_height,
    update_canvas,
)

import game_framework
import game_world
from camera import Camera
from motorcycle import Motorcycle
from temporary_map import TemporaryMap


motorcycle = None
camera = None


def init():
    global motorcycle, camera
    game_world.clear()
    camera = Camera()
    game_world.add_object(TemporaryMap(camera), game_world.BACKGROUND)
    motorcycle = Motorcycle(get_canvas_width() / 2, get_canvas_height() / 2, camera)
    game_world.add_object(motorcycle, game_world.ACTORS)


def finish():
    global motorcycle, camera
    game_world.clear()
    motorcycle = None
    camera = None


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
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()
