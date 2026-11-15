"""배송 단계의 진행 상태와 시간·목표 판정."""

from enum import Enum

from settings import STAGE_1_TARGET_REVENUE, STAGE_1_TIME_LIMIT


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

    def evaluate(self, delivery_houses, total_revenue):
        if self.state != StageState.DELIVERING:
            return
        all_delivered = bool(delivery_houses) and all(house.delivered for house in delivery_houses)
        # 마지막 배송의 정산까지 반영한 후 성공을 먼저 판단한다. 경계 시각도 포함한다.
        if all_delivered and total_revenue >= self.target_revenue and self.can_deliver():
            self.state = StageState.RETURNING
        elif all_delivered and total_revenue < self.target_revenue:
            self.failure_reason = '전량 배송했지만 목표 수익이 부족합니다'
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
