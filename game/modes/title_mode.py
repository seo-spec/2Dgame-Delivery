"""타이틀 배경과 메뉴 표시, 키보드·마우스 선택 및 플레이 진입."""

import os
from pathlib import Path

from pico2d import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEMOTION,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_UP,
    SDLK_DOWN,
    SDLK_RETURN,
    clear_canvas,
    draw_rectangle,
    get_canvas_height,
    get_canvas_width,
    get_events,
    load_image,
    update_canvas,
)

from game.core import game_framework
from game.ui.cached_font import CachedFont


BACKGROUND_PATH = (
    Path(__file__).resolve().parents[2]
    / 'assets/images/title/title_background_v1.png'
)
background = None
menu_font = None
selection = 0

MENU_ITEMS = ('시작', '옵션', '오토바이(캐릭터) 변경', '종료')
FONT_PATH = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/malgunbd.ttf'
MENU_FONT_SIZE = 28
MENU_SPACING = 76
TEXT_COLOR = (245, 238, 224)
SELECTED_COLOR = (255, 205, 104)


def init():
    global background, menu_font, selection
    selection = 0
    background = load_image(str(BACKGROUND_PATH))
    menu_font = CachedFont(FONT_PATH, MENU_FONT_SIZE)


def finish():
    global background, menu_font
    if menu_font is not None:
        menu_font.close()
    menu_font = None
    background = None


def handle_events():
    global selection
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type in (SDL_MOUSEMOTION, SDL_MOUSEBUTTONDOWN):
            mouse_y = get_canvas_height() - 1 - event.y
            for index in range(len(MENU_ITEMS)):
                left, bottom, right, top = menu_bounds(index)
                if left <= event.x <= right and bottom <= mouse_y <= top:
                    selection = index
                    if event.type == SDL_MOUSEBUTTONDOWN and event.button == 1:
                        if activate_selection():
                            return
                    break
            continue
        if event.type != SDL_KEYDOWN:
            continue
        if event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        if event.key == SDLK_UP:
            selection = (selection - 1) % len(MENU_ITEMS)
        elif event.key == SDLK_DOWN:
            selection = (selection + 1) % len(MENU_ITEMS)
        elif event.key == SDLK_RETURN:
            if activate_selection():
                return


def activate_selection():
    """선택 항목을 실행하고 화면 전환 또는 종료 여부를 반환한다."""
    if selection == 0:
        from game.modes import play_mode

        game_framework.change_mode(play_mode)
        return True
    if selection == 3:
        game_framework.quit()
        return True
    # 옵션과 오토바이(캐릭터) 변경은 추후 연결한다.
    return False


def menu_bounds(index):
    """그리기와 마우스 판정에 공통으로 사용하는 메뉴 영역."""
    width = get_canvas_width()
    height = get_canvas_height()
    left = round(width * 0.64) - 18
    right = round(width * 0.95)
    y = round(height * 0.60) - index * MENU_SPACING
    return left, y - 27, right, y + 27


def update():
    pass


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    background.draw(width / 2, height / 2, width, height)
    # 배경 오른쪽 벽면에 맞춰 메뉴를 배치한다.
    for index, label in enumerate(MENU_ITEMS):
        left, bottom, right, top = menu_bounds(index)
        y = (bottom + top) / 2
        active = index == selection
        if active:
            draw_rectangle(left, bottom, right, top, *SELECTED_COLOR)
            menu_font.draw(left + 18, y, '>', SELECTED_COLOR)
        color = SELECTED_COLOR if active else TEXT_COLOR
        menu_font.draw(left + 50, y, label, color)
    update_canvas()
