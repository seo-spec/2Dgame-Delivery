"""운석과 크레이터의 공통 초기값. 크기는 월드 픽셀 단위 반경이다."""

from random import randint, sample, uniform

MIN_RADIUS = 34
MAX_RADIUS = 54
WARNING_DURATION = 2.0
MIN_FALL_DURATION = 0.6
MAX_FALL_DURATION = 1.4
FALL_HEIGHT = 260.0
BLOCK_DURATION = 3.0
LANDING_DAMAGE_RATIO = 0.10
CONTACT_GRACE_DURATION = 0.2
PUSH_OUT_MARGIN_RATIO = 0.10
MAX_PUSH_OUT_CANDIDATES = 64
MIN_WAVE_INTERVAL = 9.0
MAX_WAVE_INTERVAL = 11.0
MIN_WAVE_COUNT = 9
MAX_WAVE_COUNT = 10
MAX_WAVE_PLACEMENT_ATTEMPTS = 500


def sample_radius():
    return randint(MIN_RADIUS, MAX_RADIUS)


def sample_wave_interval():
    return uniform(MIN_WAVE_INTERVAL, MAX_WAVE_INTERVAL)


def sample_fall_durations(count):
    """같은 묶음에서 중복 없는 낙하 시간을 밀리초 단위로 추첨한다."""
    return [value / 1000 for value in sample(
        range(round(MIN_FALL_DURATION * 1000), round(MAX_FALL_DURATION * 1000) + 1), count)]
