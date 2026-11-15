"""배송지와 지정 화물 연결 데이터. 실제 배송 처리는 아직 하지 않는다."""


class DeliveryHouse:
    def __init__(self, house_id, x, y, cargo_id, zone_offset, zone_size):
        self.house_id = house_id
        self.x = x
        self.y = y
        self.cargo_id = cargo_id
        self.delivered = False
        # 건물 중심 기준 월드 단위 오프셋과 크기. 충돌 영역과는 별도다.
        self.zone_offset = tuple(zone_offset)
        self.zone_size = tuple(zone_size)

    def get_zone_bounds(self):
        offset_x, offset_y = self.zone_offset
        width, height = self.zone_size
        center_x, center_y = self.x + offset_x, self.y + offset_y
        return (center_x - width / 2, center_y - height / 2,
                center_x + width / 2, center_y + height / 2)
