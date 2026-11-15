"""배송 단계의 진행 상태와 시간·목표 판정."""

from enum import Enum
from math import floor

from game.systems.delivery import SATISFIED_REWARD_MULTIPLIER
from game.config.settings import STAGE_1_TARGET_REVENUE, STAGE_1_TIME_LIMIT


class StageState(Enum):
    WAITING = '수령 대기'
    DELIVERING = '배송 중'
    RETURNING = '복귀 중'
    CLEAR = '클리어'
    FAILED = '실패'


class GameController:
    def __init__(self, time_limit=STAGE_1_TIME_LIMIT, target_revenue=STAGE_1_TARGET_REVENUE):
        self.time_limit = time_limit
        self.target_revenue = target_revenue
        self.state = StageState.WAITING
        self.elapsed_time = 0.0
        self.failure_reason = ''
        self.remaining_max_revenue = 0

    def start_delivery(self):
        if self.state != StageState.WAITING:
            return False
        self.elapsed_time = 0.0
        self.state = StageState.DELIVERING
        return True

    def advance_time(self, dt):
        if self.state == StageState.DELIVERING:
            self.elapsed_time += dt

    def can_deliver(self):
        return (self.state == StageState.DELIVERING
                and self.elapsed_time <= self.time_limit)

    def evaluate(self, delivery_houses, total_revenue, cargo_list):
        if self.state != StageState.DELIVERING:
            return
        all_delivered = bool(delivery_houses) and all(house.delivered for house in delivery_houses)
        # 마지막 배송의 정산까지 반영한 후 성공을 먼저 판단한다. 경계 시각도 포함한다.
        if all_delivered and total_revenue >= self.target_revenue and self.can_deliver():
            self.state = StageState.RETURNING
            return
        cargo_by_id = {cargo.cargo_id: cargo for cargo in cargo_list}
        self.remaining_max_revenue = 0
        for house in delivery_houses:
            cargo = cargo_by_id.get(house.cargo_id)
            if house.delivered or cargo is None or cargo.delivered or cargo.current_durability <= 0.0:
                continue
            # 현재 기분과 관계없이 만족 배율을 상한으로 사용하고 건별로 한 번 버린다.
            self.remaining_max_revenue += floor(
                house.base_fee * SATISFIED_REWARD_MULTIPLIER
                * cargo.current_durability / cargo.max_durability
            )
        if total_revenue + self.remaining_max_revenue < self.target_revenue:
            self.failure_reason = '화물 손상 또는 배송 수익 부족으로 목표 달성 불가'
            self.state = StageState.FAILED
        elif self.elapsed_time > self.time_limit:
            self.failure_reason = '배송 시간 초과'
            self.state = StageState.FAILED

    def check_return(self, player_x, player_y, return_bounds):
        if self.state != StageState.RETURNING:
            return False
        left, bottom, right, top = return_bounds
        if left <= player_x <= right and bottom <= player_y <= top:
            self.state = StageState.CLEAR
            return True
        return False
