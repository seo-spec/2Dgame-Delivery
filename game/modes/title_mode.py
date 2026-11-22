"""도트 도시와 순환 차량, 메뉴 입력 및 플레이 진입."""

from math import cos, hypot, pi, sin
import ctypes
from importlib import import_module

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
    SDL_SetTextureColorMod,
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


_pico = import_module('pico2d.pico2d')
BACKGROUND_PATH = title_animation.FALLBACK_PATH
background = None
streetlamp = None
light_glow = None
traffic = []
routes = []
elapsed = 0.0
menu_font = None
title_font = None
selection = 0

GAME_TITLE = 'ALLEYWAY'
GAME_SUBTITLE = 'QUICK DELIVERY'
TITLE_FONT_SIZE = 48
TITLE_X = 852
TITLE_Y = 525
SUBTITLE_Y = 480
MENU_ITEMS = ('시작', '옵션', '오토바이(캐릭터) 변경', '종료')
MENU_FONT_SIZE = 24
MENU_SPACING = 68
MENU_LEFT = 804
MENU_RIGHT = 1216
MENU_FIRST_Y = 400
MENU_ROW_HEIGHT = 56
TEXT_COLOR = (245, 238, 224)
SELECTED_COLOR = (255, 205, 104)
SELECTED_BACKGROUND = (25, 43, 52)
TITLE_SHADOW_COLOR = (12, 23, 30)


def init():
    global background, streetlamp, light_glow, menu_font, title_font, selection, elapsed
    selection = 0
    elapsed = 0.0
    streetlamp = None
    light_glow = None
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
    if traffic:
        try:
            streetlamp = load_title_image(title_animation.STREETLAMP_PATH)
        except OSError:
            streetlamp = None
    if streetlamp is not None:
        light_glow = create_light_glow()
    menu_font = CachedFont(FONT_PATH, MENU_FONT_SIZE)
    title_font = CachedFont(FONT_PATH, TITLE_FONT_SIZE)


def finish():
    global background, streetlamp, light_glow, menu_font, title_font, elapsed
    if menu_font is not None:
        menu_font.close()
    if title_font is not None:
        title_font.close()
    menu_font = None
    title_font = None
    background = None
    streetlamp = None
    light_glow = None
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
    if selection == 1:
        from game.modes import options_mode

        game_framework.change_mode(options_mode)
        return True
    if selection == 2:
        from game.modes import motorcycle_select_mode

        game_framework.change_mode(motorcycle_select_mode)
        return True
    if selection == 3:
        game_framework.quit()
        return True
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


def daylight_color():
    """시간대 사이의 색을 부드럽게 보간한다. 메뉴에는 적용하지 않는다."""
    phase = (elapsed % title_animation.DAY_NIGHT_CYCLE_SECONDS) / title_animation.DAY_NIGHT_CYCLE_SECONDS
    keyframes = title_animation.DAY_NIGHT_COLORS
    for (start, start_color), (end, end_color) in zip(keyframes, keyframes[1:]):
        if phase <= end:
            ratio = (phase - start) / (end - start)
            blend = ratio * ratio * (3 - 2 * ratio)
            return tuple(round(a + (b - a) * blend) for a, b in zip(start_color, end_color))
    return keyframes[-1][1]


def streetlamp_intensity():
    phase = (elapsed % title_animation.DAY_NIGHT_CYCLE_SECONDS) / title_animation.DAY_NIGHT_CYCLE_SECONDS
    levels = title_animation.STREETLAMP_LIGHT_LEVELS
    for (start, start_level), (end, end_level) in zip(levels, levels[1:]):
        if phase <= end:
            ratio = (phase - start) / (end - start)
            blend = ratio * ratio * (3 - 2 * ratio)
            return start_level + (end_level - start_level) * blend
    return levels[-1][1]


def create_light_glow():
    """밝은 중심과 옅은 원형 번짐을 가진 작은 공유 텍스처를 만든다."""
    size = 64
    pixels = bytearray()
    for y in range(size):
        for x in range(size):
            radius = hypot(x + 0.5 - size / 2, y + 0.5 - size / 2) / (size / 2)
            falloff = max(0.0, 1.0 - radius)
            # 중심부는 등불 유리의 발광, 바깥쪽은 약한 빛 번짐이다.
            core = max(0.0, 1.0 - radius / 0.16)
            alpha = round(max(255 * core, 80 * falloff * falloff))
            pixels.extend((*title_animation.STREETLAMP_GLOW_COLOR, alpha))
    texture = _pico.SDL_CreateTexture(
        _pico.renderer, _pico.SDL_PIXELFORMAT_ABGR8888,
        _pico.SDL_TEXTUREACCESS_STATIC, size, size,
    )
    if not texture:
        return None
    buffer = ctypes.create_string_buffer(bytes(pixels))
    updated = _pico.SDL_UpdateTexture(texture, None, buffer, size * 4)
    blended = _pico.SDL_SetTextureBlendMode(texture, _pico.SDL_BLENDMODE_ADD)
    if updated != 0 or blended != 0:
        _pico.SDL_DestroyTexture(texture)
        return None
    return _pico.Image(texture)


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
            points.append((center_x + radius * cos(angle),
                           center_y + radius * sin(angle), -angle - pi))
    if not spec['clockwise']:
        points = [(x, y, angle + pi) for x, y, angle in reversed(points)]
    segments = []
    for start, end in zip(points, points[1:] + points[:1]):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = hypot(dx, dy)
        # 최단 각도 차이를 저장해 직선·곡선 경계에서도 방향이 연속적으로 바뀐다.
        angle_delta = (end[2] - start[2] + pi) % (2 * pi) - pi
        segments.append((start[:2], dx, dy, length, start[2], angle_delta))
    return segments, sum(segment[3] for segment in segments)


def vehicle_pose(route_index, phase):
    segments, total_length = routes[route_index]
    distance = (elapsed * title_animation.ROUTES[route_index]['speed'] + phase * total_length) % total_length
    for start, dx, dy, length, angle, angle_delta in segments:
        if distance <= length:
            ratio = distance / length
            return (start[0] + dx * ratio, start[1] + dy * ratio,
                    angle + angle_delta * ratio)
        distance -= length
    start, _, _, _, angle, _ = segments[0]
    return start[0], start[1], angle


def draw():
    clear_canvas()
    width = get_canvas_width()
    height = get_canvas_height()
    ambient_color = daylight_color()
    SDL_SetTextureColorMod(background.texture, *ambient_color)
    background.draw(width / 2, height / 2, width, height)
    scale_x = width / title_animation.REFERENCE_WIDTH
    scale_y = height / title_animation.REFERENCE_HEIGHT
    if streetlamp is not None:
        SDL_SetTextureColorMod(streetlamp.texture, *ambient_color)
        lamp_width, lamp_height = title_animation.STREETLAMP_SIZE
        for x, bottom in title_animation.STREETLAMP_POSITIONS:
            streetlamp.clip_draw(
                *title_animation.STREETLAMP_CLIP,
                round(x * scale_x), round(height - (bottom - lamp_height / 2) * scale_y),
                lamp_width * scale_x, lamp_height * scale_y,
            )
    for image, spec, route_index, phase in traffic:
        SDL_SetTextureColorMod(image.texture, *ambient_color)
        x, y, angle = vehicle_pose(route_index, phase)
        sprite_width, sprite_height = spec['size']
        image.clip_composite_draw(
            *spec['clip'], angle, '', round(x * scale_x), round(height - y * scale_y),
            sprite_width * scale_x, sprite_height * scale_y,
        )
    if light_glow is not None:
        strength = streetlamp_intensity()
        if strength > 0:
            _pico.SDL_SetTextureAlphaMod(light_glow.texture, round(255 * strength))
            glow_size = title_animation.STREETLAMP_GLOW_SIZE
            for x, y in title_animation.STREETLAMP_GLOW_POSITIONS:
                light_glow.draw(
                    round(x * scale_x),
                    round(height - y * scale_y),
                    glow_size * scale_x, glow_size * scale_y,
                )
    title_x = round(TITLE_X * scale_x)
    title_y = round(TITLE_Y * scale_y)
    subtitle_y = round(SUBTITLE_Y * scale_y)
    title_font.draw(title_x + 2, title_y - 3, GAME_TITLE, TITLE_SHADOW_COLOR)
    title_font.draw(title_x, title_y, GAME_TITLE, TEXT_COLOR)
    menu_font.draw(title_x + 2, subtitle_y - 2, GAME_SUBTITLE, TITLE_SHADOW_COLOR)
    menu_font.draw(title_x, subtitle_y, GAME_SUBTITLE, SELECTED_COLOR)
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
