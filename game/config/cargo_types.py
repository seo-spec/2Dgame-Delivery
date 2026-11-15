"""수령 시 선택할 화물 종류와 대응 아이콘. 밸런스 수치는 종류와 분리한다."""

from dataclasses import dataclass
from pathlib import Path


ICON_DIRECTORY = Path(__file__).resolve().parents[2] / 'assets' / 'images' / 'cargo'


@dataclass(frozen=True)
class CargoType:
    type_id: str
    name: str

    @property
    def icon_path(self):
        return ICON_DIRECTORY / f'{self.type_id}.png'


CARGO_TYPES = (
    CargoType('parcel', '일반 화물'),
    CargoType('fragile', '취급주의'),
    CargoType('electronics', '전자제품'),
    CargoType('glassware', '유리제품'),
    CargoType('small_parcel', '소형 화물'),
    CargoType('books', '도서'),
    CargoType('flowers', '꽃'),
    CargoType('food', '음식'),
    CargoType('fruit', '과일'),
    CargoType('medicine', '의약품'),
    CargoType('clothing', '의류'),
    CargoType('ceramics', '도자기'),
    CargoType('plant', '화분'),
)
