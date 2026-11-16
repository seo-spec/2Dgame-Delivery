"""실제 신호 객체로 벌금의 방향·시간·중복·교차로 경계를 검증한다."""

import unittest
from types import SimpleNamespace

from game.systems.traffic_penalties import TrafficPenalties
from game.world.traffic_signal import TrafficSignal


class TrafficPenaltyTests(unittest.TestCase):
    def setUp(self):
        self.signals = [TrafficSignal(None, (0, 0), direction, 120, 14)
                        for direction in ((1, 0), (0, 1), (-1, 0), (0, -1))]
        self.penalties = TrafficPenalties(self.signals)
        self.bike = SimpleNamespace(x=0, y=0, collision_radius=37, speed=210, angle=0)

    def step(self, previous, position, clock=5.0, dt=0.1, delivering=True):
        for signal in self.signals:
            signal.elapsed = clock % 8
            signal.state = signal.state_at(clock)
        self.bike.x, self.bike.y = position
        return self.penalties.update(dt, previous, self.bike, delivering)

    def test_all_directions_and_both_lanes(self):
        for fx, fy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            for lane in (-30, 0, 30):
                for red in (False, True):
                    with self.subTest(direction=(fx, fy), lane=lane, red=red):
                        self.setUp()
                        clock = (5 if red else 1) if fx else (1 if red else 5)
                        previous = (-110 * fx + lane * fy, -110 * fy - lane * fx)
                        position = (-90 * fx + lane * fy, -90 * fy - lane * fx)
                        self.assertEqual(self.step(previous, position, clock), 100 if red else 0)

    def test_green_entry_then_red_inside(self):
        self.assertEqual(self.step((-110, 0), (-90, 0), clock=1), 0)
        self.assertEqual(self.step((-90, 0), (-50, 0), clock=5), 0)
        self.assertEqual(self.step((-50, 0), (20, 0), clock=5.1), 0)
        self.assertEqual(self.penalties.total_fines, 0)

    def test_red_entry_charges_once_and_notice(self):
        self.assertEqual(self.step((-110, 0), (-90, 0)), 100)
        self.assertEqual(self.step((-90, 0), (-50, 0)), 0)
        self.assertEqual(self.step((-50, 0), (-50, 0)), 0)
        self.assertEqual(self.penalties.violation_count, 1)
        self.assertAlmostEqual(self.penalties.notice_remaining, 2.8)

    def test_small_reverse_then_reentry_is_same_visit(self):
        self.assertEqual(self.step((-110, 0), (-90, 0)), 100)
        self.step((-90, 0), (-100, 0))
        self.assertEqual(self.step((-100, 0), (-90, 0)), 0)

    def test_full_exit_allows_another_fine(self):
        self.assertEqual(self.step((-110, 0), (-90, 0)), 100)
        self.step((-90, 0), (-120, 0))
        self.assertEqual(self.step((-120, 0), (-90, 0)), 100)

    def test_waiting_and_returning_are_not_fined(self):
        self.assertEqual(self.step((-110, 0), (-90, 0), delivering=False), 0)
        self.assertEqual(self.penalties.total_fines, 0)

    def test_fast_crossing_uses_entry_time(self):
        # 프레임 3.9~4.1초의 0.325 지점에서 진입하므로 초록불이다.
        self.assertEqual(self.step((-110, 0), (-70, 0), clock=4.1, dt=0.2), 0)
        self.setUp()
        # 같은 프레임의 0.65 지점에서 진입하므로 빨간불이다.
        self.assertEqual(self.step((-110, 0), (-90, 0), clock=4.1, dt=0.2), 100)

    def test_cycle_wrap_uses_entry_time(self):
        self.assertEqual(self.step((-110, 0), (-70, 0), clock=8.1, dt=0.2), 100)

    def test_shoulder_corner_entry_is_detected(self):
        # 차체가 도로 가장자리에서 걸쳐 들어갈 때도 교차로와 실제로 접촉한다.
        self.assertEqual(self.step((-130, 70), (-50, 70)), 100)

    def test_pass_outside_intersection_is_not_fined(self):
        self.assertEqual(self.step((-130, 110), (130, 110)), 0)

    def test_no_movement_or_already_inside_is_not_fined(self):
        self.assertEqual(self.step((0, 0), (0, 0)), 0)
        self.assertEqual(self.step((0, 0), (40, 0)), 0)

    def test_signal_has_no_collision(self):
        self.assertTrue(all(signal.get_collision_bounds() is None for signal in self.signals))


if __name__ == '__main__':
    unittest.main()
