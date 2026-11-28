"""렌더러 없이 검증하는 정적 지면 캐시 저장·복원·폴백 회귀 검사."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zlib

from game.world import ground_cache


class GroundCacheTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(dir=ground_cache.ROOT / '.tmp')
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.path = root / 'local' / 'sample.rgba.z'
        self.bundle = root / 'bundle'
        self.bundle.mkdir()
        replacement = patch.object(ground_cache, 'BUNDLED_CACHE_DIR', self.bundle)
        replacement.start()
        self.addCleanup(replacement.stop)
        self.payload = bytes(range(256)) * 4

    def test_missing_is_cache_miss(self):
        self.assertIsNone(ground_cache.read_pixels(self.path, len(self.payload)))

    def test_write_read_round_trip(self):
        self.assertTrue(ground_cache.write_pixels(self.path, self.payload))
        self.assertEqual(ground_cache.read_pixels(self.path, len(self.payload)), self.payload)

    def test_corrupt_local_uses_bundle(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b'broken')
        (self.bundle / self.path.name).write_bytes(zlib.compress(self.payload))
        self.assertEqual(ground_cache.read_pixels(self.path, len(self.payload)), self.payload)

    def test_valid_local_has_priority(self):
        self.assertTrue(ground_cache.write_pixels(self.path, self.payload))
        (self.bundle / self.path.name).write_bytes(zlib.compress(b'x' * len(self.payload)))
        self.assertEqual(ground_cache.read_pixels(self.path, len(self.payload)), self.payload)

    def test_invalid_size_checksum_or_trailing_data_is_rejected(self):
        self.path.parent.mkdir()
        packed = zlib.compress(self.payload)
        for invalid in (zlib.compress(self.payload + b'x'),
                        zlib.compress(self.payload[:-1]), packed[:-1], packed + b'extra'):
            with self.subTest(length=len(invalid)):
                self.path.write_bytes(invalid)
                self.assertIsNone(ground_cache.read_pixels(self.path, len(self.payload)))

    def test_unwritable_parent_reports_failure(self):
        self.path.parent.write_bytes(b'not a directory')
        self.assertFalse(ground_cache.write_pixels(self.path, self.payload))
