"""배송지와 지정 화물 연결 데이터. 실제 배송 처리는 아직 하지 않는다."""


class DeliveryHouse:
    def __init__(self, house_id, x, y, cargo_id):
        self.house_id = house_id
        self.x = x
        self.y = y
        self.cargo_id = cargo_id
        self.delivered = False
