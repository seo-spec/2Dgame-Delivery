"""우측 280px 안에 배송지별 상태를 보여 주는 도트풍 카드 패널."""

from math import ceil

from pico2d import draw_rectangle

from game.config import settings
from game.systems.stage import StageState
from game.ui.progress_hud import PANEL, EDGE, HIGHLIGHT, CREAM, MUTED, MINT, AMBER, RED


class DeliveryPanel:
    def __init__(self, font, label_font, value_font, cargo_icons):
        # HUD가 이미 준비한 글꼴·아이콘을 빌린다. 별도 로딩/종료는 하지 않는다.
        self.font = font
        self.label_font = label_font
        self.value_font = value_font
        self.cargo_icons = cargo_icons

    @staticmethod
    def _box(left, bottom, right, top, color):
        draw_rectangle(round(left), round(bottom), round(right), round(top), *color, filled=True)

    def _card(self, left, bottom, right, top, color):
        self._box(left + 2, bottom, right - 2, top, color)
        self._box(left, bottom + 2, right, top - 2, color)
        self._box(left + 2, bottom + 2, right - 2, top - 2, PANEL)
        self._box(left + 4, top - 4, right - 4, top - 2, HIGHLIGHT)

    @staticmethod
    def _status(house, controller):
        if controller.state == StageState.WAITING:
            return '수령 대기', '배송 시작 전', '배송 시작 전', 0.0, MUTED
        if house.delivered:
            return '배송 완료', '배송 완료', house.delivered_mood or '보통', 1.0, MINT
        elapsed = controller.elapsed_time
        late = elapsed > house.deadline
        seconds = ceil(elapsed - house.deadline) if late else ceil(house.deadline - elapsed)
        urgent = not late and house.deadline - elapsed <= 10
        status = '! 지각' if late else '! 마감 임박' if urgent else '배송 중'
        message = f'{seconds:,}초 초과' if late else f'마감까지 {seconds:,}초'
        mood = house.get_customer_mood(elapsed)
        color = RED if late else AMBER if urgent or mood != '만족' else MINT
        ratio = max(0.0, min(1.0, elapsed / max(house.deadline, 0.001)))
        return status, message, mood, ratio, color

    def draw(self, width, height, houses, cargo_by_id, controller):
        panel_x = settings.VIEWPORT_LEFT + width
        right_edge = panel_x + settings.DELIVERY_PANEL_WIDTH
        self._box(panel_x, 0, right_edge, height, (25, 39, 48))
        self._box(panel_x, 0, panel_x + 2, height, EDGE)
        self.value_font.draw(panel_x + 24, height - 34, '배송 현황', CREAM, max_width=232)
        self.label_font.draw(panel_x + 24, height - 60, '출발 기준 마감 / 고객 기분',
                             MUTED, max_width=232)
        self._box(panel_x + 12, height - 78, right_edge - 12, height - 76, EDGE)

        # 720px 기준: 카드 상단630, 간격114, 높이104. 다섯 번째 하단70.
        left, right = panel_x + 12, right_edge - 12
        for index, house in enumerate(houses):
            top = height - 90 - index * 114
            bottom = top - 104
            status, message, mood, ratio, color = self._status(house, controller)
            accent = color if house.delivered or status.startswith('!') else EDGE
            self._card(left, bottom, right, top, accent)
            self._box(left + 2, bottom + 6, left + 4, top - 6, color)
            x = left + 12
            # 구획별 폭을 제한해 긴 글자와 숫자가 옆 정보에 닿지 않게 한다.
            self.font.draw(x, top - 17, house.label.removesuffix('집'), CREAM, max_width=80)
            self.label_font.draw(x + 90, top - 17, status, color, max_width=142)
            self.value_font.draw(x, top - 40, message, color, max_width=232)
            self.label_font.draw(x, top - 62, f'기분: {mood}', MUTED, max_width=174)
            cargo = cargo_by_id.get(house.cargo_id)
            cargo_type = cargo.cargo_type if cargo is not None else None
            name = cargo_type.name if cargo_type is not None else '수령 전'
            self.label_font.draw(x, top - 82, f'화물: {name}', CREAM, max_width=174)
            if cargo_type is not None:
                icon = self.cargo_icons.get(cargo_type.type_id)
                if icon is not None:
                    icon.draw(right - 28, top - 73, 32, 32)
            self._box(x, bottom + 6, right - 12, bottom + 10, (49, 67, 77))
            if ratio > 0:
                self._box(x, bottom + 6, x + (right - 12 - x) * ratio, bottom + 10, color)

        self.label_font.draw(panel_x + 24, 42, '! 마감 임박: 남은 시간 10초 이내',
                             AMBER, max_width=232)
        self.label_font.draw(panel_x + 24, 22, '! 지각: 초과시간 표시', RED, max_width=232)
