"""기존 하단 영역에 화물5개의 상태를 보여 주는 도트풍 카드."""

from pico2d import draw_rectangle

from game.ui.progress_hud import PANEL, EDGE, HIGHLIGHT, CREAM, MUTED, MINT, RED


class CargoPanel:
    def __init__(self, font, label_font, cargo_icons):
        # 상단·우측 HUD와 동일한 기존 캐시를 빌리고 별도 자원을 로드하지 않는다.
        self.font = font
        self.label_font = label_font
        self.cargo_icons = cargo_icons

    @staticmethod
    def _box(left, bottom, right, top, color):
        draw_rectangle(round(left), round(bottom), round(right), round(top), *color, filled=True)

    @staticmethod
    def _status(cargo):
        if cargo is None:
            return '수령 대기', 0.0, '--', MUTED
        ratio = cargo.current_durability / cargo.max_durability
        value = f'{ratio * 100:.0f}%'
        if cargo.delivered:
            return '완료', ratio, value, MINT
        if ratio <= 0:
            return '파손', ratio, value, RED
        return '적재', ratio, value, MINT if ratio >= 0.5 else RED

    def draw(self, width, houses, cargo_by_id):
        left, right = 12, width - 12
        bottom, top = 12, 120
        count = max(1, len(houses))
        gap = 8
        card_width = (right - left - gap * (count - 1)) / count
        # 기존 하단 예약 영역 전체를 덮고 그 안에 동일 폭 카드를 배치한다.
        self._box(left, bottom, right, top, (25, 39, 48))
        for index, house in enumerate(houses):
            x = round(left + index * (card_width + gap))
            end = round(left + index * (card_width + gap) + card_width)
            cargo = cargo_by_id.get(house.cargo_id)
            status, ratio, value, color = self._status(cargo)
            border = color if status in ('파손', '완료') else EDGE
            self._box(x + 2, bottom, end - 2, top, border)
            self._box(x, bottom + 2, end, top - 2, border)
            self._box(x + 2, bottom + 2, end - 2, top - 2, PANEL)
            self._box(x + 4, top - 4, end - 4, top - 2, HIGHLIGHT)
            self.font.draw(x + 10, 102, house.label.removesuffix('집'), CREAM, max_width=50)
            self.label_font.draw(x + 70, 102, status, color, max_width=end - x - 80)

            cargo_type = cargo.cargo_type if cargo is not None else None
            if cargo_type is not None:
                icon = self.cargo_icons.get(cargo_type.type_id)
                if icon is not None:
                    icon.draw(x + 28, 76, 32, 32)
            else:
                # 수령 전 빈 아이콘 슬롯. 텍스처를 만들거나 읽지 않는다.
                self._box(x + 12, 60, x + 44, 92, (49, 67, 77))
                self.label_font.draw(x + 19, 76, '--', MUTED, max_width=20)
            name = cargo_type.name if cargo_type is not None else '화물 수령 전'
            self.label_font.draw(x + 50, 77, name, CREAM, max_width=end - x - 60)
            self.label_font.draw(x + 10, 51, '내구', MUTED, max_width=38)
            self.font.draw(x + 58, 51, value, color, max_width=end - x - 86)
            self._box(x + 10, 26, end - 10, 32, (49, 67, 77))
            fill = max(0.0, min(1.0, ratio))
            if fill > 0:
                self._box(x + 10, 26, x + 10 + (end - x - 20) * fill, 32, color)
            if status == '파손':
                self.label_font.draw(end - 25, 51, '!', RED, max_width=12)
