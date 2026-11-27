# 출발지·배송 건물 연결 점검과 도시 소품 통일

## 확인 범위

타이틀 title_city_v1.png, 배달소와 기본/파란 주택/상점 입구 PNG, 맵 좌표, RoadFinish, MapDecoration, ZoneMarkers를 확인했다. 소품은 맵에 배치된 7종 38개 전부를 대상으로 한다. 건물 확대 교체나 새 장식 추가는 하지 않는다. 게임 실행·자동 테스트·커밋은 하지 않았다.

## 건물과 고객 점검

| 대상 | 표시 크기 | 진입부 중심 x / 폭 | 문턱 폭 | 배송 구역과 진입부 겹침 | 기존 고객 발 좌표 |
|---|---|---|---|---|---|
| 기본 주택 (750,900) | 280×280 | 750 / 48 | 36 | 12px | (820,706) |
| 기본 주택 (1450,1050) | 280×280 | 1450 / 48 | 36 | 12px | (1520,856) |
| 파란 주택 (750,1650) | 300×300 | 750 / 52 | 40 | 13px | (820,1451) |
| 상점 (1450,1650) | 320×320 | 1450 / 56 | 44 | 13px | (1520,1451) |
| 상점 (2250,1050) | 280×280 | 2250 / 48 | 36 | 12px | (2320,856) |

- PNG의 문은 대략 캔버스 가로 중앙이다. 진입부와 문턱도 건물 중심 x에 정렬되어 있다. 문턱은 이미지에서 보이는 문보다 넓어 중앙을 받친다.
- 고객은 중심 진입부 오른쪽에 있어 코드상 발 좌표가 진입부와 겹치지 않는다. 실제 얼굴·느낌표와 오토바이의 겹침은 카메라 및 플레이 상태에 따라 수동 확인이 필요하다.
- 배달소 (750,150)는 북쪽 수령 구역 (690,310)~(810,390)과 기존 진입로 (690,260)~(810,390)를 사용한다. 원본 고객 표시 코드상 배달소에는 고객을 표시하지 않는다. 기존 입구 이미지와 조명 부착점은 유지한다.
- 같은 1254px PNG를 280px/320px로 표시하는 두 상점은 도트 크기에 약 14% 차이가 있다. 기존 크기와 공유 자산 유지 조건에 따라 이번에는 건물을 다시 그리거나 표시 크기를 바꾸지 않는다.
- 코드로 입구 중심이나 배송 구역의 단절이 확인되지 않아 건물·진입부 좌표는 수정하지 않았다. PNG 외곽 픽셀과 실제 문턱 겹침, 최종 도트 밀도는 실행 미확인이다.

## 확인된 불일치와 수정

| 종류 | 수량 | 변경 |
|---|---:|---|
| 나무 | 12 | 부드러운 큰 잎에서 타이틀을 참고한 밝은 녹색 잎 덩어리·깊은 청록 음영·계단 외곽선으로 교체 |
| 버스 정류장 | 4 | 청록 지붕·크림 기둥·벤치·버스 표식을 유지하며 픽셀 표현 정리. 원래 배치를 유지한 편집본 사용 |
| 분수 | 1 | 크림 돌 테두리·청록 수면·짧은 도트 물결로 정리 |
| 벤치 | 6 | 기존 bench_pixel_v1.png 공유 적용 |
| 분리수거함 | 7 | 기존 recycling_bin_pixel_v1.png 공유 적용 |
| 우편함 | 3 | 기존 mailbox_pixel_v1.png 공유 적용 |
| 화분 | 5 | 기존 planter_pixel_v1.png 공유 적용 |

기존에는 벤치·분리수거함·우편함·화분 각각 한 곳만 새 이미지였다. 좌표별 분기를 종류별 공유 로드로 바꾸어 같은 종류 안에서 구형/신형 이미지가 섞이지 않도록 했다. 원본 PNG와 맵 위치·표시 크기·투명 여백 기준·충돌 데이터는 보존한다. 생성 이미지의 정확한 실루엣 픽셀 일치는 보장하지 않으며 수동 확인 대상으로 둔다.

나무 두 곳의 기존 1px 좌우 흔들림·주기·위상은 유지한다. 새 수관을 사용할 때 원본 가지/잎 레이어를 중복 출력하지 않는다. 회전이나 새 애니메이션은 추가하지 않는다. 새 나무 로드 실패 시 기존 이미지와 기존 분리 레이어를 사용한다.

## 렌더링

- 초기화 시 종류별 한 번만 로드하며 실패 결과도 공유한다. 새 이미지 실패 시 원본으로 복귀한다.
- 새 소품 텍스처에는 최근접 필터를 명시한다.
- 정적인 소품도 전체 캔버스가 화면 밖이면 출력을 생략한다. 흔들리는 두 나무는 TreeSway의 기존 여유 범위 포함 검사를 사용한다.
- 매 프레임 파일 로딩·이미지 생성은 없다. 동일 소품 수를 유지하며 새 수관 성공 시 흔들리는 두 나무의 레이어 출력이 각각 2회에서 1회로 줄어든다.
- 1254×1254 PNG 6종의 RGBA 합계는 37,740,384바이트다. 정류장 텍스처를 더한 메모리와 최종 메타데이터는 아래에 기록한다. 텍스처마다 표시 개수만큼 복제하지 않는다. 이 수치는 환산값이며 GPU 실측값이 아니다.
- 정류장 1536×1024는 6,291,456바이트이므로 소품 7종 합계는 44,031,840바이트(약 41.99MiB)다. 기존에는 원본 7종과 도트 소품 4종, 나무 분리 레이어 2종을 함께 로드했지만, 새 자산 로드 성공 시 7종만 공유한다.
- 도로 판정, 충돌, 수령/배송 입력, 고객 배치, HUD와 건물 원본은 수정하지 않는다.

## 수동 확인

- 출발지와 배송 건물 5곳에서 문·문턱·진입부가 자연스럽게 연결되는지.
- 고객·느낌표·오토바이가 나무나 소품에 가려지지 않는지.
- 맵의 나무·정류장·분수와 기존 도트 소품의 색과 윤곽이 어울리는지.
- 정류장 외곽에 빛 번짐/사각형/투명 테두리가 남지 않는지.
- 나무 두 곳에서 구형 잎이 겹치거나 회전하지 않는지.
- 기존 충돌과 배송 입력 조건, 수령 전 고객 숨김이 유지되는지.
- 카메라 경계에서 소품이 갑자기 잘리지 않는지, 재시작 후 표시가 유지되는지.

## 제작 도구와 프롬프트

내장 image_gen을 사용하고 transparent_background=true로 요청했다. 새 자산은 assets/images/tree_title_pixel_v1.png, bus_stop_pixel_v1.png, fountain_pixel_v1.png에 별도 저장한다. 원본은 유지한다. 프롬프트는 제작 목표이며 실제 투명도/크기와 화면 정합 확인을 대신하지 않는다.

최종 사용 생성 파일: 나무 exec-5ad9729d-57f9-477e-aed0-1b6ab45468ae.png, 정류장 exec-ca0f8881-c8d8-4379-84e9-65b1fed5d73c.png, 분수 exec-dd695ca0-c08b-43f2-9e40-56b350e19dc7.png. 정류장의 새 구도 재제작 시안은 원본 배치와 차이가 있어 사용하지 않았다.

알파 128 이상 영역을 2px 간격으로 조사한 외곽은 나무 (96,104)~(1156,1152), 정류장 (98,336)~(1438,704), 분수 (100,108)~(1146,1160)이다. 각 캔버스 크기·중심·넓은 여백을 유지하는 기준이며 원본의 정확한 외곽 픽셀 일치는 아니다. 알파 1 수준의 미세 외곽은 더 넓게 남아 있다. 정류장 바깥쪽 (50,500), (700,200), (700,300), (700,800)의 표본은 알파 0이다. 도구 미리보기의 RGB 번짐을 실제 게임에서 불투명하게 출력되는 조명으로 단정하지 않는다. 실제 배경 합성은 미확인이다.

### 나무

Use case style-transfer. Image1 EDIT TARGET top-down tree sprite. Image2 STYLE reference city title foliage only. Keep square1254x1254 transparent canvas and tree crown silhouette approximatelyx90..1160,y95..1165, center627. Replace smooth lobed leaves and gradients with compact pixel-art clustered foliage matching title's crisp trees: several small irregular leaf clumps, yellow-green sunlit clusters upper-left, mid grassy green, deep teal-green lower-right shadows, 4flat tones, charcoal-green 1logicalpixel outline, hard square stepped edges. True overhead/top-down circular crown, no tall side-view trunk, no ground, no props, no glow, no outside shadow. No floral petal leaf shapes, no soft gradients or airbrush. Design native55x55 logical pixels for110x110 screen with readable larger clusters and 2px screen units. Dense solid crown with no transparent holes, authentic transparent exterior. Preserve original centered footprint and generous margins. One tree asset only.

### 정류장 최초 편집

Use case style-transfer. Image1 edit target bus shelter sprite; image2 visual style reference city title only. Keep1536x1024 landscape canvas and exact shelter geometry footprint approximately x105..1435,y340..695 including round bus symbol onright. Redraw as crisp cohesive pixel-art top-down slightly overhead urban prop: rectangular teal paneled canopy with cream metal edge, pale teal glass panels beneath, short brown slatted bench, right circular bus pictogram. Preserve overhead view, same canopy proportions, support and bench positions, thin visible sidewall only. Hard stepped edges and 3-4flat shades per material, upper-left illumination, dark blue-green outlines, designed115x77logicalpixels displayed230x154. REMOVE entire soft beige light halo outside shelter; genuinely transparent exterior including margins. Do not add ground, people, text, props, shadow outside original footprint. No airbrush or smooth gradients, no photorealism or tall front-facing shelter. Single isolated game sprite.

### 정류장 외곽 제거 시도

Use case background-extraction. Exact edit target supplied pixel-art bus shelter. REMOVE THE ENTIRE OUTSIDE HALO / GREY GLOW and ALL exterior translucent pixels. Exterior around structure must be zero-alpha transparent right up to hard dark shelter outline. Keep1536x1024 canvas and exact shelter position and size unchanged, x100..1435,y335..705. Keep canopy glass bench posts rightbus pictogram untouched. Do not replace halo with black, checkerboard, floor or any color. Genuine transparent cutout with crisp hard pixel outline, no glow, no ambient haze, no cast shadow outside outline. All pixels outside actual shelter hardware and sign must alpha0. Preserve existing sprite design.

### 정류장 재제작 시안 — 미사용

Create one transparent-background pixel-art game asset: an overhead urban BUS SHELTER,1536x1024 transparent canvas, sprite positioned x100..1435,y335..705. Wide horizontal teal rectangular roof in6panels spanningx105..1285,y340..560, narrow cream metal rim and dark navy-green outline. Below roof short pale teal glass back panel, narrow brown slatted bench centeredx690,y610, slim cream posts atx145and1245endingy695. Onright, attached small cream-rimmed teal circular bus pictogram centeredx1370,y530 radius60. Top-down slightly overhead view compatible with title-reference city but no street ground. Cozy crisp 2D pixel art,115x77logicalpixel grid displayed230x154, limited flat teal cream brown palette and upper-left light, hard stepped edges, short sidewalls. ABSOLUTELY NO LIGHT HALO, NO GLOW, NO AMBIENT GRAY HAZE, NO CAST SHADOW OUTSIDE OBJECT, NO COLORED BACKDROP. Everywhere outside precise shelter hardware is pure zero-alpha transparency. No text, extra props or characters. Single sprite, preserve substantial transparent margin around asset.

### 분수

Use case style-transfer. Edit target supplied overhead circular fountain sprite. Preserve1254x1254 transparent canvas, centered circular silhouettex100..1140,y110..1155, cream stone circular rim, four cardinal square ornamental blocks with terracotta diamond and small central cream nozzle. Convert to crisp 2D pixel-art consistent with cozy delivery game's teal cream palette: hard stepped circular edges, dark blue-charcoal thin outlines, 3flat stone shades upper-left light, restrained teal water and short angular stepped ripple marks. True vertical top-down circular pool, not isometric, no tall jet. Design115x115logicalpixels shown230x230,2px screen units. No soft gradients, airbrush, halo, outer ground or new props, no text. All outside original silhouette genuinely transparent. Keep original proportions and locations, one sprite only.

