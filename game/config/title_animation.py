"""도트 도시 타이틀의 자산과 장식 차량 경로. 좌표는 왼쪽 위 원점이다."""

from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parents[2] / 'assets/images/title'
REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720
BACKGROUND_PATH = ASSET_DIR / 'title_city_v1.png'
FALLBACK_PATH = ASSET_DIR / 'title_background_v1.png'
MENU_SAFE_RECT = (780, 235, 1240, 570)
MAX_FRAME_TIME = 0.1
CORNER_RADIUS = 18
ROUTES = (
    {'rect': (168, 170, 673, 581), 'clockwise': True, 'speed': 36.0},
    {'rect': (138, 140, 703, 611), 'clockwise': False, 'speed': 42.0},
)
SPRITES = {
    'car': {
        'path': ASSET_DIR / 'title_car.png',
        'size': (24, 48),
        'clip': (199, 316, 528, 1054),
    },
    'motorcycle': {
        'path': ASSET_DIR / 'title_motorcycle.png',
        'size': (18, 36),
        'clip': (246, 404, 471, 936),
    },
}
# 같은 차선은 속도를 통일하고 간격을 고정해 장식 차량끼리 따라잡지 않는다.
VEHICLES = (
    ('car', 0, 0.0),
    ('motorcycle', 0, 1 / 3),
    ('car', 0, 2 / 3),
    ('motorcycle', 1, 0.0),
    ('car', 1, 1 / 3),
    ('motorcycle', 1, 2 / 3),
)
