"""시작 시 복원과 옵션 화면이 공유하는 화면 모드 전환."""

from importlib import import_module

from pico2d import get_canvas_height, get_canvas_width


_pico = import_module('pico2d.pico2d')


def is_fullscreen():
    return bool(_pico.SDL_GetWindowFlags(_pico.window) & _pico.SDL_WINDOW_FULLSCREEN)


def set_fullscreen(enabled):
    # SDL 논리 좌표는 출력과 마우스 판정을 같은 캔버스 크기로 유지한다.
    result = _pico.SDL_RenderSetLogicalSize(
        _pico.renderer, get_canvas_width(), get_canvas_height(),
    )
    if result != 0:
        return False
    flags = _pico.SDL_WINDOW_FULLSCREEN_DESKTOP if enabled else 0
    return _pico.SDL_SetWindowFullscreen(_pico.window, flags) == 0
