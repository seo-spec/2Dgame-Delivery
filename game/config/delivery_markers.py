"""생성된 바닥 마커 PNG. 원본 알파를 보존하고 투명 여백만 UV에서 제외한다."""

from pathlib import Path

MARKER_DIRECTORY = Path(__file__).resolve().parents[2] / 'assets/images/markers'
# clip: left, bottom, width, height (pico2d의 아래쪽 원점).
MARKER_SPRITES = {
    'pickup': ('pickup_zone_v1.png', (83, 69, 1609, 738)),
    'delivery': ('delivery_zone_v1.png', (96, 80, 1582, 724)),
    'return': ('return_zone_v1.png', (88, 76, 1600, 727)),
    'complete': ('complete_zone_v1.png', (93, 80, 1588, 717)),
}
