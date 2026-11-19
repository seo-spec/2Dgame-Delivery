"""현재 타이틀을 5초 준비 후 60초 측정하는 선택 실행 진입점."""

import argparse
import json
import math
import platform
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from time import perf_counter


MAX_SAMPLES = 65536


def summarize(values):
    ordered = sorted(values)
    return {
        'mean_ms': sum(ordered) / len(ordered) * 1000,
        'p95_ms': ordered[math.ceil(len(ordered) * 0.95) - 1] * 1000,
        'max_ms': ordered[-1] * 1000,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.tmp/title_baseline.json'))
    parser.add_argument('--cpu', default='unrecorded')
    parser.add_argument('--gpu', default='unrecorded')
    parser.add_argument('--refresh-hz', default='unrecorded')
    args = parser.parse_args()

    import pico2d
    import main as application
    from game.config import settings
    from game.core import game_framework
    from game.modes import title_mode

    original_init = title_mode.init
    original_update = title_mode.update
    original_draw = title_mode.draw
    original_present = title_mode.update_canvas
    original_events = title_mode.handle_events
    samples = []
    started = None
    previous_present = None
    update_seconds = 0.0
    present_seconds = 0.0
    load_seconds = None
    image_draw_count = 0
    status = 'interrupted'
    try:
        pico_version = metadata.version('pico2d')
    except metadata.PackageNotFoundError:
        pico_version = getattr(pico2d, '__version__', 'unrecorded')

    def measured_init():
        nonlocal load_seconds, started, previous_present, image_draw_count
        before = perf_counter()
        original_init()
        started = perf_counter()
        previous_present = started
        load_seconds = started - before
        image_draw_count = 1 + len(getattr(title_mode, 'traffic', ()))

    def measured_update():
        nonlocal update_seconds
        before = perf_counter()
        original_update()
        update_seconds = perf_counter() - before

    def measured_events():
        original_events()
        if game_framework.next_mode is not None:
            game_framework.quit()

    def measured_present():
        nonlocal present_seconds
        before = perf_counter()
        original_present()
        present_seconds = perf_counter() - before

    def measured_draw():
        nonlocal previous_present, status
        before = perf_counter()
        original_draw()
        completed = perf_counter()
        render_seconds = max(0.0, completed - before - present_seconds)
        game_framework.record_render_times(render_seconds, present_seconds)
        # 준비 구간과 겹친 첫 프레임은 제외한다.
        if previous_present >= started + 5.0:
            if len(samples) == MAX_SAMPLES:
                status = 'sample_capacity_exceeded'
                game_framework.quit()
                return
            samples.append((completed - previous_present, update_seconds,
                            render_seconds, present_seconds))
        previous_present = completed
        if completed >= started + 65.0:
            status = 'complete'
            game_framework.quit()

    title_mode.init = measured_init
    title_mode.update = measured_update
    title_mode.draw = measured_draw
    title_mode.update_canvas = measured_present
    title_mode.handle_events = measured_events
    print('타이틀 측정 시작 — 5초 준비 + 60초 수집. 창을 전경에 유지하고 입력하지 마세요.')
    try:
        application.main()
    except BaseException:
        status = 'error'
        raise
    finally:
        title_mode.init = original_init
        title_mode.update = original_update
        title_mode.draw = original_draw
        title_mode.update_canvas = original_present
        title_mode.handle_events = original_events
        report = {
            'status': status,
            'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
            'environment': {
                'python': platform.python_version(), 'platform': platform.platform(),
                'pico2d_version': pico_version, 'pico2d_path': pico2d.__file__,
                'cpu': args.cpu, 'gpu': args.gpu, 'refresh_hz': args.refresh_hz,
                'window': [settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT],
                'vsync_requested': True,
            },
            'warmup_seconds': 5, 'requested_sample_seconds': 60,
            'sample_capacity': MAX_SAMPLES, 'sample_count': len(samples),
            'title_init_ms': None if load_seconds is None else load_seconds * 1000,
            'background_image_draws_per_frame': 1,
            'title_image_draws_per_frame': image_draw_count,
            'notes': 'CPU wall time. Render includes menu, excludes update_canvas. '
                     'Present includes submission/vsync wait. GPU execution time is unmeasured.',
        }
        if samples:
            elapsed = sum(row[0] for row in samples)
            report['sample_seconds'] = elapsed
            report['average_fps'] = len(samples) / elapsed
            for column, label in enumerate(('frame', 'update', 'render', 'present')):
                report[label] = summarize([row[column] for row in samples])
            report['update_plus_render'] = summarize([row[1] + row[2] for row in samples])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'측정 상태 {status}, 결과 {args.output.resolve()}')


if __name__ == '__main__':
    main()
