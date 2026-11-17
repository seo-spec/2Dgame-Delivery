"""타이틀 배경 표시와 입력 처리를 위한 기본 모드."""

from pathlib import Path

from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    get_canvas_height,
    get_canvas_width,
    get_events,
    load_image,
    update_canvas,
)

from game.core import game_framework


BACKGROUND_PATH = (
    Path(__file__).resolve().parents[2]
    / 'assets/images/title/title_background_v1.png'
)
background = None

# 추가 예정 메뉴: 시작, 옵션, 오토바이(캐릭터) 변경, 종료.


def init():
    global background
    background = load_image(str(BACKGROUND_PATH))


def finish():
    global background
    background = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return


def update():
    pass


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    background.draw(width / 2, height / 2, width, height)
    update_canvas()
