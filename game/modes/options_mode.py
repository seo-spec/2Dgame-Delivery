"""옵션 화면의 기본 진입과 화면 표시."""

from pico2d import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_RETURN,
    clear_canvas,
    draw_rectangle,
    get_canvas_height,
    get_canvas_width,
    get_events,
    update_canvas,
)

from game.config.fonts import FONT_PATH
from game.core import game_framework
from game.ui.cached_font import CachedFont


font = None


def init():
    global font
    font = CachedFont(FONT_PATH, 24)


def finish():
    global font
    if font is not None:
        font.close()
    font = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN and event.key in (SDLK_RETURN, SDLK_ESCAPE):
            return_to_title()
            return
        if event.type == SDL_MOUSEBUTTONDOWN and event.button == 1:
            left, bottom, right, top = return_bounds()
            mouse_y = get_canvas_height() - 1 - event.y
            if left <= event.x <= right and bottom <= mouse_y <= top:
                return_to_title()
                return


def return_to_title():
    from game.modes import title_mode

    game_framework.change_mode(title_mode)


def return_bounds():
    """돌아가기 표시와 마우스 판정이 공유하는 영역."""
    center_x = round(get_canvas_width() / 2)
    center_y = round(get_canvas_height() * 0.4)
    return center_x - 100, center_y - 28, center_x + 100, center_y + 28


def update():
    pass


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    draw_rectangle(0, 0, width, height, 25, 43, 52, filled=True)
    font.draw(round(width / 2 - 24), round(height * 0.7), '옵션', (245, 238, 224))
    left, bottom, right, top = return_bounds()
    font.draw(round((left + right) / 2 - 48), round((bottom + top) / 2),
              '돌아가기', (245, 238, 224))
    update_canvas()
