"""큰 오토바이 미리보기와 하단 선택 카드로 구성한 차고 화면."""

from pico2d import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_RETURN,
    clear_canvas,
    draw_rectangle,
    get_canvas_height,
    get_canvas_width,
    get_events,
    load_image,
    update_canvas,
)

from game.config.fonts import FONT_PATH
from game.config import motorcycle_catalog
from game.core import game_framework
from game.ui.cached_font import CachedFont


font = None
label_font = None
preview_images = {}
selection = 0
MOTORCYCLES = tuple(motorcycle_catalog.MOTORCYCLES.values())
PREVIEW_BOTTOM = 250
BACKGROUND_COLOR = (18, 31, 39)
PANEL_COLOR = (25, 43, 52)
CARD_COLOR = (32, 53, 65)
TEXT_COLOR = (245, 238, 224)
MUTED_COLOR = (157, 179, 188)
SELECTED_COLOR = (255, 205, 104)
STAT_PANEL_COLOR = (14, 26, 35)
STAT_BORDER_COLOR = (83, 134, 155)
STAT_TRACK_COLOR = (38, 61, 75)
STAT_FILL_COLOR = (96, 183, 220)
# 비교용 막대의 공통 상한. 안정성 100%는 흔들림 배율 1.0인 기본형이다.
STAT_SPEED_MAX = 300.0
STAT_STABILITY_MAX = 200.0


def init():
    global font, label_font, selection
    font = CachedFont(FONT_PATH, 24)
    label_font = CachedFont(FONT_PATH, 18)
    preview_images.clear()
    for motorcycle in MOTORCYCLES:
        image_path = motorcycle['preview_path']
        if image_path not in preview_images:
            preview_images[image_path] = load_image(str(image_path))
    current_id = motorcycle_catalog.get_selected_motorcycle()['id']
    selection = next(index for index, motorcycle in enumerate(MOTORCYCLES)
                     if motorcycle['id'] == current_id)


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
            elif event.key == SDLK_RETURN:
                use_selected_motorcycle()
        if event.type == SDL_MOUSEBUTTONDOWN and event.button == 1:
            mouse_y = get_canvas_height() - 1 - event.y
            left, bottom, right, top = back_bounds()
            if left <= event.x <= right and bottom <= mouse_y <= top:
                return_to_title()
                return
            left, bottom, right, top = use_bounds()
            if left <= event.x <= right and bottom <= mouse_y <= top:
                use_selected_motorcycle()
                return
            for index in range(len(MOTORCYCLES)):
                left, bottom, right, top = card_bounds(index)
                if left <= event.x <= right and bottom <= mouse_y <= top:
                    selection = index
                    break


def use_selected_motorcycle():
    motorcycle = MOTORCYCLES[selection]
    if motorcycle['render'] is None:
        return
    motorcycle_catalog.selected_motorcycle_id = motorcycle['id']


def use_bounds():
    center_x = round(get_canvas_width() * 0.36)
    center_y = PREVIEW_BOTTOM + 36
    return center_x - 88, center_y - 24, center_x + 88, center_y + 24


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


def draw_stat_row(label, value, ratio, left, right, y):
    label_font.draw(left, y, label, TEXT_COLOR)
    label_font.draw(right - 96, y, value, SELECTED_COLOR)
    bar_bottom, bar_top = y - 26, y - 16
    draw_rectangle(left, bar_bottom, right, bar_top, *STAT_TRACK_COLOR, filled=True)
    fill_width = round((right - left) * max(0.0, min(1.0, ratio)))
    if fill_width > 0:
        draw_rectangle(left, bar_bottom, left + fill_width, bar_top,
                       *STAT_FILL_COLOR, filled=True)


def draw_stats_panel(stats, width, preview_y):
    left, right = round(width * 0.69), width - 48
    top = round(preview_y - 48)
    bottom = PREVIEW_BOTTOM + 16
    draw_rectangle(left, bottom, right, top, *STAT_PANEL_COLOR, filled=True)
    draw_rectangle(left, bottom, right, top, *STAT_BORDER_COLOR)
    speed = stats['max_speed']
    stability = 100.0 / stats['cargo_shake_multiplier']
    draw_stat_row('최고속도', f'{speed:.0f} px/s', speed / STAT_SPEED_MAX,
                  left + 16, right - 16, top - 18)
    draw_stat_row('화물 안정성', f'{stability:.0f}%', stability / STAT_STABILITY_MAX,
                  left + 16, right - 16, top - 76)


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
    preview_bottom, preview_top = PREVIEW_BOTTOM, height - 112
    preview_y = (preview_bottom + preview_top) / 2
    draw_rectangle(32, preview_bottom, width - 32, preview_top, *PANEL_COLOR, filled=True)
    draw_rectangle(64, preview_bottom + 76, round(width * 0.64),
                   preview_bottom + 80, *MUTED_COLOR, filled=True)
    motorcycle = MOTORCYCLES[selection]
    draw_motorcycle(motorcycle['preview_path'], motorcycle['preview_clip'],
                    width * 0.36, preview_bottom + 80,
                    width * 0.46, preview_top - preview_bottom - 104)
    font.draw(round(width * 0.71), round(preview_y + 24), motorcycle['name'], TEXT_COLOR)
    if motorcycle['id'] == motorcycle_catalog.get_selected_motorcycle()['id']:
        label_font.draw(round(width * 0.71), round(preview_y - 22),
                        '현재 사용 중', SELECTED_COLOR)
    elif motorcycle['render'] is not None:
        left, bottom, right, top = use_bounds()
        draw_rectangle(left, bottom, right, top, *CARD_COLOR, filled=True)
        draw_rectangle(left, bottom, right, top, *SELECTED_COLOR)
        font.draw(round((left + right) / 2 - 48), round((bottom + top) / 2),
                  '사용하기', SELECTED_COLOR)
    else:
        label_font.draw(round(width * 0.71), round(preview_y - 22),
                        '미리보기', MUTED_COLOR)

    stats = motorcycle.get('stats')
    if stats is not None:
        draw_stats_panel(stats, width, preview_y)

    draw_rectangle(32, 24, width - 32, 226, *PANEL_COLOR, filled=True)
    label_font.draw(56, 204, '오토바이 목록', MUTED_COLOR)
    for index, motorcycle in enumerate(MOTORCYCLES):
        left, bottom, right, top = card_bounds(index)
        draw_rectangle(left, bottom, right, top, *CARD_COLOR, filled=True)
        color = SELECTED_COLOR if index == selection else MUTED_COLOR
        draw_rectangle(left, bottom, right, top, *color)
        draw_motorcycle(motorcycle['preview_path'], motorcycle['preview_clip'],
                        (left + right) / 2, bottom + 46, 144, 76)
        label_font.draw(left + 16, bottom + 24, motorcycle['name'], color)
    update_canvas()
