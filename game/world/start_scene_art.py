"""출발 화면에만 적용하는 v2 자산·팔레트와 초기화 전용 텍스처 로더."""

from importlib import import_module
from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parents[2] / 'assets/images/title_match_v2'
GROUND_BOUNDS = (250, 90, 1250, 810)
GROUND_FADE = 48
# 종류와 위치를 함께 지정해 다른 구역의 공통 v1 자산은 유지한다.
ASSETS = {
    ('delivery_depot', (750, 150)): ('depot_title_v2.png', (320, 320)),
    ('cafe', (450, 150)): ('cafe_title_v2.png', (280, 280)),
    ('tree', (900, 600)): ('tree_title_v2.png', (110, 110)),
    ('bench', (630, 580)): ('bench_title_v2.png', (110, 110)),
    ('recycling_bin', (700, 580)): ('bin_title_v2.png', (32, 32)),
    ('mailbox', (620, 330)): ('mailbox_title_v2.png', (64, 64)),
    ('planter', (570, 650)): ('planter_title_v2.png', (120, 120)),
}
TINTS = {
    'grass': (130, 150, 90),
    'asphalt': (69, 75, 73),
    'sidewalk': (200, 190, 165),
    'yard': (174, 169, 154),
    'marking': (229, 215, 185),
}


def ground_strength(wx, wy):
    left, bottom, right, top = GROUND_BOUNDS
    if not (left < wx < right - 1 and bottom < wy < top - 1):
        return 0.0
    edge = min(wx - left, right - 1 - wx, wy - bottom, top - 1 - wy)
    ratio = max(0.0, min(1.0, edge / GROUND_FADE))
    return ratio * ratio * (3 - 2 * ratio)


def ground_tint(wx, wy, color, material, base=None):
    """기존 색의 작은 재질 차이를 남겨 지정 범위 안에서만 섞는다."""
    strength = ground_strength(wx, wy)
    if strength <= 0:
        return color
    target = TINTS[material]
    base = color if base is None else base
    return tuple(round(channel + strength * (target[index] - base[index]))
                 for index, channel in enumerate(color))


def load_compact_image(filename, size):
    """PNG는 보존하고 초기화 때 CPU 면을 줄여 필요한 GPU 텍스처만 만든다."""
    pico = import_module('pico2d.pico2d')
    try:
        sdl = import_module('sdl2')
        image_api = import_module('sdl2.sdlimage')
    except ImportError as error:
        raise OSError('기존 SDL 이미지 바인딩을 사용할 수 없습니다.') from error
    required = ('SDL_CreateRGBSurfaceWithFormat', 'SDL_BlitScaled',
                'SDL_SetSurfaceBlendMode', 'SDL_CreateTextureFromSurface', 'SDL_FreeSurface')
    if not all(hasattr(sdl, name) for name in required):
        raise OSError('v2 이미지 초기화에 필요한 SDL 기능이 없습니다.')
    source = image_api.IMG_Load(str(ASSET_DIR / filename).encode('utf-8'))
    if not source:
        raise OSError(f'v2 이미지를 읽지 못했습니다: {filename}')
    surface = None
    texture = None
    try:
        surface = sdl.SDL_CreateRGBSurfaceWithFormat(0, size[0], size[1], 32,
                                                    sdl.SDL_PIXELFORMAT_ABGR8888)
        if not surface:
            raise OSError(f'v2 이미지 작업 면 생성 실패: {filename}')
        if (sdl.SDL_SetSurfaceBlendMode(source, sdl.SDL_BLENDMODE_NONE) != 0
                or sdl.SDL_BlitScaled(source, None, surface, None) != 0):
            raise OSError(f'v2 이미지 축소 실패: {filename}')
        texture = sdl.SDL_CreateTextureFromSurface(pico.renderer, surface)
        if not texture:
            raise OSError(f'v2 이미지 전송 실패: {filename}')
        if (sdl.SDL_SetTextureBlendMode(texture, sdl.SDL_BLENDMODE_BLEND) != 0
                or sdl.SDL_SetTextureScaleMode(texture, 0) != 0):
            raise OSError(f'v2 이미지 출력 설정 실패: {filename}')
        return pico.Image(texture)
    except Exception:
        if texture:
            sdl.SDL_DestroyTexture(texture)
        raise
    finally:
        if surface:
            sdl.SDL_FreeSurface(surface)
        sdl.SDL_FreeSurface(source)
