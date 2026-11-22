"""골목길 퀵배송 실행 진입점."""

from pico2d import close_canvas, open_canvas

from game.core import game_framework
from game.modes import title_mode
from game.config import settings
from game.config.user_settings import load_screen_mode
from game.core.display import set_fullscreen


def main():
    open_canvas(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, sync=True)
    try:
        if load_screen_mode() and not set_fullscreen(True):
            print('저장된 전체화면 설정을 적용하지 못했습니다. 창 모드로 시작합니다.')
        game_framework.run(title_mode)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
