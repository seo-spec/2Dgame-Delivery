"""화물 상태를 확인하기 위한 임시 화면 고정 텍스트."""

import os
from pathlib import Path

from pico2d import get_canvas_height, get_canvas_width, load_font


FONT_PATH = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'malgun.ttf'
FONT_SIZE = 18
TEXT_LEFT = 16
TEXT_TOP_MARGIN = 30
LINE_SPACING = 26


class CargoDebugText:
    def __init__(self):
        # Windows 기본 한글 폰트. 플레이 초기화 시 한 번만 불러온다.
        self.font = load_font(str(FONT_PATH), FONT_SIZE)

    def draw(self, cargo_list):
        if not cargo_list:
            return
        cargo = cargo_list[0]
        if cargo.delivered:
            status = '배송 완료'
        else:
            status = '파손' if cargo.current_durability <= 0.0 else '정상'
        lines = (
            f'화물 ID: {cargo.cargo_id}',
            f'상태: {status}',
            f'내구도: {cargo.current_durability:.1f} / {cargo.max_durability:.1f}',
            f'흔들림: {cargo.shake:.1f}',
        )
        top = get_canvas_height() - TEXT_TOP_MARGIN
        for index, text in enumerate(lines):
            y = top - index * LINE_SPACING
            # 밝은 지형에서도 읽을 수 있도록 작은 검은 그림자만 추가한다.
            self.font.draw(TEXT_LEFT + 1, y - 1, text, (0, 0, 0))
            self.font.draw(TEXT_LEFT, y, text, (255, 255, 255))

    def draw_delivery_hint(self, visible):
        if not visible:
            return
        text = 'Space: 배달'
        x, y = get_canvas_width() // 2 - 55, 40
        self.font.draw(x + 1, y - 1, text, (0, 0, 0))
        self.font.draw(x, y, text, (255, 255, 255))
