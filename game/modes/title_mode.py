"""도트 도시와 순환 차량, 메뉴 입력 및 플레이 진입."""

from math import atan2, cos, hypot, pi, sin

from pico2d import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEMOTION,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_UP,
    SDLK_DOWN,
    SDLK_RETURN,
    SDL_SetTextureScaleMode,
    clear_canvas,
    draw_rectangle,
    get_canvas_height,
    get_canvas_width,
    get_events,
    load_image,
    update_canvas,
)

from game.core import game_framework
from game.config import title_animation
from game.config.fonts import FONT_PATH
from game.ui.cached_font import CachedFont


BACKGROUND_PATH = title_animation.FALLBACK_PATH
background = None
traffic = []
routes = []
elapsed = 0.0
menu_font = None
selection = 0

MENU_ITEMS = ('시작', '옵션', '오토바이(캐릭터) 변경', '종료')
MENU_FONT_SIZE = 24
MENU_SPACING = 68
MENU_LEFT = 804
MENU_RIGHT = 1216
MENU_FIRST_Y = 432
MENU_ROW_HEIGHT = 56
TEXT_COLOR = (245, 238, 224)
SELECTED_COLOR = (255, 205, 104)
SELECTED_BACKGROUND = (25, 43, 52)


def init():
    global background, menu_font, selection, elapsed
    selection = 0
    elapsed = 0.0
    traffic.clear()
    routes.clear()
    try:
        background = load_title_image(title_animation.BACKGROUND_PATH)
        sprites = {
            name: load_title_image(spec['path'])
            for name, spec in title_animation.SPRITES.items()
        }
        routes.extend(build_route(spec) for spec in title_animation.ROUTES)
        for name, route_index, phase in title_animation.VEHICLES:
            traffic.append((sprites[name], title_animation.SPRITES[name], route_index, phase))
    except OSError:
        # 불완전한 자산 묶음은 버리고 기존 완성 배경으로 진입한다.
        traffic.clear()
        routes.clear()
        background = None
        background = load_image(str(BACKGROUND_PATH))
    menu_font = CachedFont(FONT_PATH, MENU_FONT_SIZE)


def finish():
    global background, menu_font, elapsed
    if menu_font is not None:
        menu_font.close()
    menu_font = None
    background = None
    traffic.clear()
    routes.clear()
    elapsed = 0.0


def load_title_image(path):
    image = load_image(str(path))
    SDL_SetTextureScaleMode(image.texture, 0)  # SDL_ScaleModeNearest, 도트 경계 유지
    return image


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
    scale_x = get_canvas_width() / title_animation.REFERENCE_WIDTH
    scale_y = get_canvas_height() / title_animation.REFERENCE_HEIGHT
    y = MENU_FIRST_Y - index * MENU_SPACING
    return (
        round(MENU_LEFT * scale_x),
        round((y - MENU_ROW_HEIGHT / 2) * scale_y),
        round(MENU_RIGHT * scale_x),
        round((y + MENU_ROW_HEIGHT / 2) * scale_y),
    )


def update():
    global elapsed
    elapsed += min(game_framework.frame_time, title_animation.MAX_FRAME_TIME)


def build_route(spec):
    """둥근 사각 경로의 선분과 길이를 초기화 시 한 번 계산한다."""
    left, top, right, bottom = spec['rect']
    radius = title_animation.CORNER_RADIUS
    corners = (
        (right - radius, top + radius, -pi / 2),
        (right - radius, bottom - radius, 0),
        (left + radius, bottom - radius, pi / 2),
        (left + radius, top + radius, pi),
    )
    points = []
    for center_x, center_y, start_angle in corners:
        for step in range(9):
            angle = start_angle + step * pi / 16
            points.append((center_x + radius * cos(angle), center_y + radius * sin(angle)))
    if not spec['clockwise']:
        points.reverse()
    segments = []
    for start, end in zip(points, points[1:] + points[:1]):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = hypot(dx, dy)
        segments.append((start, dx, dy, length, atan2(-dy, dx) - pi / 2))
    return segments, sum(segment[3] for segment in segments)


def vehicle_pose(route_index, phase):
    segments, total_length = routes[route_index]
    distance = (elapsed * title_animation.ROUTES[route_index]['speed'] + phase * total_length) % total_length
    for start, dx, dy, length, angle in segments:
        if distance <= length:
            ratio = distance / length
            return start[0] + dx * ratio, start[1] + dy * ratio, angle
        distance -= length
    start, _, _, _, angle = segments[0]
    return start[0], start[1], angle


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    background.draw(width / 2, height / 2, width, height)
    scale_x = width / title_animation.REFERENCE_WIDTH
    scale_y = height / title_animation.REFERENCE_HEIGHT
    for image, spec, route_index, phase in traffic:
        x, y, angle = vehicle_pose(route_index, phase)
        sprite_width, sprite_height = spec['size']
        image.clip_composite_draw(
            *spec['clip'], angle, '', round(x * scale_x), round(height - y * scale_y),
            sprite_width * scale_x, sprite_height * scale_y,
        )
    # 오른쪽 창고 지붕의 어두운 영역에 메뉴를 배치한다.
    for index, label in enumerate(MENU_ITEMS):
        left, bottom, right, top = menu_bounds(index)
        y = (bottom + top) / 2
        active = index == selection
        if active:
            draw_rectangle(left, bottom, right, top, *SELECTED_BACKGROUND, filled=True)
            draw_rectangle(left, bottom, round(left + 4 * scale_x), top,
                           *SELECTED_COLOR, filled=True)
            menu_font.draw(round(left + 18 * scale_x), y, '>', SELECTED_COLOR)
        color = SELECTED_COLOR if active else TEXT_COLOR
        menu_font.draw(round(left + 48 * scale_x), y, label, color)
    update_canvas()
