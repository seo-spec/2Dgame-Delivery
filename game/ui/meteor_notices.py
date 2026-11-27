"""미니맵 아래의 간단한 운석 경고와 첫 묶음 효과음."""

from pathlib import Path

from pico2d import (
    draw_line, draw_rectangle, load_wav,
    Mix_HaltChannel, Mix_Pause, Mix_PlayChannel, Mix_Playing, Mix_Resume,
)

from game.config import meteor as config
from game.systems.stage import StageState
from game.ui.progress_hud import PANEL, EDGE, HIGHLIGHT, AMBER, RED

SOUND_PATH = Path(__file__).resolve().parents[2] / 'assets/sounds/meteor_warning.wav'


class MeteorNotices:
    def __init__(self, font):
        self.font = font
        self.seen_alert = 0
        self.sound = None
        self.channel = -1
        try:
            self.sound = load_wav(str(SOUND_PATH))
            self.sound.set_volume(config.ALERT_SOUND_VOLUME)
        except (OSError, RuntimeError):
            print('[운석 경고음] 사운드를 불러오지 못했습니다. 시각 경고는 계속 표시합니다.')

    def _stop_sound(self):
        if self.channel >= 0:
            Mix_HaltChannel(self.channel)
            self.channel = -1

    def sync(self, meteor_system, state):
        if self.channel >= 0 and not Mix_Playing(self.channel):
            self.channel = -1
        if state in (StageState.FAILED, StageState.CLEAR) or meteor_system.alert_started_at is None:
            self._stop_sound()
            self.seen_alert = meteor_system.alert_serial
            return
        if meteor_system.alert_serial != self.seen_alert:
            self.seen_alert = meteor_system.alert_serial
            if self.seen_alert == 1 and self.sound is not None:
                # pico2d의 Wav는 채널 제어 메서드가 없어, 노출된 믹서 API로
                # 이 효과음의 채널만 기록해 일시정지·재시작 때 제어한다.
                self.channel = Mix_PlayChannel(-1, self.sound.wav, 0)
                if self.channel < 0:
                    print('[운석 경고음] 재생 채널을 얻지 못했습니다. 시각 경고는 유지합니다.')

    def set_paused(self, paused):
        if self.channel >= 0 and Mix_Playing(self.channel):
            if paused:
                Mix_Pause(self.channel)
            else:
                Mix_Resume(self.channel)

    def close(self):
        self._stop_sound()
        self.seen_alert = 0
        self.sound = None

    def _warning_active(self, controller, meteor_system):
        return (controller.state not in (StageState.FAILED, StageState.CLEAR)
                and bool(meteor_system.meteors))

    def draw(self, controller, meteor_system, minimap):
        if self._warning_active(controller, meteor_system):
            self._draw_warning(meteor_system, minimap)

    def _draw_warning(self, meteor_system, minimap):
        left, bottom, right, top = minimap.warning_bounds()
        falling = any(item.state == 'FALLING' for item in meteor_system.meteors)
        started = meteor_system.alert_started_at
        emphasis = (meteor_system.alert_serial == 1 and started is not None
                    and 0 <= meteor_system.clock - started < config.FIRST_ALERT_DURATION)
        accent = RED if falling else AMBER
        flashing = emphasis and int((meteor_system.clock - started) * 6) % 2 == 0
        border = accent if flashing else EDGE

        def box(x1, y1, x2, y2, color):
            draw_rectangle(round(x1), round(y1), round(x2), round(y2), *color, filled=True)

        # 예약된140×36px 안에서2px 계단 모서리와 윗면을 표현한다.
        box(left + 2, bottom, right - 2, top, border)
        box(left, bottom + 2, right, top - 2, border)
        box(left + 2, bottom + 2, right - 2, top - 2, PANEL)
        box(left + 4, top - 4, right - 4, top - 2, accent if flashing else HIGHLIGHT)
        box(left + 2, bottom + 6, left + 4, top - 6, accent)
        x, y = round(left + 20), round((bottom + top) / 2)
        if falling:
            # 꼬리와 각진 운석 본체: 예고 삼각형과 실루엣부터 구분한다.
            box(x + 3, y + 5, x + 5, y + 11, accent)
            box(x + 7, y + 4, x + 9, y + 8, accent)
            box(x - 6, y - 5, x + 4, y + 5, accent)
            box(x - 4, y - 7, x + 2, y + 7, accent)
            box(x - 4, y - 3, x, y + 1, PANEL)
            message = '낙하 중!'
        else:
            draw_line(x, y + 10, x - 10, y - 9, *accent)
            draw_line(x - 10, y - 9, x + 10, y - 9, *accent)
            draw_line(x + 10, y - 9, x, y + 10, *accent)
            box(x - 1, y - 1, x + 1, y + 5, accent)
            box(x - 1, y - 6, x + 1, y - 4, accent)
            message = '운석 예고'
        # 기존 Galmuri 캐시를 재사용하고 폭에 맞춰 표시 배율만 제한한다.
        self.font.draw(round(left + 38), y, message, accent, max_width=right - left - 48)
