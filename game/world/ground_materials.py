"""월드2px 격자에 놓는 낮은 대비의 풀 덩어리와 아스팔트 자국."""

from game.world.road_geometry import GRASS_COLOR


# 점 노이즈 대신 윤곽과 밝은 잎면을 가진 작은 덩어리를 사용한다.
# '.'은 바탕, s는 낮은 잎면, +는 밝은 잎면, v는 풀잎의 이음부다.
GRASS_PATCHES = (
    (
        '................', '....ss..........', '...s++s...ss....',
        '..ss++ss.s++s...', '...svsss.s++ss..', '....ss..ssvss...',
        '..ss...s++ss....', '.s++s.ss++ss....', '.ssvss.svss.....',
        '..sss...ss......', '................',
    ),
    (
        '................', '.........ss.....', '..ss....s++s....',
        '.s++ss..svss....', '..svss...ss.....', '...sss.ss.......',
        '......s++ss.....', '.....ss++vs.....', '......ssss......',
        '................', '................',
    ),
    (
        '................', '......ss........', '.....s++s.......',
        '..ss.ss+vs......', '.s++s.ssss......', '.ssvs....ss.....',
        '..sss...s++ss...', '........svsss...', '.........ss.....',
        '................', '................',
    ),
)
GRASS_OFFSETS = {'.': 0, 's': -2, '+': 4, 'v': -6}
ASPHALT_SCUFF = ('........', '..sss...', '.ss..s..', '........')


def grass_color(wx, wy, quiet=False):
    gx, gy = wx // 2, wy // 2
    if quiet:
        return GRASS_COLOR
    cell_x, local_x = divmod(gx, 32)
    cell_y, local_y = divmod(gy, 32)
    seed = (cell_x * 73856093) ^ (cell_y * 19349663)
    if seed % 4 == 0:
        return GRASS_COLOR
    patch = GRASS_PATCHES[(seed >> 3) % len(GRASS_PATCHES)]
    x = local_x - (2 + (seed >> 6 & 7))
    y = local_y - (3 + (seed >> 10 & 7))
    if not (0 <= x < 16 and 0 <= y < len(patch)):
        return GRASS_COLOR
    if seed & 1:
        x = 15 - x
    shade = GRASS_OFFSETS[patch[y][x]]
    return tuple(channel + shade for channel in GRASS_COLOR)


def asphalt_shade(wx, wy, quiet=False):
    if quiet:
        return 0
    cell_x, local_x = divmod(wx // 2, 64)
    cell_y, local_y = divmod(wy // 2, 64)
    seed = (cell_x * 83492791) ^ (cell_y * 19349663)
    if seed % 4:
        return 0
    x = local_x - (8 + (seed >> 5 & 31))
    y = local_y - (8 + (seed >> 10 & 31))
    if 0 <= x < 8 and 0 <= y < 4 and ASPHALT_SCUFF[y][x] == 's':
        return -2
    return 0
