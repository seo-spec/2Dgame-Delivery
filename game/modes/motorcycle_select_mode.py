"""큰 오토바이 미리보기와 하단 선택 카드로 구성한 차고 화면."""

from pathlib import Path

from pico2d import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_LEFT,
    SDLK_RIGHT,
    clear_canvas,
    draw_rectangle,
    get_canvas_height,
    get_canvas_width,
    get_events,
    load_image,
    update_canvas,
)

from game.config.fonts import FONT_PATH
from game.core import game_framework
from game.ui.cached_font import CachedFont


font = None
label_font = None
preview_images = {}
selection = 0
PREVIEW_PATH = Path(__file__).resolve().parents[2] / 'assets/images/motorcycle/motorcycle_side_v1.png'
MOTORCYCLES = (('기본 오토바이', PREVIEW_PATH),)
BACKGROUND_COLOR = (18, 31, 39)
PANEL_COLOR = (25, 43, 52)
CARD_COLOR = (32, 53, 65)
TEXT_COLOR = (245, 238, 224)
MUTED_COLOR = (157, 179, 188)
SELECTED_COLOR = (255, 205, 104)


def init():
    global font, label_font, selection
    font = CachedFont(FONT_PATH, 24)
    label_font = CachedFont(FONT_PATH, 18)
    preview_images.clear()
    for _, image_path in MOTORCYCLES:
        if image_path not in preview_images:
            preview_images[image_path] = load_image(str(image_path))
    selection = 0


def finish():
    global font, label_font
    if font is not None:
        font.close()
    font = None
    if label_font is not None:
        label_font.close()
    label_font = None
    preview_images.clear()


def handle_events():
    global selection
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                return_to_title()
                return
            if event.key == SDLK_LEFT:
                selection = (selection - 1) % len(MOTORCYCLES)
            elif event.key == SDLK_RIGHT:
                selection = (selection + 1) % len(MOTORCYCLES)
        if event.type == SDL_MOUSEBUTTONDOWN and event.button == 1:
            mouse_y = get_canvas_height() - 1 - event.y
            left, bottom, right, top = back_bounds()
            if left <= event.x <= right and bottom <= mouse_y <= top:
                return_to_title()
                return
            for index in range(len(MOTORCYCLES)):
                left, bottom, right, top = card_bounds(index)
                if left <= event.x <= right and bottom <= mouse_y <= top:
                    selection = index
                    break


def return_to_title():
    from game.modes import title_mode

    game_framework.change_mode(title_mode)


def back_bounds():
    height = get_canvas_height()
    return 32, height - 76, 208, height - 24


def card_bounds(index):
    left = 56 + index * 184
    return left, 48, left + 168, 180


def draw_motorcycle(image_path, x, y, max_width, max_height):
    """사이드 뷰 이미지의 비율을 유지해 미리보기 영역 안에 맞춘다."""
    image = preview_images[image_path]
    scale = min(max_width / image.w, max_height / image.h)
    image.draw(x, y, image.w * scale, image.h * scale)


def update():
    pass


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    draw_rectangle(0, 0, width, height, *BACKGROUND_COLOR, filled=True)
    draw_rectangle(0, height - 96, width, height, *PANEL_COLOR, filled=True)
    font.draw(round(width / 2 - 78), height - 50, '오토바이 변경', TEXT_COLOR)
    left, bottom, right, top = back_bounds()
    draw_rectangle(left, bottom, right, top, *CARD_COLOR, filled=True)
    font.draw(left + 18, round((bottom + top) / 2), '< 돌아가기', TEXT_COLOR)

    # 위쪽은 큰 미리보기, 아래쪽은 보유 오토바이 카드 목록이다.
    preview_bottom, preview_top = 250, height - 112
    preview_y = (preview_bottom + preview_top) / 2
    draw_rectangle(32, preview_bottom, width - 32, preview_top, *PANEL_COLOR, filled=True)
    draw_rectangle(64, preview_bottom + 36, round(width * 0.64),
                   preview_bottom + 40, *MUTED_COLOR, filled=True)
    name, image_path = MOTORCYCLES[selection]
    draw_motorcycle(image_path, width * 0.36, preview_y,
                    width * 0.46, preview_top - preview_bottom - 64)
    font.draw(round(width * 0.71), round(preview_y + 24), name, TEXT_COLOR)
    label_font.draw(round(width * 0.71), round(preview_y - 22),
                    '현재 사용 중', SELECTED_COLOR)

    draw_rectangle(32, 24, width - 32, 226, *PANEL_COLOR, filled=True)
    label_font.draw(56, 204, '오토바이 목록', MUTED_COLOR)
    for index, (name, image_path) in enumerate(MOTORCYCLES):
        left, bottom, right, top = card_bounds(index)
        draw_rectangle(left, bottom, right, top, *CARD_COLOR, filled=True)
        color = SELECTED_COLOR if index == selection else MUTED_COLOR
        draw_rectangle(left, bottom, right, top, *color)
        draw_motorcycle(image_path, (left + right) / 2, bottom + 80, 144, 76)
        label_font.draw(left + 16, bottom + 24, name, color)
    update_canvas()
