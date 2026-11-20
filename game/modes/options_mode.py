"""옵션 화면의 기본 진입과 화면 표시."""

from pico2d import (
    SDL_QUIT,
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


def update():
    pass


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    draw_rectangle(0, 0, width, height, 25, 43, 52, filled=True)
    font.draw(round(width / 2 - 24), round(height * 0.7), '옵션', (245, 238, 224))
    font.draw(round(width / 2 - 48), round(height * 0.4), '돌아가기', (245, 238, 224))
    update_canvas()
