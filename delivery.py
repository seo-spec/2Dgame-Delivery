"""배송지와 지정 화물 연결 데이터 및 배송 완료 처리."""


STOP_SPEED_THRESHOLD = 15.0  # 전·후진 공통 저속·정차 기준. 단위: 픽셀/초.


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

    def contains_position(self, player_x, player_y):
        left, bottom, right, top = self.get_zone_bounds()
        return left <= player_x <= right and bottom <= player_y <= top

    def can_deliver(self, player_x, player_y, speed):
        speed_magnitude = abs(speed)
        return (not self.delivered
                and self.contains_position(player_x, player_y)
                and speed_magnitude <= STOP_SPEED_THRESHOLD)

    def try_deliver(self, player_x, player_y, speed, cargo_list):
        if not self.can_deliver(player_x, player_y, speed):
            return False
        cargo = next((cargo for cargo in cargo_list
                      if cargo.cargo_id == self.cargo_id and not cargo.delivered), None)
        if cargo is None:
            return False
        # 파손 여부와 무관하게 지정 화물과 배송지를 함께 완료한다. 화물은 보관한다.
        cargo.delivered = True
        self.delivered = True
        return True
