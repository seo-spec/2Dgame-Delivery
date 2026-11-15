"""공통 게임 루프와 초 단위 프레임 시간 관리."""

from time import perf_counter


running = False
frame_time = 0.0


def quit():
    global running
    running = False


def run(start_mode):
    global running, frame_time

    running = True
    frame_time = 0.0
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

            start_mode.update()
            start_mode.draw()
    finally:
        running = False
        start_mode.finish()
