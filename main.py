"""골목길 퀵배송 실행 진입점."""

from pico2d import close_canvas, open_canvas

from game.core import game_framework
from game.modes import play_mode
from game.config import settings


def main():
    open_canvas(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, sync=True)
    try:
        game_framework.run(play_mode)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
