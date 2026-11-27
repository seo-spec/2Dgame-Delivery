"""pico2d와 같은 글자 배치를 유지하면서 반복 문구의 텍스처를 재사용한다."""

from collections import OrderedDict
from importlib import import_module

# 패키지에 복사된 renderer 값 대신 실제 캔버스를 관리하는 모듈을 참조한다.
_pico = import_module('pico2d.pico2d')


class CachedFont:
    def __init__(self, path, size=18, capacity=256):
        self.capacity = capacity
        self.images = OrderedDict()
        self.font = _pico.TTF_OpenFont(str(path).encode('utf-8'), size)
        if not self.font:
            raise OSError(f'폰트를 불러올 수 없습니다: {path}')

    def draw(self, x, y, text, color=(0, 0, 0), max_width=None):
        if not text or not self.font:
            return
        key = text, tuple(color)
        image = self.images.pop(key, None)
        if image is None:
            surface = _pico.TTF_RenderUTF8_Blended(self.font, text.encode('utf-8'), _pico.SDL_Color(*color))
            if not surface:
                return
            try:
                texture = _pico.SDL_CreateTextureFromSurface(_pico.renderer, surface)
            finally:
                _pico.SDL_FreeSurface(surface)
            if not texture:
                return
            image = _pico.Image(texture)
        self.images[key] = image
        if len(self.images) > self.capacity:
            self.images.popitem(last=False)
        # pico2d.Font.draw와 동일: x는 왼쪽, y는 이미지 중심 높이.
        # 폭 제한은 표시 배율만 바꾼다. 원본 텍스처와 캐시 키는 그대로 재사용한다.
        scale = min(1.0, max(0.0, max_width) / image.w) if max_width is not None else 1.0
        image.draw(x + image.w * scale / 2, y, image.w * scale, image.h * scale)

    def close(self):
        self.images.clear()
        if self.font:
            _pico.TTF_CloseFont(self.font)
            self.font = None
