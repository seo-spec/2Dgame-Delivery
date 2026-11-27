"""HUD와 월드의 주요 표시를 피해 우선순위대로 놓는 안내 배너."""

from pico2d import draw_rectangle

from game.ui.progress_hud import PANEL, EDGE, HIGHLIGHT, CREAM, MINT, AMBER, RED


class NoticeStack:
    def __init__(self, font, label_font):
        self.font = font
        self.label_font = label_font
        self.items = []
        self.obstacles = []
        self.width = 1000
        self.height = 720

    def begin(self, width, height, obstacles):
        self.width, self.height = width, height
        self.items.clear()
        self.obstacles = list(obstacles)

    def add(self, text, kind='상태', priority=20):
        item = (priority, kind, text)
        if item not in self.items:
            self.items.append(item)

    @staticmethod
    def _overlaps(a, b):
        return a[0] < b[2] + 6 and a[2] > b[0] - 6 and a[1] < b[3] + 6 and a[3] > b[1] - 6

    @staticmethod
    def _wrap(text, width):
        # 글자 단위 예상 폭으로 나누고 실제 렌더에서는 캐시된 텍스처 폭으로 한 번 더 맞춘다.
        lines, line, used = [], '', 0
        for char in text:
            advance = 18 if ord(char) > 127 else 10
            if line and used + advance > width:
                lines.append(line)
                line, used = '', 0
            line += char
            used += advance
        if line:
            lines.append(line)
        return lines or ['']

    def draw(self):
        occupied = list(self.obstacles)
        has_action = any(priority == 70 and kind == '조작' for priority, kind, _ in self.items)
        for _, kind, text in sorted(self.items, key=lambda item: -item[0]):
            if has_action and kind == '상태':
                continue
            placed = False
            for width in (min(520, self.width - 40), 400, 300):
                if width > self.width - 40:
                    continue
                lines = self._wrap(text, width - 94)
                height = 22 * len(lines) + 18
                # 하단 카드 위부터 탐색하고, 중앙/왼쪽/오른쪽 후보를 차례로 검사한다.
                for bottom in range(132, int(self.height - 80 - height) + 1, 12):
                    for left in ((self.width - width) / 2, 20, self.width - width - 20):
                        bounds = (left, bottom, left + width, bottom + height)
                        if any(self._overlaps(bounds, obstacle) for obstacle in occupied):
                            continue
                        self._draw_banner(bounds, kind, lines)
                        occupied.append(bounds)
                        placed = True
                        break
                    if placed:
                        break
                if placed:
                    break
            # 빈자리가 없는 낮은 우선순위 안내는 주요 화면 위에 억지로 겹쳐 그리지 않는다.

    def _draw_banner(self, bounds, kind, lines):
        left, bottom, right, top = bounds
        color = RED if kind in ('경고', '실패') else MINT if kind == '조작' else AMBER
        def box(x1, y1, x2, y2, tint):
            draw_rectangle(round(x1), round(y1), round(x2), round(y2), *tint, filled=True)
        box(left + 2, bottom, right - 2, top, EDGE)
        box(left, bottom + 2, right, top - 2, EDGE)
        box(left + 2, bottom + 2, right - 2, top - 2, PANEL)
        box(left + 4, top - 4, right - 4, top - 2, HIGHLIGHT)
        box(left + 2, bottom + 6, left + 4, top - 6, color)
        label = '! 경고' if kind == '경고' else kind
        self.label_font.draw(round(left + 12), round((top + bottom) / 2), label, color, max_width=62)
        for index, line in enumerate(lines):
            self.font.draw(round(left + 82), round(top - 20 - index * 22), line,
                           CREAM if kind != '실패' else RED, max_width=right - left - 94)
