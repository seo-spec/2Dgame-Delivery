"""골목길 퀵배송 실행 진입점."""

from pico2d import close_canvas, open_canvas

import game_framework
import play_mode


# 초기 개발용 크기. 최종 해상도는 추후 결정한다.
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


def main():
    open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT, sync=True)
    try:
        game_framework.run(play_mode)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
