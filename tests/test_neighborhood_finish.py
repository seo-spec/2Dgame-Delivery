"""출발지 정적 바닥이 주행·상호작용 여백을 침범하지 않는지 확인한다."""

from types import SimpleNamespace
import unittest

from game.world.neighborhood_finish import paint_neighborhood


class NeighborhoodFinishTests(unittest.TestCase):
    def setUp(self):
        self.finish = SimpleNamespace(left=0, bottom=0, width=12, height=12)
        self.original = bytes((130, 150, 90, 255)) * 144
        self.layout = {'bounds': [2, 2, 10, 10],
                       'surfaces': [{'bounds': [0, 0, 12, 12], 'material': 'stone'}],
                       'parking_bays': [[0, 0, 12, 12]]}

    def render(self, road=None, quiet=None, sidewalk=None):
        pixels = bytearray(self.original)
        blank = bytearray(144)
        paint_neighborhood(self.finish, pixels, road if road is not None else blank,
                           quiet if quiet is not None else blank,
                           sidewalk if sidewalk is not None else blank,
                           self.layout, lambda: None)
        return pixels

    def test_area_outside_selected_block_is_unchanged(self):
        pixels = self.render()
        for y in range(12):
            for x in range(12):
                if not (2 <= x < 10 and 2 <= y < 10):
                    offset = ((11 - y) * 12 + x) * 4
                    self.assertEqual(pixels[offset:offset + 4], self.original[offset:offset + 4])
        self.assertNotEqual(pixels, self.original)

    def test_road_sidewalk_and_interaction_masks_are_preserved(self):
        for protected in ('road', 'quiet', 'sidewalk'):
            with self.subTest(protected=protected):
                self.assertEqual(self.render(**{protected: bytearray([1] * 144)}), self.original)

    def test_alpha_is_preserved(self):
        pixels = self.render()
        self.assertEqual(pixels[3::4], self.original[3::4])

    def test_no_layout_does_not_modify_pixels(self):
        self.layout = None
        self.assertEqual(self.render(), self.original)

    def test_overlapping_paving_has_no_internal_outline(self):
        self.layout = {'bounds': [0, 0, 12, 12], 'surfaces': [
            {'bounds': [0, 0, 12, 12], 'material': 'stone'}]}
        expected = self.render()
        self.layout['surfaces'] = [
            {'bounds': [0, 0, 8, 12], 'material': 'stone'},
            {'bounds': [4, 0, 12, 12], 'material': 'stone'},
        ]
        self.assertEqual(self.render(), expected)

    def test_tree_island_fades_into_underlying_paving(self):
        self.finish = SimpleNamespace(left=0, bottom=0, width=32, height=32)
        self.original = bytes((130, 150, 90, 255)) * 1024
        self.layout = {'bounds': [0, 0, 32, 32], 'surfaces': [
            {'bounds': [0, 0, 32, 32], 'material': 'stone'}]}
        blank = bytearray(1024)
        def draw():
            pixels = bytearray(self.original)
            paint_neighborhood(self.finish, pixels, blank, blank, blank, self.layout, lambda: None)
            return pixels
        base = draw()
        self.layout['surfaces'].append(
            {'bounds': [4, 4, 28, 28], 'material': 'garden', 'shape': 'ellipse'})
        pixels = draw()
        def difference(x, y):
            offset = ((31 - y) * 32 + x) * 4
            return sum(abs(pixels[offset + c] - base[offset + c]) for c in range(3))
        self.assertEqual(difference(2, 16), 0)
        self.assertGreater(difference(4, 16), 0)
        self.assertLess(difference(4, 16), difference(16, 16))
        self.assertEqual(pixels[3::4], base[3::4])
