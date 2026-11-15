"""화물 상태를 확인하기 위한 임시 화면 고정 텍스트."""

import os
from pathlib import Path

from pico2d import get_canvas_height, get_canvas_width, load_font


FONT_PATH = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'malgun.ttf'
FONT_SIZE = 18
TEXT_LEFT = 16
TEXT_TOP_MARGIN = 30
LINE_SPACING = 26
CARD_COLUMNS = 3
CARD_TOP_MARGIN = 110
CARD_ROW_SPACING = 208


class CargoDebugText:
    def __init__(self):
        # Windows 기본 한글 폰트. 플레이 초기화 시 한 번만 불러온다.
        self.font = load_font(str(FONT_PATH), FONT_SIZE)

    def draw(self, cargo_list, total_revenue, delivery_houses, elapsed_time, cargo_received):
        lines = [
            f'누적 수익: {total_revenue:,}원',
            f'배송: {sum(house.delivered for house in delivery_houses)} / {len(delivery_houses)}',
            f'경과시간: {elapsed_time:.1f}초',
            '화물 수령 완료' if cargo_received else '배달소에서 화물을 수령하세요',
        ]
        self._draw_lines(lines, TEXT_LEFT, get_canvas_height() - TEXT_TOP_MARGIN)
        cargo_by_id = {cargo.cargo_id: cargo for cargo in cargo_list}
        column_width = (get_canvas_width() - TEXT_LEFT * 2) / CARD_COLUMNS
        for index, house in enumerate(delivery_houses):
            label = house.label
            lines = [f'[{label}]']
            cargo = cargo_by_id.get(house.cargo_id)
            if cargo is not None:
                if cargo.delivered:
                    status = '배송 완료'
                else:
                    status = '파손' if cargo.current_durability <= 0.0 else '정상'
                lines.extend((
                    f'화물 ID: {cargo.cargo_id}',
                    f'상태: {status}',
                    f'내구도: {cargo.current_durability:.1f} / {cargo.max_durability:.1f}',
                    f'흔들림: {cargo.shake:.1f}',
                ))
            else:
                lines.extend((f'화물 ID: {house.cargo_id}', '상태: 수령 대기'))
            if house.delivered:
                mood_text = f'{label} 배송 시 기분: {house.delivered_mood}'
            elif cargo_received:
                mood_text = f'{label} 고객 기분: {house.get_customer_mood(elapsed_time)}'
            else:
                mood_text = f'{label} 고객 기분: 배송 시작 전'
            lines.append(mood_text)
            column, row = index % CARD_COLUMNS, index // CARD_COLUMNS
            left = round(TEXT_LEFT + column * column_width)
            top = get_canvas_height() - TEXT_TOP_MARGIN - CARD_TOP_MARGIN - row * CARD_ROW_SPACING
            self._draw_lines(lines, left, top)

    def _draw_lines(self, lines, left, top):
        for index, text in enumerate(lines):
            y = top - index * LINE_SPACING
            # 밝은 지형에서도 읽을 수 있도록 작은 검은 그림자만 추가한다.
            self.font.draw(left + 1, y - 1, text, (0, 0, 0))
            self.font.draw(left, y, text, (255, 255, 255))

    def draw_delivery_hint(self, visible):
        if not visible:
            return
        text = 'Space: 배달'
        x, y = get_canvas_width() // 2 - 55, 40
        self.font.draw(x + 1, y - 1, text, (0, 0, 0))
        self.font.draw(x, y, text, (255, 255, 255))

    def draw_pickup_hint(self, visible):
        if visible:
            text = 'Space: 화물 수령'
            x, y = get_canvas_width() // 2 - 75, 40
            self.font.draw(x + 1, y - 1, text, (0, 0, 0))
            self.font.draw(x, y, text, (255, 255, 255))
