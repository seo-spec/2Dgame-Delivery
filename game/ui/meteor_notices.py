"""운석 수령 전 안내와 첫 묶음 경고. 표시는 운석 시뮬레이션 시계만 사용한다."""

from pathlib import Path

from pico2d import (
    draw_rectangle, get_canvas_height, load_wav,
    Mix_HaltChannel, Mix_Pause, Mix_PlayChannel, Mix_Playing, Mix_Resume,
)

from game.config import meteor as config
from game.config import settings
from game.systems.stage import StageState
from game.ui.minimap import MINIMAP_RESERVED_WIDTH

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

    def _alert_active(self, controller, meteor_system):
        if controller.state in (StageState.WAITING, StageState.FAILED, StageState.CLEAR):
            return False
        started = meteor_system.alert_started_at
        duration = (config.FIRST_ALERT_DURATION if meteor_system.alert_serial == 1
                    else config.REPEAT_ALERT_DURATION)
        return started is not None and 0 <= meteor_system.clock - started < duration

    def reserved_height(self, controller, meteor_system):
        if controller.state == StageState.WAITING:
            return 126
        return 54 if self._alert_active(controller, meteor_system) else 0

    def bounds(self, controller, meteor_system):
        reserved = self.reserved_height(controller, meteor_system)
        if not reserved:
            return None
        top = get_canvas_height() - 80
        return (settings.VIEWPORT_LEFT + 12, top - reserved + 6,
                settings.VIEWPORT_LEFT + settings.VIEWPORT_WIDTH - MINIMAP_RESERVED_WIDTH - 12, top)

    def draw(self, controller, meteor_system):
        bounds = self.bounds(controller, meteor_system)
        if bounds is None:
            return
        left, bottom, right, top = bounds
        waiting = controller.state == StageState.WAITING
        first = meteor_system.alert_serial == 1
        background = (25, 40, 57) if waiting else (67, 30, 36)
        draw_rectangle(left, bottom, right, top, *background, filled=True)
        draw_rectangle(left, bottom, left + 4, top, 240, 95, 75, filled=True)
        if waiting:
            lines = (
                ('운석 주의보 안내', (255, 210, 145)),
                ('붉은 외곽 = 낙하 위치 / 안쪽 원이 닫히면 착지', (245, 248, 249)),
                ('크레이터는 3초 차단 / 통행 불가 표지가 사라지면 통과', (245, 248, 249)),
                ('미니맵: 점멸은 낙하 / 줄어드는 채움은 차단 해제 시간', (180, 215, 235)),
            )
            for index, (text, color) in enumerate(lines):
                self.font.draw(left + 16, top - 24 - index * 25, text, color)
        else:
            text = ('운석 주의! 붉은 영역을 피하세요' if first
                    else f'운석 주의보 · {meteor_system.alert_count}곳 낙하 예고')
            self.font.draw(left + 16, top - 30, text, (255, 225, 195))
            if first and int((meteor_system.clock - meteor_system.alert_started_at) * 6) % 2 == 0:
                draw_rectangle(left, bottom, right, top, 255, 135, 105)
