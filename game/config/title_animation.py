"""도트 도시 타이틀의 자산과 장식 차량 경로. 좌표는 왼쪽 위 원점이다."""

from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parents[2] / 'assets/images/title'
REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720
BACKGROUND_PATH = ASSET_DIR / 'title_city_v1.png'
FALLBACK_PATH = ASSET_DIR / 'title_background_v1.png'
MENU_SAFE_RECT = (780, 235, 1240, 570)
# 위치는 왼쪽 위 원점의 받침대 중심이다. 차량 차선과 메뉴 영역을 피한다.
STREETLAMP_PATH = ASSET_DIR / 'title_streetlamp.png'
STREETLAMP_SIZE = (12, 50)
STREETLAMP_CLIP = (262, 325, 297, 1259)
STREETLAMP_POSITIONS = (
    (280, 112),  # 상단 도로변 왼쪽
    (430, 112),  # 상단 도로변
    (600, 112),  # 상단 도로변 오른쪽
    (102, 240),  # 왼쪽 외곽 보도 위쪽
    (102, 360),  # 왼쪽 외곽 보도
    (741, 400),  # 오른쪽 외곽 보도
    (741, 530),  # 오른쪽 외곽 보도 아래쪽
    (450, 554),  # 하단 도로의 안쪽 보도
)
MAX_FRAME_TIME = 0.1
# 한 주기의 비율과 RGB 밝기. 끝 색을 시작 색과 맞춰 반복 경계를 연결한다.
DAY_NIGHT_CYCLE_SECONDS = 30.0
DAY_NIGHT_COLORS = (
    (0.00, (255, 255, 255)),  # 낮
    (0.12, (255, 255, 255)),
    (0.34, (235, 180, 145)),  # 노을
    (0.50, (75, 95, 145)),   # 밤
    (0.68, (75, 95, 145)),
    (0.85, (215, 180, 165)),  # 새벽
    (1.00, (255, 255, 255)),
)
CORNER_RADIUS = 22
ROUTES = (
    {'rect': (168, 170, 673, 581), 'clockwise': True, 'speed': 48.0},
    {'rect': (138, 140, 703, 611), 'clockwise': False, 'speed': 54.0},
)
SPRITES = {
    'car': {
        'path': ASSET_DIR / 'title_car.png',
        'size': (26, 52),
        'clip': (199, 316, 528, 1054),
    },
    'motorcycle': {
        'path': ASSET_DIR / 'title_motorcycle.png',
        'size': (20, 40),
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
