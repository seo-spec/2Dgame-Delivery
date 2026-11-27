# 북쪽 주택 입구와 배송 대기 공간 연결

## 기존 좌표와 표시

- 주택 `collision_preview_house`: (750,900), 표시280×280.
- 충돌: x645~855, y824~970. 기존 offset(0,-3), size210×146 유지.
- 배송 구역: x660~840, y690~780. 기존 offset(0,-165), size180×90 유지.
- 고객 발 좌표: (820,706). 기존 `ZoneMarkers` 계산과 위치를 변경하지 않았다.
- 기존 이미지 전체를 같은 캔버스 크기로 표시하면 남쪽 지붕 끝은 대략 y824에 해당한다.

## 변경 내용

- `assets/images/building_sample_entrance_pixel_v1.png`를 별도 제작해 해당 주택1개에만 적용한다. 공유 원본 `building_sample_pixel_v1.png`와 `building_sample.png`는 보존하며 다른 주택은 그대로다.
- 남쪽 외곽 안쪽에 좁은 벽면과 가운데 나무 문을 표현했다. 기존 지붕·용마루·환기구 구도는 유지하도록 제작했다. 이미지1254×1254, 모서리 알파0 확인. 외곽 픽셀 일치와 정확한 문턱 정합은 실행 미확인이다.
- 표시용 진입부 x726~774, y768~826(폭48px), 문턱 x732~768, y814~826. 위쪽은 건물 이미지 아래로 겹치고 아래쪽12px은 기존 배송 구역 안으로 이어진다.
- 진입부는 기존 정적 지면 텍스처의 RGB에 초기화 시 합성한다. 별도 지면 텍스처나 매 프레임 출력은 추가하지 않으며 기존 화면 밖 출력 생략을 사용한다.
- 해당 주택 이미지도 전체 표시 캔버스가 화면 밖이면 출력을 생략한다. 전용 이미지는 초기화 시1회 캐시 로드, 실패하면 기존 공유 주택 이미지로 돌아간다.
- 진입부 설정은 `road_finish.entry_paths`에만 들어간다. 실제 도로를 구성하는 `access_paths`나 `RoadSurface`에는 추가하지 않았다. 새 충돌 영역도 없다.
- 건물/고객 위치·충돌·배송 구역·입력 조건·다른 건물/소품/HUD·규칙은 변경하지 않았다.
- 새 입구 이미지는 기존 공유 이미지와 별도 텍스처1개를 사용한다. 지면 포장은 기존 지면 텍스처에 합성되므로 지면 출력은 여전히 보일 때1회다.

## 제작 도구와 프롬프트

내장 image_gen 편집, transparent_background=true. 기존 도트 기본 주택을 편집 대상으로 사용했다.

Use case precise-object-edit. Edit target supplied pixel-art orange roof sprite. Create house SOUTH ENTRANCE variant for exactly same top-down game building. Keep square1254x1254 canvas and transparent margins; keep footprint approx x150..1105,y310..970, same orange roof tile pattern, ridge, vent, cream frame and hard stepped pixel style, upper-left light. Change ONLY bottom/southmost roof edge: replace its last narrow roof band inside original footprint (approximately y880..960) with a short cream wall/eave strip and centered wooden entry door (approx x575..680 y890..960) with dark inset and cream door frame, readable from top-down. Bottom boundary remains at y970, do NOT extend facade or artwork downward/outside existing footprint. The door must face screen-bottom south and visibly connect to a small stone doorstep that will be drawn separately below building by game. Preserve all other tiles/ridge/vent positions and colors; only local entrance at bottom changes. No porch floor/ground/path in this PNG, no props, characters, signage, outside shadows or text. Genuine transparent background. Do not redraw as frontal/isometric house. Native140x140 logical pixel density when shown280x280, hard 2px screen pixel edges, limited3tone palette. Original roof source must remain available; save separate variant.

## 수동 확인

- (750,900)의 주택만 남쪽 문이 보이고 다른 주택은 기존 지붕인지.
- 문·문턱·포장 진입부가 끊기지 않고 기존 배송 구역까지 이어지는지.
- 고객이 이전 위치에 있고 얼굴/느낌표를 진입부가 가리지 않는지.
- 기존 건물 충돌과 배송 구역 안 Space 조건이 유지되는지.
- 진입부가 새 도로로 판정되지 않는지.
- 카메라 이동/재시작 후 입구·진입부가 정상인지.

게임 실행·자동 테스트·커밋은 하지 않았다. 실제 합성 화면·입구와 충돌 실루엣의 대응은 미확인이다.
