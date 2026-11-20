"""갈무리 폰트와 타이틀 메뉴 스타일을 사용하는 옵션 화면."""

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
MENU_FONT_SIZE = 24
MENU_ROW_HEIGHT = 56
BGM_VOLUME = 80
BACKGROUND_COLOR = (18, 31, 39)
TEXT_COLOR = (245, 238, 224)
SELECTED_COLOR = (255, 205, 104)
SELECTED_BACKGROUND = (25, 43, 52)


def init():
    global font
    font = CachedFont(FONT_PATH, MENU_FONT_SIZE)


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
    half_height = MENU_ROW_HEIGHT // 2
    return center_x - 160, center_y - half_height, center_x + 160, center_y + half_height


def update():
    pass


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    draw_rectangle(0, 0, width, height, *BACKGROUND_COLOR, filled=True)
    font.draw(round(width / 2 - 24), round(height * 0.7), '옵션', TEXT_COLOR)
    font.draw(round(width / 2 - 120), round(height * 0.52),
              f'BGM 음량  {BGM_VOLUME}%', TEXT_COLOR)
    left, bottom, right, top = return_bounds()
    center_y = round((bottom + top) / 2)
    draw_rectangle(left, bottom, right, top, *SELECTED_BACKGROUND, filled=True)
    draw_rectangle(left, bottom, left + 4, top, *SELECTED_COLOR, filled=True)
    font.draw(left + 18, center_y, '>', SELECTED_COLOR)
    font.draw(left + 48, center_y, '돌아가기', SELECTED_COLOR)
    update_canvas()
