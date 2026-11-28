"""출발지 한 블록의 낮은 지면 구성. 새 월드 객체나 판정을 만들지 않는다."""


def _inside_rounded(x, y, bounds, radius):
    x, y = x // 2 * 2, y // 2 * 2
    left, bottom, right, top = bounds
    if not (left <= x < right and bottom <= y < top):
        return False
    cx = max(left + radius, min(right - radius - 1, x))
    cy = max(bottom + radius, min(top - radius - 1, y))
    return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2


def _color(wx, wy, material):
    # 바닥 재질은 기존 화면2px 격자와 맞추고 차량보다 낮은 대비로 유지한다.
    x, y = wx // 2 * 2, wy // 2 * 2
    if material == 'garden':
        patch = ((x // 10 * 37) ^ (y // 8 * 13)) & 3
        base = (112, 134, 78)
        shade = (0, 2, -3, 1)[patch]
        if x % 10 in (2, 4) and y % 8 == 2:
            shade += 4
    else:
        width, height = (28, 14) if material == 'brick' else (24, 24)
        row, local_y = divmod(y, height)
        column, local_x = divmod(x + (row % 2) * (width // 2), width)
        shade = ((column * 17 ^ row * 29) & 3) - 1
        base = {'stone': (190, 182, 157), 'brick': (166, 146, 117),
                'service': (170, 168, 150)}[material]
        if local_x < 2 or local_y < 2:
            shade -= 5 if material != 'service' else 2
        elif local_y == height - 2:
            shade += 2
    return tuple(channel + shade for channel in base)


def _ellipse_coverage(x, y, bounds):
    left, bottom, right, top = bounds
    rx, ry = (right - left) / 2, (top - bottom) / 2
    if rx <= 0 or ry <= 0:
        return 0.0
    x, y = x // 2 * 2 + 1, y // 2 * 2 + 1
    distance = (((x - left - rx) / rx) ** 2 + ((y - bottom - ry) / ry) ** 2) ** 0.5
    ratio = min(1.0, max(0.0, (1 - distance) * min(rx, ry) / 6))
    return ratio * ratio * (3 - 2 * ratio)


def paint_neighborhood(finish, pixels, road_mask, quiet, sidewalk, layout, pump):
    if not layout:
        return
    region = layout['bounds']
    if (finish.left >= region[2] or finish.left + finish.width <= region[0]
            or finish.bottom >= region[3] or finish.bottom + finish.height <= region[1]):
        return
    surfaces = layout['surfaces']
    # 사각형별로 외곽선을 덧그리지 않고 최종 재질 영역을 먼저 합친다.
    owners = bytearray(finish.width * finish.height)
    underlays = bytearray(len(owners))
    active = []
    for number, surface in enumerate(surfaces, 1):
        bounds = surface['bounds']
        left = max(finish.left, bounds[0], region[0])
        bottom = max(finish.bottom, bounds[1], region[1])
        right = min(finish.left + finish.width, bounds[2], region[2])
        top = min(finish.bottom + finish.height, bounds[3], region[3])
        if left >= right or bottom >= top:
            continue
        active.append((left, bottom, right, top))
        radius = surface.get('radius', 0)
        for wy in range(bottom, top):
            if wy % 16 == 0:
                pump()
            row = finish.height - 1 - (wy - finish.bottom)
            for wx in range(left, right):
                index = row * finish.width + wx - finish.left
                inside = (_ellipse_coverage(wx, wy, bounds) > 0
                          if surface.get('shape') == 'ellipse'
                          else _inside_rounded(wx, wy, bounds, radius))
                if (road_mask[index] or sidewalk[index]
                        or quiet[index] and not layout.get('quiet_floor') or not inside):
                    continue
                underlays[index] = owners[index]
                owners[index] = number
    if active:
        for wy in range(min(b[1] for b in active), max(b[3] for b in active)):
            if wy % 16 == 0:
                pump()
            row = finish.height - 1 - (wy - finish.bottom)
            for wx in range(min(b[0] for b in active), max(b[2] for b in active)):
                x = wx - finish.left
                index = row * finish.width + x
                number = owners[index]
                if not number:
                    continue
                surface = surfaces[number - 1]
                material = surface['material']
                color = _color(wx, wy, material)
                if quiet[index] and layout.get('quiet_floor'):
                    # 배송 공간은 포장 바탕만 이어 주고 줄눈/장식을 넣지 않는다.
                    color = (190, 182, 157)
                offset = index * 4
                if surface.get('shape') == 'ellipse':
                    coverage = _ellipse_coverage(wx, wy, surface['bounds'])
                    beneath = underlays[index]
                    base = (_color(wx, wy, surfaces[beneath - 1]['material']) if beneath
                            else pixels[offset:offset + 3])
                    color = tuple(round(base[c] * (1 - coverage) + channel * coverage)
                                  for c, channel in enumerate(color))
                else:
                    # 연결된 재질/기존 보도 쪽에는 잔디색 테두리를 만들지 않는다.
                    neighbors = ((x >= 2, index - 2), (x < finish.width - 2, index + 2),
                                 (row >= 2, index - finish.width * 2),
                                 (row < finish.height - 2, index + finish.width * 2))
                    if any(valid and not owners[other] and not sidewalk[other]
                           and not road_mask[other] and not quiet[other]
                           for valid, other in neighbors):
                        color = tuple((channel + pixels[offset + c]) // 2
                                      for c, channel in enumerate(color))
                pixels[offset:offset + 3] = bytes(color)
    # 배달소 옆 두 소형 주차칸. 빈 바닥선만 넣고 차량·차단물은 추가하지 않는다.
    for left, bottom, right, top in layout.get('parking_bays', []):
        for wy in range(max(bottom, finish.bottom), min(top, finish.bottom + finish.height)):
            row = finish.height - 1 - (wy - finish.bottom)
            for wx in range(max(left, finish.left), min(right, finish.left + finish.width)):
                if not (wx < left + 2 or wx >= right - 2 or wy < bottom + 2):
                    continue
                if not (region[0] <= wx < region[2] and region[1] <= wy < region[3]):
                    continue
                index = row * finish.width + wx - finish.left
                if not (road_mask[index] or sidewalk[index] or quiet[index]):
                    pixels[index * 4:index * 4 + 3] = bytes((209, 195, 160))
