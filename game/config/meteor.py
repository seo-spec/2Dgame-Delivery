"""운석과 크레이터의 공통 초기값. 크기는 월드 픽셀 단위 반경이다."""

from random import randint

MIN_RADIUS = 34
MAX_RADIUS = 54
WARNING_DURATION = 2.0
MIN_FALL_DURATION = 0.6
MAX_FALL_DURATION = 1.4
FALL_HEIGHT = 260.0


def sample_radius():
    return randint(MIN_RADIUS, MAX_RADIUS)
