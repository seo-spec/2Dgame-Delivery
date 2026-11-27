# 배송 건물 세 곳의 도트 이미지와 입구 연결

## 범위와 좌표

기존 미술 기준의 탑다운 지붕 중심 구도, 화면 약 2px 도트 밀도, 좌상단 광원, 청회색 외곽선과 절제된 명암을 기준으로 제작했다. 이미지 파일을 직접 확인했으며 게임 실행 화면은 확인하지 않았다.

| 대상 ID / 중심 | 원본 / 표시 크기 | 충돌 영역 | 배송 영역 | 기존 고객 발 위치 |
|---|---|---|---|---|
| delivery_house_c / (750,1650) | building_blue_house.png / 300×300 | (616,1573)~(884,1727) | (660,1435)~(840,1525) | (820,1451) |
| delivery_house_d / (1450,1650) | building_shop.png / 320×320 | (1314,1566)~(1586,1734) | (1360,1435)~(1540,1525) | (1520,1451) |
| delivery_house_e / (2250,1050) | building_shop.png / 280×280 | (2131,976)~(2369,1124) | (2160,840)~(2340,930) | (2320,856) |

지정한 건물 3개에만 적용한다.

세 건물 모두 남쪽 배송 구역을 향하도록 입구를 이미지 아래쪽 가운데에 배치한다. 건물·고객 좌표와 표시 크기, 모든 판정 데이터는 변경하지 않았다.

| 대상 | 표시용 진입부 (left,bottom,right,top) | 문턱 |
|---|---|---|
| 파란 주택 C | (724,1512,776,1576) | (730,1564,770,1576) |
| 상점 D | (1422,1512,1478,1568) | (1428,1556,1472,1568) |
| 상점 E | (2226,918,2274,978) | (2232,966,2268,978) |

진입부 아래쪽은 배송 구역에 12~13px 겹치고, 위쪽은 건물 아래에 겹쳐 그린다. 고객은 입구 중심 오른쪽의 기존 위치에 유지된다. 생성 이미지의 미세한 외곽·여백 차이와 문턱 정합은 실제 화면에서 수동 확인해야 한다.

## 자산과 연결

- `assets/images/building_blue_house_entrance_pixel_v1.png`: 파란 기와·크림 테두리·천창·용마루를 유지한 남쪽 입구 변형. 대상 C만 적용하며 기존 파란 주택 자산은 유지한다.
- `assets/images/building_shop_entrance_pixel_v1.png`: 청록 평지붕·크림 테두리·왼쪽 환기구 2개·오른쪽 실외기를 유지하고 남쪽 유리문을 추가한다. D/E는 같은 텍스처와 로드 실패 캐시를 공유하며 기존 표시 크기로 출력한다.
- 로드 실패 시 각 원본을 사용한다. 새 자산은 별도 파일이며 원본을 덮어쓰지 않았다.
- 기존 `RoadFinish`의 진입부 전용 초기화 합성·도로 픽셀 제외·화면 밖 출력 생략을 재사용한다. 기존 지면 재질 구역을 넓히지 않는다.
- 세 진입부의 RGBA 예상 합계: (52×64 + 56×56 + 48×60)×4 = 37,376바이트(36.5KiB). 보일 때 최대 3회 추가 출력. 실측값이 아니다.
- 두 상점의 표시 크기 차이로 도트 크기에는 약 14% 차이가 있다. 같은 자산 공유와 기존 크기 유지를 우선했고, 최종 화면에서 밀도를 확인한다.
- 두 PNG 모두 1254×1254, 좌상단 모서리 알파 0이다. 알파 128 이상을 2px 간격으로 조사한 외곽은 파란 주택 원본 (66,302)~(1188,948), 새 이미지 (58,298)~(1196,978), 상점 원본 (94,294)~(1160,958), 새 이미지 (88,292)~(1164,962)다. 캔버스와 넓은 투명 여백은 유지하지만 외곽 픽셀은 완전히 같지 않다. 주택 남쪽은 문 표현으로 화면 약 7px 길어지며 진입부 위쪽과 겹친다. 충돌 영역은 그대로다.
- 새 이미지 2개의 RGBA 환산 메모리는 12,580,128바이트(약 12MiB), 진입부 포함 약 12.03MiB다. 두 상점 때문에 텍스처를 중복 로드하지 않으며 건물 출력 횟수는 기존과 같다.
- 실제 도로 구성인 `access_paths`와 `RoadSurface`, 충돌, 수령·배송·입력 조건, 다른 소품/건물/HUD는 수정하지 않았다.

## 제작 도구와 최종 프롬프트

내장 image_gen 편집, transparent_background=true. 주택은 기존 도트 파란 주택을 편집하고 원본을 구도 참조로 사용했다. 상점은 원본 편집으로 제작했다. 최초 생성 중 달라진 여백/캔버스는 추가 편집으로 교정했으며 버린 시안은 게임에서 참조하지 않는다.

최종 생성 원본 파일: 주택 `exec-b722500f-b862-4a35-8d2e-54020fec583a.png`, 상점 `exec-759bbadc-d531-477a-867e-a5184c4ae338.png`. 두 파일을 프로젝트의 위 자산 경로로 복사했다. 아래 프롬프트는 제작 요청이며 정확한 외곽 준수 여부는 위 메타데이터를 기준으로 한다.

### 파란 주택 최종 보정

Use case precise-object-edit. Image1 EDIT TARGET is pixel roof with south door; Image2 geometry reference ONLY. Correct ONLY bottom band of image1: current south edge extends too far down. Keep1254x1254 canvas, upper roof and sides fixed. Move bottom wall/door boundary UP so final lowest opaque pixel y959 (same as original roof reference approx y950..960). All y>=970 must be fully transparent. Rebuild narrow wall and south door in y875..959 INSIDE roof original footprint, do not simply append wall below original roof. Preserve x60..1195 width, y300 top, blue tiles ridge skylight and upper-left light. Door bottom y959, centeredx627, pixels hard edged. No ground or other additions. Genuine transparency. Exact footprint preservation is the main goal.

### 상점 최종 편집

Edit this exact1254x1254 SQUARE image in place. Output1254x1254 square transparent canvas; preserve all original transparent margins. Building occupies x88..1165,y292..960 and MUST stay there, no recentering, no tighter crop, no landscape aspect ratio. Top-down teal flat roof with cream parapet two dark vents upper-left, AC upper-right unchanged composition. Convert smooth original into hard stepped 2D pixel art with limited3tones per material and dark blue-charcoal outlines, approximate140x140 logical grid, upper-left lighting. Add narrow SOUTH glazed double entry door centeredx627 in existing bottom cream rim, doorboundsx565..689,y885..959, INSIDE building originalfootprint. Lowest opaque pixel y960; transparent y>=970. Preserve roof shape, AC, vents and positions. No ground, path, props, text, outside shadow, people, isometric walls. Crucial retain square canvas AND original transparent margins; shop must not expand to fill canvas.

## 수동 확인

- 세 건물의 입구·문턱·진입부가 연결되고 투명 사각형·과한 외곽 변화가 없는지.
- 두 크기의 상점에서 문과 진입부의 폭·중앙이 자연스러운지.
- 고객·느낌표·오토바이가 가려지지 않는지.
- 기존 충돌과 배송 입력 조건이 유지되고 진입부가 새 도로로 판정되지 않는지.
- 다른 좌표의 파란 주택/상점과 이미 개선한 건물은 유지되는지.
- 카메라 이동·재시작 후 정상인지.

실행 테스트와 커밋은 하지 않았다. 실제 합성 화면, 성능 수치와 텍스처 로드 실패 경로의 실행 결과는 미확인이다.
