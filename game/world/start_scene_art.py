"""맵 전체의 공통 v2 자산·입구 변형·팔레트와 초기화 전용 텍스처 로더."""

from importlib import import_module
from functools import lru_cache
import json
from pathlib import Path

from game.config import settings


ASSET_DIR = Path(__file__).resolve().parents[2] / 'assets/images/title_match_v2'
_frame_data = None
GROUND_BOUNDS = (0, 0, settings.WORLD_WIDTH, settings.WORLD_HEIGHT)
# 같은 종류는 최대 표시 크기로 한 번만 준비하고 기존 개별 크기로 출력한다.
COMMON_ASSETS = {
    'delivery_depot': ('depot_title_v2.png', (320, 320)),
    'cafe': ('cafe_title_v2.png', (280, 280)),
    'building': ('house_title_v2.png', (280, 280)),
    'blue_house': ('blue_house_title_v2.png', (300, 300)),
    'shop': ('shop_title_v2.png', (320, 320)),
    'apartment': ('apartment_title_v2.png', (300, 300)),
    'tree': ('tree_title_v2.png', (140, 140)),
    'bench': ('bench_title_v2.png', (110, 110)),
    'recycling_bin': ('bin_title_v2.png', (32, 32)),
    'mailbox': ('mailbox_title_v2.png', (64, 64)),
    'planter': ('planter_title_v2.png', (120, 120)),
    'bus_stop': ('bus_stop_title_v2.png', (230, 154)),
    'fountain': ('fountain_title_v2.png', (230, 230)),
}
ENTRANCE_ASSETS = {
    'collision_preview_house': ('house_entrance_title_v2.png', (280, 280)),
    'delivery_house_b': ('house_entrance_title_v2.png', (280, 280)),
    'delivery_house_c': ('blue_house_entrance_title_v2.png', (300, 300)),
    'delivery_house_d': ('shop_entrance_title_v2.png', (320, 320)),
    'delivery_house_e': ('shop_entrance_title_v2.png', (320, 320)),
}


def get_asset_spec(asset, object_id):
    # 실제로 남쪽 입구를 적용해 둔 다섯 건물에만 입구 변형을 사용한다.
    return ENTRANCE_ASSETS.get(object_id, COMMON_ASSETS.get(asset))


TINTS = {
    'grass': (130, 150, 90),
    'asphalt': (69, 75, 73),
    'sidewalk': (200, 190, 165),
    'yard': (174, 169, 154),
    'marking': (229, 215, 185),
}


def ground_strength(wx, wy):
    left, bottom, right, top = GROUND_BOUNDS
    return 1.0 if left <= wx < right and bottom <= wy < top else 0.0


def ground_tint(wx, wy, color, material, base=None):
    """기존 색의 작은 재질 차이를 남겨 지정 범위 안에서만 섞는다."""
    strength = ground_strength(wx, wy)
    if strength <= 0:
        return color
    base = color if base is None else base
    if strength == 1.0:
        return _solid_ground_tint(color, material, base)
    target = TINTS[material]
    return tuple(round(channel + strength * (target[index] - base[index]))
                 for index, channel in enumerate(color))


@lru_cache(maxsize=256)
def _solid_ground_tint(color, material, base):
    # 월드 전체 팔레트는 작은 색상 조합만 반복한다. 좌표별 캐시는 만들지 않는다.
    return tuple(channel + target - original
                 for channel, target, original in zip(color, TINTS[material], base))


def load_compact_image(filename, size):
    """PNG는 보존하고 초기화 때 CPU 면을 줄여 필요한 GPU 텍스처만 만든다."""
    global _frame_data
    if _frame_data is None:
        try:
            _frame_data = json.loads((ASSET_DIR / 'frames.json').read_text(encoding='utf-8'))
        except (OSError, ValueError) as error:
            raise OSError('v2 자산 외곽 기준을 읽지 못했습니다.') from error
    frame = _frame_data.get(filename)
    if frame is None:
        raise OSError(f'v2 자산 외곽 기준이 없습니다: {filename}')
    pico = import_module('pico2d.pico2d')
    try:
        sdl = import_module('sdl2')
        image_api = import_module('sdl2.sdlimage')
    except ImportError as error:
        raise OSError('기존 SDL 이미지 바인딩을 사용할 수 없습니다.') from error
    required = ('SDL_CreateRGBSurfaceWithFormat', 'SDL_BlitScaled', 'SDL_Rect', 'SDL_FillRect',
                'SDL_MapRGBA',
                'SDL_SetSurfaceBlendMode', 'SDL_CreateTextureFromSurface', 'SDL_FreeSurface',
                'SDL_SetTextureBlendMode', 'SDL_SetTextureScaleMode', 'SDL_DestroyTexture')
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
        # 생성 캔버스의 비율/여백 편차를 v1의 불투명 외곽 기준으로 정규화한다.
        sx, sy, sw, sh = frame['source_rect']
        rx, ry, rw, rh = frame['reference_rect']
        reference_w, reference_h = frame['reference_size']
        left, top = round(rx * size[0] / reference_w), round(ry * size[1] / reference_h)
        right = round((rx + rw) * size[0] / reference_w)
        bottom = round((ry + rh) * size[1] / reference_h)
        source_rect = sdl.SDL_Rect(sx, sy, sw, sh)
        destination_rect = sdl.SDL_Rect(left, top, right - left, bottom - top)
        if (sdl.SDL_FillRect(surface, None, 0) != 0
                or sdl.SDL_SetSurfaceBlendMode(source, sdl.SDL_BLENDMODE_NONE) != 0
                or sdl.SDL_BlitScaled(source, source_rect, surface, destination_rect) != 0):
            raise OSError(f'v2 이미지 축소 실패: {filename}')
        roof = frame.get('opaque_roof')
        if roof:
            # 청록 지붕 중앙의 생성 알파 오류를 막고 설비만 위에 초기 합성한다.
            def target_rect(rect):
                x, y, width, height = rect
                x1, y1 = round(x * size[0] / reference_w), round(y * size[1] / reference_h)
                x2 = round((x + width) * size[0] / reference_w)
                y2 = round((y + height) * size[1] / reference_h)
                return sdl.SDL_Rect(x1, y1, x2 - x1, y2 - y1)

            color = sdl.SDL_MapRGBA(surface.contents.format, *roof['color'], 255)
            if (sdl.SDL_FillRect(surface, target_rect(roof['rect']), color) != 0
                    or sdl.SDL_SetSurfaceBlendMode(source, sdl.SDL_BLENDMODE_BLEND) != 0):
                raise OSError(f'v2 지붕 기본 면 준비 실패: {filename}')
            for rect in roof['details']:
                x, y, width, height = rect
                x1, y1 = round(sx + (x - rx) * sw / rw), round(sy + (y - ry) * sh / rh)
                x2 = round(sx + (x + width - rx) * sw / rw)
                y2 = round(sy + (y + height - ry) * sh / rh)
                detail = sdl.SDL_Rect(x1, y1, x2 - x1, y2 - y1)
                if sdl.SDL_BlitScaled(source, detail, surface, target_rect(rect)) != 0:
                    raise OSError(f'v2 지붕 설비 합성 실패: {filename}')
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
