"""기존 상단 예약 영역 안에서 진행 정보를 보여 주는 도트풍 HUD."""

from pico2d import draw_rectangle

from game.config.fonts import FONT_PATH
from game.systems.stage import StageState
from game.ui.cached_font import CachedFont


PANEL = (34, 50, 61)
EDGE = (104, 123, 126)
HIGHLIGHT = (178, 185, 163)
CREAM = (241, 232, 210)
MUTED = (188, 200, 200)
MINT = (142, 215, 174)
AMBER = (240, 193, 90)
RED = (238, 128, 108)


class ProgressHUD:
    def __init__(self):
        self.label_font = CachedFont(FONT_PATH, 16)
        self.value_font = CachedFont(FONT_PATH, 20)
        self.timer_font = CachedFont(FONT_PATH, 30)

    def close(self):
        self.label_font.close()
        self.value_font.close()
        self.timer_font.close()

    @staticmethod
    def _box(left, bottom, right, top, color):
        draw_rectangle(round(left), round(bottom), round(right), round(top), *color, filled=True)

    def draw(self, width, height, remaining, completed, total, revenue, controller):
        left, right = 12, width - 12
        bottom, top = height - 64, height - 12
        # 2px 계단 모서리와 얇은 밝은 윗면. 기존 상단 영역 밖으로 확장하지 않는다.
        self._box(left + 2, bottom, right - 2, top, EDGE)
        self._box(left, bottom + 2, right, top - 2, EDGE)
        self._box(left + 2, bottom + 2, right - 2, top - 2, PANEL)
        self._box(left + 4, top - 4, right - 4, top - 2, HIGHLIGHT)
        # 1000px 플레이 영역에서 구획: 시간(28~252), 배송(276~402), 수익(426~758), 상태(794~972).
        delivery_x = round(width * 0.276)
        revenue_x = round(width * 0.426)
        state_x = round(width * 0.794)
        for divider in (delivery_x - 16, revenue_x - 16, state_x - 16):
            self._box(divider, bottom + 10, divider + 2, top - 10, EDGE)

        urgent = controller.state == StageState.DELIVERING and remaining <= 30
        time_color = RED if urgent else CREAM
        self.label_font.draw(28, height - 28, '남은 시간', MUTED, max_width=88)
        self.label_font.draw(28, height - 48, '시간 주의' if urgent else 'TIME',
                             RED if urgent else MUTED, max_width=88)
        self.timer_font.draw(122, height - 39, f'{remaining // 60:02d}:{remaining % 60:02d}',
                             time_color, max_width=delivery_x - 146)

        self.label_font.draw(delivery_x, height - 26, '배송 완료', MUTED,
                             max_width=revenue_x - delivery_x - 26)
        self.value_font.draw(delivery_x, height - 47, f'{completed} / {total}', CREAM,
                             max_width=revenue_x - delivery_x - 26)
        self.label_font.draw(revenue_x, height - 26, '수익 / 목표', MUTED,
                             max_width=state_x - revenue_x - 26)
        self.value_font.draw(revenue_x, height - 47,
                             f'{revenue:,} / {controller.target_revenue:,}원', AMBER,
                             max_width=state_x - revenue_x - 26)

        state_color = (RED if controller.state == StageState.FAILED else
                       AMBER if controller.state == StageState.WAITING else MINT)
        self._box(state_x - 4, bottom + 7, state_x - 2, top - 7, state_color)
        self.label_font.draw(state_x + 8, height - 26, '진행 상태', MUTED,
                             max_width=right - state_x - 24)
        self.value_font.draw(state_x + 8, height - 47, controller.state.value, state_color,
                             max_width=right - state_x - 24)
