"""창을 열지 않고 실행하는 도로 합집합 및 실제 맵 경계 검사."""

import math
import unittest

from game.world.road_geometry import RoadGeometry
from game.world.road_map import RoadMap
from game.world.road_surface import RoadSurface


def tile_surface(mask, size=300):
    geometry = RoadGeometry(size)
    return RoadSurface((l, b, r + 1, t + 1)
                       for l, b, r, t in geometry.road_tiles[mask])


class RoadSurfaceTests(unittest.TestCase):
    def test_union_across_seam(self):
        surface = RoadSurface([(0, 0, 10, 10), (10, 0, 20, 10)])
        self.assertTrue(surface.contains_circle(10, 5, 5))
        self.assertFalse(surface.contains_circle(10, 5, 5.001))

    def test_interior_hole_and_small_gap(self):
        surface = RoadSurface([(0, 0, 20, 9), (0, 11, 20, 20),
                               (0, 9, 9, 11), (11, 9, 20, 11)])
        self.assertFalse(surface.contains_circle(10, 10, 8))
        gap = RoadSurface([(0, 0, 10, 20), (10.001, 0, 20, 20)])
        self.assertFalse(gap.contains_circle(10, 10, 5))

    def test_straight_and_sidewalk(self):
        surface = tile_surface(5)
        self.assertTrue(surface.contains_circle(150, 150, 60))
        self.assertFalse(surface.contains_circle(150, 150, 60.001))
        self.assertFalse(surface.contains_point(85, 150))
        self.assertTrue(surface.contains_point(90, 150))
        self.assertFalse(surface.contains_circle(95, 150, 6))

    def test_cross_and_t_junction(self):
        cross = tile_surface(15)
        self.assertTrue(cross.contains_circle(150, 150, 80))
        self.assertFalse(cross.contains_circle(150, 150, 86))
        tee = tile_surface(11)
        self.assertTrue(tee.contains_point(150, 250))
        self.assertFalse(tee.contains_point(150, 50))

    def test_curve_and_rotations(self):
        for mask, x, y in [(3, 194, 194), (9, 106, 194),
                           (12, 106, 106), (6, 194, 106)]:
            with self.subTest(mask=mask):
                surface = tile_surface(mask)
                self.assertTrue(surface.contains_circle(x, y, 20))
                self.assertFalse(surface.contains_circle(x, y, 62))
                self.assertFalse(surface.contains_point(150, 150))

    def test_dead_end(self):
        surface = tile_surface(4)
        self.assertTrue(surface.contains_circle(150, 150, 59))
        self.assertTrue(surface.contains_point(150, 205))
        self.assertFalse(surface.contains_point(150, 211))
        self.assertFalse(surface.contains_circle(150, 205, 10))

    def test_invalid_and_zero_radius(self):
        surface = RoadSurface([(0, 0, 10, 10)])
        self.assertTrue(surface.contains_circle(0, 0, 0))
        for radius in (-1, math.nan, math.inf):
            self.assertFalse(surface.contains_circle(5, 5, radius))
        self.assertFalse(surface.contains_point(math.nan, 5))
        self.assertFalse(RoadSurface([]).contains_circle(0, 0, 1))

    def test_actual_map_seam_access_path_and_bounds(self):
        road_map = RoadMap(None)
        self.assertTrue(road_map.is_circle_on_road(900, 450, 40))
        self.assertFalse(road_map.is_circle_on_road(900, 450, 61))
        self.assertTrue(road_map.is_circle_on_road(750, 390, 30))
        self.assertTrue(road_map.is_point_on_road(750, 300))
        self.assertFalse(road_map.is_point_on_road(692, 300))
        self.assertFalse(road_map.is_point_on_road(-1, 450))


if __name__ == '__main__':
    unittest.main()
