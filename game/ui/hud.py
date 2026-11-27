"""상단 진행 정보·하단 화물 상태·오른쪽 배송 마감 HUD."""

from math import ceil

from pico2d import get_canvas_height, load_image, draw_rectangle
from game.ui.cached_font import CachedFont
from game.ui.progress_hud import ProgressHUD
from game.ui.delivery_panel import DeliveryPanel
from game.ui.cargo_panel import CargoPanel
from game.core import debug_view
from game.core import game_framework
from game.config import settings
from game.config.fonts import FONT_PATH
from game.systems.stage import StageState
from game.systems.traffic_penalties import FINE_AMOUNT

FONT_SIZE = 18
LINE_SPACING = 26
NAVY = (25, 40, 57)
WHITE = (245, 248, 249)
MUTED = (112, 132, 146)
GREEN = (137, 226, 179)
RED = (239, 132, 108)
YELLOW = (255, 205, 104)


class CargoDebugText:
    def __init__(self):
        self.font = CachedFont(FONT_PATH, FONT_SIZE)
        self.menu_font = CachedFont(FONT_PATH, 30)
        self.progress_hud = ProgressHUD()
        self.cargo_icons = {}
        self.delivery_panel = DeliveryPanel(self.font, self.progress_hud.label_font,
                                            self.progress_hud.value_font, self.cargo_icons)
        self.cargo_panel = CargoPanel(self.font, self.progress_hud.label_font, self.cargo_icons)

    def close(self):
        self.font.close()
        self.menu_font.close()
        self.progress_hud.close()
        self.cargo_icons.clear()

    def prepare_cargo_icons(self, cargo_list):
        # 수령 시 한 번 불러오고 draw에서는 캐시만 사용한다. 수령 전에는 읽지 않는다.
        for cargo in cargo_list:
            cargo_type = cargo.cargo_type
            if cargo_type is not None and cargo_type.type_id not in self.cargo_icons:
                self.cargo_icons[cargo_type.type_id] = load_image(str(cargo_type.icon_path))

    def _box(self, left, bottom, right, top, color):
        draw_rectangle(round(left), round(bottom), round(right), round(top), *color, filled=True)

    def _text(self, text, x, y, color=WHITE):
        self.font.draw(round(x), round(y), text, color)

    def _draw_lines(self, lines, left, top):
        for index, text in enumerate(lines):
            self._text(text, left, top - index * LINE_SPACING)

    def _bar(self, x, y, width, ratio, color):
        self._box(x, y, x + width, y + 8, (218, 226, 230))
        fill = max(0.0, min(1.0, ratio)) * width
        if fill > 0:
            self._box(x, y, x + fill, y + 8, color)

    def draw(self, cargo_list, total_revenue, delivery_houses, controller, top_reserved_height=0,
             traffic_diagnostics=()):
        width, height = settings.VIEWPORT_WIDTH, get_canvas_height()
        elapsed = controller.elapsed_time
        waiting = controller.state == StageState.WAITING
        completed = sum(house.delivered for house in delivery_houses)
        remaining = max(0, ceil(controller.time_limit - elapsed))
        self.progress_hud.draw(width, height, remaining, completed, len(delivery_houses),
                               total_revenue, controller)

        cargo_by_id = {cargo.cargo_id: cargo for cargo in cargo_list}
        self.cargo_panel.draw(width, delivery_houses, cargo_by_id)

        self.delivery_panel.draw(width, height, delivery_houses, cargo_by_id, controller)

        if controller.state == StageState.RETURNING:
            self._notice('배달소로 돌아가세요')
        elif controller.state == StageState.FAILED:
            reason = controller.failure_reason
            if len(reason) > 24:
                self._notice('실패: 배송 수익·손상·벌금 확인', 158)
                self._notice('목표 수익 달성 불가', 130)
            else:
                self._notice(f'실패: {reason}')
        elif waiting:
            self._notice('배달소에서 화물을 수령하세요')

        if debug_view.enabled:
            lines = [f'FPS {game_framework.fps:.1f} | 계산 {game_framework.update_ms:.1f}ms',
                     f'그리기 {game_framework.render_ms:.1f}ms / 화면대기 {game_framework.present_ms:.1f}ms',
                     f'경과시간: {elapsed:.2f}초',
                     f'남은 최대 예상 수익: {controller.remaining_max_revenue:,}원']
            lines.extend(traffic_diagnostics)
            for house in delivery_houses:
                cargo = cargo_by_id.get(house.cargo_id)
                shake = f'{cargo.shake:.1f}' if cargo else '--'
                lines.append(f'{house.label} ({house.x}, {house.y}) {house.cargo_id} 흔들림 {shake}')
                if cargo is not None:
                    name = cargo.cargo_type.name if cargo.cargo_type else '일반 화물'
                    lines.append(f'  {name} | 흔들림 손상 x{cargo.shake_damage_multiplier:.1f}'
                                 f' / 충돌 피해 x{cargo.collision_damage_multiplier:.1f}')
            top = height - 78 - top_reserved_height
            # 운석 안내·하단 디버그 도구와 겹치면 상세 행 수만 줄인다.
            max_lines = max(1, int((top - 280 - 14) // LINE_SPACING))
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                lines[-1] = '... 상세 상태는 개발 로그 참고'
            self._box(12, top - 14 - len(lines) * LINE_SPACING, 680, top, NAVY)
            self._draw_lines(lines, 24, top - 26)

    def _notice(self, text, y=130):
        center = settings.VIEWPORT_WIDTH / 2
        half = max(260, len(text) * 9)
        self._box(center - half, y - 12, center + half, y + 24, NAVY)
        self._text(text, center - half + 12, y, WHITE)

    def draw_delivery_hint(self, target):
        if target is not None:
            self._notice(f'Space: {target.label} 배달')

    def draw_signal_penalty(self, penalties):
        if penalties.notice_remaining > 0:
            x = settings.VIEWPORT_LEFT + settings.VIEWPORT_WIDTH / 2
            y = get_canvas_height() - 96
            self._box(x - 165, y - 21, x + 165, y + 21, NAVY)
            self._box(x - 165, y - 21, x - 161, y + 21, RED)
            self._text(f'신호 위반! 벌금 {FINE_AMOUNT}원', x - 135, y, RED)

    def draw_delivery_indicator(self, target, motorcycle, camera):
        """실제 배송 입력과 같은 대상 판정으로 차체 위에 작은 느낌표를 표시한다."""
        if target is None:
            return
        x, player_y = camera.world_to_screen(motorcycle.x, motorcycle.y)
        y = player_y + motorcycle.collision_radius + 28
        # 월드와 같은 좌표를 사용하고 화면 가장자리에서 다른 UI 영역으로 넘기지 않는다.
        if (x - 16 < camera.viewport_left
                or x + 16 > camera.viewport_left + camera.viewport_width
                or y - 20 < camera.viewport_bottom
                or y + 20 > camera.viewport_bottom + camera.viewport_height):
            return
        self._box(x - 16, y - 20, x + 16, y + 20, NAVY)
        self._box(x - 13, y - 17, x + 13, y + 17, YELLOW)
        self._box(x - 2, y - 3, x + 2, y + 11, NAVY)
        self._box(x - 2, y - 11, x + 2, y - 7, NAVY)

    def draw_house_label(self, house, x, y):
        text = f'{house.label} 완료' if house.delivered else house.label
        self.font.draw(x + 1, y - 1, text, (0, 0, 0))
        self.font.draw(x, y, text, WHITE)

    def draw_pickup_hint(self, visible):
        if visible:
            self._notice('Space: 화물 수령')

    def draw_clear_result(self, delivery_houses, total_revenue, target_revenue):
        completed = sum(house.delivered for house in delivery_houses)
        self._box(270, 264, settings.VIEWPORT_WIDTH - 270, 442, NAVY)
        self._draw_lines(('STAGE CLEAR', f'최종 배송: {completed} / {len(delivery_houses)}',
                          f'최종 수익: {total_revenue:,}원',
                          f'목표 {target_revenue:,}원: ' + ('달성' if total_revenue >= target_revenue else '미달성')),
                         292, 409)

    def draw_restart_hint(self):
        self._notice('R: 다시 시작', 190)

    def pause_button_bounds(self, index):
        center_x, center_y = settings.WINDOW_WIDTH / 2, get_canvas_height() / 2
        top = center_y + 75 - index * 76
        return center_x - 160, top - 56, center_x + 160, top

    def pause_button_at(self, x, y):
        for index in range(3):
            left, bottom, right, top = self.pause_button_bounds(index)
            if left <= x <= right and bottom <= y <= top:
                return index
        return None

    def draw_pause_menu(self, selected):
        width, height = settings.WINDOW_WIDTH, get_canvas_height()
        # 현재 화면 위에 얇은 빗금과 중앙 메뉴를 겹쳐 표시한다.
        for y in range(0, height, 3):
            self._box(0, y, width, y + 1, (12, 22, 32))
        cx, cy = width / 2, height / 2
        self._box(cx - 205, cy - 215, cx + 205, cy + 190, NAVY)
        self._box(cx - 205, cy + 183, cx + 205, cy + 190, GREEN)
        self.menu_font.draw(round(cx - 63), round(cy + 135), 'PAUSED', WHITE)
        for index, text in enumerate(('Resume', 'Restart', 'Exit')):
            left, bottom, right, top = self.pause_button_bounds(index)
            active = index == selected
            self._box(left, bottom, right, top, GREEN if active else (43, 61, 77))
            self.menu_font.draw(round(left + 28), round(bottom + 18), text, NAVY if active else WHITE)
        self._text('↑↓ 선택 · Enter 확인 · Esc 재개', cx - 165, cy - 190, WHITE)
