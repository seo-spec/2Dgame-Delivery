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
# clip은 투명 여백을 제외한 왼쪽 아래 원점 영역이며 두 차종의 바닥을 맞춘다.
MOTORCYCLES = (
    ('기본 오토바이', PREVIEW_PATH, (82, 53, 1343, 862)),
    ('블루 바이크', PREVIEW_PATH.with_name('motorcycle_blue_side_v1.png'), (79, 35, 1369, 887)),
)
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
    for _, image_path, _ in MOTORCYCLES:
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


def draw_motorcycle(image_path, clip, x, bottom, max_width, max_height):
    """차종별 투명 여백을 제외하고 같은 바닥선과 표시 영역에 맞춘다."""
    image = preview_images[image_path]
    clip_width, clip_height = clip[2:]
    scale = min(max_width / clip_width, max_height / clip_height)
    draw_width, draw_height = clip_width * scale, clip_height * scale
    image.clip_draw(*clip, x, bottom + draw_height / 2, draw_width, draw_height)


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
    name, image_path, clip = MOTORCYCLES[selection]
    draw_motorcycle(image_path, clip, width * 0.36, preview_bottom + 40,
                    width * 0.46, preview_top - preview_bottom - 64)
    font.draw(round(width * 0.71), round(preview_y + 24), name, TEXT_COLOR)
    if image_path == PREVIEW_PATH:
        label_font.draw(round(width * 0.71), round(preview_y - 22),
                        '현재 사용 중', SELECTED_COLOR)

    draw_rectangle(32, 24, width - 32, 226, *PANEL_COLOR, filled=True)
    label_font.draw(56, 204, '오토바이 목록', MUTED_COLOR)
    for index, (name, image_path, clip) in enumerate(MOTORCYCLES):
        left, bottom, right, top = card_bounds(index)
        draw_rectangle(left, bottom, right, top, *CARD_COLOR, filled=True)
        color = SELECTED_COLOR if index == selection else MUTED_COLOR
        draw_rectangle(left, bottom, right, top, *color)
        draw_motorcycle(image_path, clip, (left + right) / 2, bottom + 46, 144, 76)
        label_font.draw(left + 16, bottom + 24, name, color)
    update_canvas()
