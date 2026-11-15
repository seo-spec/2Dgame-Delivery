"""배송지와 지정 화물 연결 데이터 및 배송 완료 처리."""

from math import floor


INITIAL_A_BASE_FEE = 500  # PRD 6.2 A집 초기 배달비. 단위: 원.
INITIAL_A_DEADLINE = 45.0  # 스테이지 출발 기준 마감. 단위: 초.
INITIAL_B_BASE_FEE = 550
INITIAL_B_DEADLINE = 65.0
# (건물 ID, 표시 이름, 지정 화물 ID, 기본비, 출발 기준 마감)
INITIAL_DELIVERY_SETTINGS = (
    ('collision_preview_house', 'A집', 'sample_cargo_01', INITIAL_A_BASE_FEE, INITIAL_A_DEADLINE),
    ('delivery_house_b', 'B집', 'sample_cargo_02', INITIAL_B_BASE_FEE, INITIAL_B_DEADLINE),
    ('delivery_house_c', 'C집', 'sample_cargo_03', 600, 90.0),
    ('delivery_house_d', 'D집', 'sample_cargo_04', 650, 115.0),
    ('delivery_house_e', 'E집', 'sample_cargo_05', 700, 140.0),
)
SATISFIED_DEADLINE_RATIO = 0.7
SATISFIED_REWARD_MULTIPLIER = 1.2
NORMAL_REWARD_MULTIPLIER = 1.0
DISSATISFIED_REWARD_MULTIPLIER = 0.7


class DeliveryHouse:
    def __init__(self, house_id, x, y, cargo_id, zone_offset, zone_size,
                 base_fee, deadline, label=None):
        self.house_id = house_id
        self.label = label if label is not None else house_id
        self.x = x
        self.y = y
        self.cargo_id = cargo_id
        self.delivered = False
        self.base_fee = base_fee
        self.deadline = deadline
        self.reward = None  # 미정산과 0원 배송을 구분한다.
        self.delivered_mood = None
        # 건물 중심 기준 월드 단위 오프셋과 크기. 충돌 영역과는 별도다.
        self.zone_offset = tuple(zone_offset) if zone_offset is not None else None
        self.zone_size = tuple(zone_size) if zone_size is not None else None

    def get_customer_mood(self, elapsed_time):
        if elapsed_time <= self.deadline * SATISFIED_DEADLINE_RATIO:
            return '만족'
        if elapsed_time <= self.deadline:
            return '보통'
        return '불만'

    def get_zone_bounds(self):
        if self.zone_offset is None or self.zone_size is None:
            return None
        offset_x, offset_y = self.zone_offset
        width, height = self.zone_size
        center_x, center_y = self.x + offset_x, self.y + offset_y
        return (center_x - width / 2, center_y - height / 2,
                center_x + width / 2, center_y + height / 2)

    def contains_position(self, player_x, player_y):
        bounds = self.get_zone_bounds()
        if bounds is None:
            return False
        left, bottom, right, top = bounds
        return left <= player_x <= right and bottom <= player_y <= top

    def can_deliver(self, player_x, player_y):
        return (not self.delivered
                and self.contains_position(player_x, player_y))

    def try_deliver(self, player_x, player_y, cargo_list, elapsed_time):
        if not self.can_deliver(player_x, player_y):
            return False
        cargo = next((cargo for cargo in cargo_list
                      if cargo.cargo_id == self.cargo_id and not cargo.delivered), None)
        if cargo is None:
            return False
        mood = self.get_customer_mood(elapsed_time)
        multiplier = {
            '만족': SATISFIED_REWARD_MULTIPLIER,
            '보통': NORMAL_REWARD_MULTIPLIER,
            '불만': DISSATISFIED_REWARD_MULTIPLIER,
        }[mood]
        # 손상 갱신 후의 내구도로 최종 금액만 버림한다. 완료 후 재정산하지 않는다.
        reward = 0 if cargo.current_durability <= 0.0 else floor(
            self.base_fee * multiplier * cargo.current_durability / cargo.max_durability
        )
        self.reward = reward
        self.delivered_mood = mood
        # 파손 여부와 무관하게 지정 화물과 배송지를 함께 완료한다. 화물은 보관한다.
        cargo.delivered = True
        self.delivered = True
        return True
