"""차종별 차고·주행 이미지와 실행 중 적용 차종."""

from . import motorcycle_sprite as sprite


ASSET_DIR = sprite.SPRITE_PATH.parent
DEFAULT_MOTORCYCLE_ID = 'standard'
selected_motorcycle_id = DEFAULT_MOTORCYCLE_ID

MOTORCYCLES = {
    'standard': {
        'id': 'standard',
        'name': '기본 오토바이',
        'preview_path': ASSET_DIR / 'motorcycle_side_v1.png',
        'preview_clip': (82, 53, 1343, 862),
        'render': {
            'path': sprite.SPRITE_PATH,
            'origin': (0, 0),
            'frame_size': (sprite.SPRITE_FRAME_WIDTH, sprite.SPRITE_FRAME_HEIGHT),
            'columns': sprite.SPRITE_COLUMNS,
            'direction_count': sprite.SPRITE_DIRECTION_COUNT,
            'render_mode': sprite.SPRITE_RENDER_MODE,
            'base_frame': sprite.SPRITE_BASE_FRAME,
            'metrics': sprite.SPRITE_FRAME_METRICS,
        },
    },
    'blue': {
        'id': 'blue',
        'name': '블루 바이크',
        'preview_path': ASSET_DIR / 'motorcycle_blue_side_v1.png',
        'preview_clip': (79, 35, 1369, 887),
        'render': {
            'path': ASSET_DIR / 'motorcycle_blue_top_v1.png',
            'origin': (165, 133),
            'frame_size': (1445, 655),
            'columns': 1,
            'direction_count': 1,
            'render_mode': 'continuous',
            'base_frame': 0,
            'metrics': ((722.5, 327.5, 0.0, 723.2),),
        },
    },
    'red': {
        'id': 'red',
        'name': '레드 스쿠터',
        'preview_path': ASSET_DIR / 'motorcycle_red_side_v1.png',
        'preview_clip': (93, 52, 1328, 864),
        'render': {
            'path': ASSET_DIR / 'motorcycle_red_top_v1.png',
            'origin': (471, 85),
            'frame_size': (1150, 606),
            'columns': 1,
            'direction_count': 1,
            'render_mode': 'continuous',
            'base_frame': 0,
            'metrics': ((575.0, 303.0, 0.0, 593.6),),
        },
    },
}


def get_selected_motorcycle():
    motorcycle = MOTORCYCLES.get(selected_motorcycle_id, MOTORCYCLES[DEFAULT_MOTORCYCLE_ID])
    if motorcycle['render'] is None:
        return MOTORCYCLES[DEFAULT_MOTORCYCLE_ID]
    return motorcycle
