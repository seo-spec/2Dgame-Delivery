"""추가 환경 물체가 도로·입구·기존 물체를 막지 않는지 검사한다."""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from game.world.camera import Camera
from game.world.road_map import RoadMap
from game.world.road_geometry import SIDEWALK_COLOR
from game.world.start_scene_art import get_asset_spec


ROOT = Path(__file__).resolve().parents[1]


def overlaps(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def expand(a, margin):
    return a[0]-margin, a[1]-margin, a[2]+margin, a[3]+margin


class DensityLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 지면 업로드만 생략한다. 도로 도형·맵 데이터는 실제 코드를 사용한다.
        with patch('game.world.road_map.RoadFinish', side_effect=OSError('지면 업로드 생략')):
            with redirect_stdout(StringIO()):
                cls.map = RoadMap(Camera())
        cls.config = cls.map.config
        cls.items = cls.config['density_props']
        cls.frames = json.loads((ROOT/'assets/images/title_match_v2/frames.json').read_text())

    @classmethod
    def bounds(cls, item):
        x, y = item['position']
        w, h = item['size']
        filename, _ = get_asset_spec(item.get('asset', 'building'), item.get('id'))
        frame = cls.frames[filename]
        rx, ry, rw, rh = frame['reference_rect']
        fw, fh = frame['reference_size']
        rect = (x+(rx/fw-.5)*w, y+(.5-(ry+rh)/fh)*h,
                x+((rx+rw)/fw-.5)*w, y+(.5-ry/fh)*h)
        collider = item['collision']
        cx, cy = x+collider['offset'][0], y+collider['offset'][1]
        cw, ch = collider['size']
        return (min(rect[0], cx-cw/2), min(rect[1], cy-ch/2),
                max(rect[2], cx+cw/2), max(rect[3], cy+ch/2))

    def test_unique_visible_colliding_objects(self):
        ids = [item['id'] for item in self.items]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        for item in self.items:
            self.assertTrue(item['id'].startswith('density_'))
            self.assertTrue(all(size > 0 for size in item['collision']['size']))
            left, bottom, right, top = self.bounds(item)
            self.assertTrue(0 <= left < right <= self.map.width)
            self.assertTrue(0 <= bottom < top <= self.map.height)

    def test_road_and_sidewalk_clearance(self):
        roads = list(self.map.road_surface.rectangles)
        for tx, ty, connection in self.map.tiles:
            roads.extend((tx*self.map.tile_size+l, ty*self.map.tile_size+b,
                          tx*self.map.tile_size+r+1, ty*self.map.tile_size+t+1)
                         for l,b,r,t,color in self.map.geometry.tiles[connection]
                         if color == SIDEWALK_COLOR)
        roads.extend(tuple(path['bounds']) for path in self.config.get('access_paths', []))
        for item in self.items:
            with self.subTest(item=item['id']):
                self.assertFalse(any(overlaps(expand(self.bounds(item), 12), road) for road in roads))

    def test_delivery_zones_and_approaches_remain_open(self):
        reserved = []
        for building in self.config['buildings']:
            for key in ('pickup_zone', 'delivery_zone'):
                zone = building.get(key)
                if zone is None:
                    continue
                x, y = (building['position'][i]+zone['offset'][i] for i in (0, 1))
                w, h = zone['size']
                reserved.append((x-w/2-48, y-h/2-48, x+w/2+48, y+h/2+48))
                points = [(max(l, min(r, x)), max(b, min(t, y)))
                          for l,b,r,t in self.map.road_surface.rectangles]
                px, py = min(points, key=lambda p: (p[0]-x)**2+(p[1]-y)**2)
                reserved.append((min(x,px)-48, min(y,py)-48, max(x,px)+48, max(y,py)+48))
        for item in self.items:
            self.assertFalse(any(overlaps(self.bounds(item), rect) for rect in reserved), item['id'])

    def test_no_overlap_with_existing_or_new_objects(self):
        occupied = [self.bounds(item) for item in self.config['buildings']+self.config['props']]
        for item in self.items:
            rect = self.bounds(item)
            self.assertFalse(any(overlaps(expand(rect, 12), other) for other in occupied), item['id'])
            occupied.append(rect)

    def test_spawn_and_parking_remain_clear(self):
        x,y = self.map.spawn
        reserved = [(x-100,y-100,x+100,y+100)]
        reserved += [expand(rect, 32) for rect in
                     self.config['road_finish']['neighborhood']['parking_bays']]
        for item in self.items:
            self.assertFalse(any(overlaps(self.bounds(item), rect) for rect in reserved), item['id'])
