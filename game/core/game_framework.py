"""공통 게임 루프와 초 단위 프레임 시간 관리."""

from time import perf_counter


running = False
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


def run(start_mode):
    global running, frame_time, fps, update_ms, draw_ms, render_ms, present_ms

    running = True
    frame_time = 0.0
    fps = update_ms = draw_ms = 0.0
    render_ms = present_ms = 0.0
    sample_time = 0.0
    sample_frames = 0
    try:
        start_mode.init()
        previous_time = perf_counter()

        while running:
            start_mode.handle_events()
            if not running:
                break

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
            start_mode.update()
            update_ended = perf_counter()
            update_ms = update_ms * 0.9 + (update_ended - update_started) * 100
            start_mode.draw()
            # draw에는 update_canvas의 화면 갱신/수직 동기화 대기도 포함된다.
            draw_ms = draw_ms * 0.9 + (perf_counter() - update_ended) * 100
    finally:
        running = False
        start_mode.finish()
