"""골목길 퀵배송 실행 진입점."""

from pico2d import close_canvas, open_canvas

import game_framework
import play_mode
import settings


def main():
    open_canvas(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, sync=True)
    try:
        game_framework.run(play_mode)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
