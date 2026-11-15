"""레이어별 게임 객체 등록, 갱신, 그리기 관리."""


BACKGROUND = 0
ACTORS = 1
FOREGROUND = 2

world = [[], [], []]


def add_object(obj, depth=ACTORS):
    if not 0 <= depth < len(world):
        raise ValueError("Invalid drawing layer")
    if any(obj is existing for layer in world for existing in layer):
        raise ValueError("Object is already registered")
    world[depth].append(obj)


def remove_object(obj):
    for layer in world:
        for index, existing in enumerate(layer):
            if existing is obj:
                del layer[index]
                return
    raise ValueError("Cannot remove an unregistered object")


def clear():
    for layer in world:
        layer.clear()


def update():
    # 순회 시작 시 목록을 고정해 새 객체는 다음 갱신부터 처리한다.
    objects = [(layer, obj) for layer in world for obj in layer]
    for layer, obj in objects:
        if any(obj is existing for existing in layer):
            obj.update()


def render():
    objects = [(layer, obj) for layer in world for obj in layer]
    for layer, obj in objects:
        if any(obj is existing for existing in layer):
            obj.draw()
