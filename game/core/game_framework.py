"""공통 게임 루프와 초 단위 프레임 시간 관리."""

from time import perf_counter


running = False
current_mode = None
next_mode = None
frame_time = 0.0
fps = 0.0
update_ms = 0.0
draw_ms = 0.0
render_ms = 0.0
present_ms = 0.0


def record_render_times(render_seconds, present_seconds):
    global render_ms, present_ms
    render_ms = render_ms * 0.9 + render_seconds * 100
    present_ms = present_ms * 0.9 + present_seconds * 100


def quit():
    global running
    running = False


def change_mode(mode):
    """입력 처리가 끝난 뒤 전환할 모드를 예약한다."""
    global next_mode
    next_mode = mode


def run(start_mode):
    global running, frame_time, fps, update_ms, draw_ms, render_ms, present_ms
    global current_mode, next_mode

    running = True
    current_mode = start_mode
    next_mode = None
    frame_time = 0.0
    fps = update_ms = draw_ms = 0.0
    render_ms = present_ms = 0.0
    sample_time = 0.0
    sample_frames = 0
    try:
        current_mode.init()
        previous_time = perf_counter()

        while running:
            current_mode.handle_events()
            if not running:
                break

            if next_mode is not None:
                departing_mode = current_mode
                current_mode = None
                departing_mode.finish()
                current_mode = next_mode
                next_mode = None
                current_mode.init()
                # 새 모드의 로딩 시간이 첫 업데이트에 누적되지 않게 한다.
                previous_time = perf_counter()
                sample_time = 0.0
                sample_frames = 0

            current_time = perf_counter()
            frame_time = current_time - previous_time
            previous_time = current_time
            sample_time += frame_time
            sample_frames += 1
            if sample_time >= 0.5:
                fps = sample_frames / sample_time
                sample_time = 0.0
                sample_frames = 0

            update_started = perf_counter()
            current_mode.update()
            update_ended = perf_counter()
            update_ms = update_ms * 0.9 + (update_ended - update_started) * 100
            current_mode.draw()
            # draw에는 update_canvas의 화면 갱신/수직 동기화 대기도 포함된다.
            draw_ms = draw_ms * 0.9 + (perf_counter() - update_ended) * 100
    finally:
        running = False
        try:
            if current_mode is not None:
                current_mode.finish()
        finally:
            current_mode = None
            next_mode = None
