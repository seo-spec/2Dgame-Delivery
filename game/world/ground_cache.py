"""정적 지면의 RGBA 결과만 저장한다. 렌더러·충돌 데이터는 캐시하지 않는다."""

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import zlib


ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / '.tmp/ground-cache'


def cache_path(road_map, config):
    signature = getattr(road_map, '_ground_cache_signature', None)
    if signature is None:
        digest = sha256(b'ground-rgba-v1')
        for filename in ('road_finish.py', 'ground_materials.py', 'road_geometry.py',
                         'road_surface.py', 'start_scene_art.py', 'ground_cache.py'):
            digest.update((ROOT / 'game/world' / filename).read_bytes())
        digest.update((ROOT / 'game/config/settings.py').read_bytes())
        digest.update(json.dumps(road_map.config, sort_keys=True).encode('utf-8'))
        digest.update(json.dumps([road_map.width, road_map.height,
                                  road_map.road_surface.rectangles]).encode('utf-8'))
        signature = digest.hexdigest()
        road_map._ground_cache_signature = signature
    key = sha256((signature + json.dumps(config, sort_keys=True)).encode('utf-8')).hexdigest()
    return CACHE_DIR / (key + '.rgba.z')


def read_pixels(path, expected_size):
    try:
        # 압축 체크섬과 크기를 확인하고 손상/불완전 캐시는 다시 생성한다.
        with path.open('rb') as stream:
            packed = stream.read(expected_size + 65537)
        if len(packed) > expected_size + 65536:
            return None
        decoder = zlib.decompressobj()
        pixels = decoder.decompress(packed, expected_size + 1)
        if (len(pixels) != expected_size or not decoder.eof
                or decoder.unused_data or decoder.unconsumed_tail):
            return None
        return pixels
    except (OSError, zlib.error):
        return None


def write_pixels(path, pixels):
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='ground-',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(zlib.compress(pixels, level=1))
        temporary.replace(path)
    except OSError:
        # 읽기 전용 설치/디스크 부족이어도 현재 합성 결과로 플레이한다.
        pass
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
