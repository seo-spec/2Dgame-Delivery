"""수령할 화물 종류·아이콘 및 종류별 손상 배율 초기값."""

from dataclasses import dataclass
from pathlib import Path


ICON_DIRECTORY = Path(__file__).resolve().parents[2] / 'assets' / 'images' / 'cargo'


@dataclass(frozen=True)
class CargoType:
    type_id: str
    name: str
    shake_damage_multiplier: float = 1.0
    collision_damage_multiplier: float = 1.0

    @property
    def icon_path(self):
        return ICON_DIRECTORY / f'{self.type_id}.png'


CARGO_TYPES = (
    CargoType('parcel', '일반 화물'),
    CargoType('fragile', '취급주의', 1.4, 1.4),
    CargoType('electronics', '전자제품', 1.2, 1.3),
    CargoType('glassware', '유리제품', 1.6, 1.6),
    CargoType('small_parcel', '소형 화물', 0.8, 0.8),
    CargoType('books', '도서', 0.6, 0.7),
    CargoType('flowers', '꽃', 1.3, 1.1),
    CargoType('food', '음식', 1.2, 1.0),
    CargoType('fruit', '과일', 1.1, 1.2),
    CargoType('medicine', '의약품', 1.2, 1.1),
    CargoType('clothing', '의류', 0.4, 0.5),
    CargoType('ceramics', '도자기', 1.5, 1.6),
    CargoType('plant', '화분', 1.1, 1.4),
)
