# 기본 주택·파란 주택·상점 공통 이미지 통일

## 적용 범위

- 기본 주택 6개 중 기존 입구 주택 2개를 유지하고 나머지 4개는 building_sample_pixel_v1.png를 공유한다: (150,750), (150,450), (3150,150), (1650,1950).
- 파란 주택 7개 중 기존 입구 주택 (750,1650)을 유지하고 나머지 6개는 building_blue_house_pixel_v1.png를 공유한다: (150,150), (2250,1650), (2550,150), (3450,1050), (750,2550), (2550,2550).
- 상점 7개 중 기존 입구 상점 (1450,1650), (2250,1050)을 유지하고 나머지 5개는 새 building_shop_pixel_v1.png를 공유한다: (1650,150), (2850,150), (3450,450), (1050,2550), (2850,2550).
- 이미 입구·진입부가 있는 배송 건물 5곳은 기존 전용 이미지 우선 적용을 유지한다. 상점 공통 자산에는 입구를 새로 추가하지 않는다. 다른 방향의 배송 구역과 기존 표시 조건에 관여하지 않는다.

## 호환성과 제작 기준

기본 주택은 기존 주황 기와·크림 테두리·용마루·환기구, 파란 주택은 기존 파란 기와·크림 테두리·천창이 유지되는 도트 자산을 재사용했다. 새로 생성하거나 덮어쓰지 않았다. 상점은 기존 청록 평지붕·크림 난간·좌측 환기구 2개·우측 실외기와 배관을 유지하며 같은 탑다운 도트풍으로 제작했다. 좌상단 광원과 청회색 외곽선을 기준으로 한다.

위치·표시 크기·충돌·배송 구역·고객·입력 조건은 유지한다. 맵 파일, 지면·소품·HUD·게임 규칙은 수정하지 않았다. 기존 원본 PNG와 입구 PNG는 보존한다.

## 초기화와 출력

알파 128 이상을 2px 간격으로 조사한 외곽은 다음과 같다. 모두 1254×1254 캔버스이며 새/재사용 도트 이미지의 좌상단 알파는 0이다. 원본과 넓은 투명 여백이 호환되지만 외곽 픽셀은 완전히 같지 않다. 실제 합성 화면은 미확인이다.

| 종류 | 원본 표본 외곽 | 도트 표본 외곽 |
|---|---|---|
| 기본 주택 | (156,316)~(1096,962) | (148,312)~(1104,968) |
| 파란 주택 | (66,302)~(1188,948) | (60,300)~(1194,958) |
| 상점 | (94,294)~(1160,958) | (90,290)~(1164,962) |

세 공통 자산 RGBA 환산 합계는 18,870,192바이트(약 18MiB)다. 건물 수만큼 복제하지 않는다. 기존 기본/파란 주택은 원본과 별도 도트 PNG를 함께 로드했지만 이제 공통 도트 PNG만 로드하고, 원본은 실패 시에만 사용한다. GPU 실측값은 아니다.

공통 자산은 기존 common_buildings 로드 경로에 등록한다. 같은 종류는 이미지와 실패 폴백 캐시를 공유하며 새 파일 실패 시 원본을 로드한다. 기존 좌표별 중복 로드 분기를 제거했다. 입구 자산은 공통 이미지 선택 후 기존 전용 분기로 덮어 선택하므로 기존 배송 건물의 입구를 유지한다.

최근접 필터와 전체 표시 캔버스 기준 화면 밖 출력 생략을 기존 공통 건물 경로에서 재사용한다. 매 프레임 생성·로딩은 없다. 건물당 이미지 출력은 기존 1회를 유지한다. 원본과 도트 자산을 같은 종류별로 중복 로드하던 부분을 줄인다.

실행 테스트와 커밋은 하지 않았다. 실제 배경 합성·도트 밀도·가림·로드 실패 경로 실행 결과는 미확인이다.

## 수동 확인

- 남아 있던 기본 주택·파란 주택·상점이 같은 종류끼리 도트풍으로 통일되는지.
- 기존 배송 건물 5곳의 문·문턱·진입부가 유지되는지.
- 공통 상점에 새 문이나 진입부가 추가되지 않았는지.
- 240/260/280px 주택의 외곽·투명 여백·도트 크기가 자연스러운지.
- 기존 고객·느낌표·충돌·배송 입력·재시작 동작이 유지되는지.
- 카메라 이동 시 건물이 갑자기 잘리거나 누락되지 않는지.

## 제작 도구와 프롬프트

내장 image_gen 편집, transparent_background=true. 원본 building_shop.png를 편집 대상으로 사용한다. 최종 자산 경로는 assets/images/building_shop_pixel_v1.png이다. 기존 주택 도트 PNG와 입구 PNG는 변경하지 않는다.

생성 파일 exec-92979603-c8af-4535-9c86-09fb70142867.png를 프로젝트의 새 상점 경로로 복사했다.

Use case style-transfer. Edit supplied top-down teal flat-roof shop sprite to crisp2D pixel art. Preserve exact1254x1254 transparent canvas and building footprint approxx90..1164,y294..960, centered627. Preserve cream rectangular parapet, teal flat roof, two dark square vents upper-left, beige AC and pipes upper-right, all positions and sizes. No new doors or facade: this is a COMMON ROOF variant, not the separate delivery entrance variant. Upper-left light, dark blue-charcoal stepped outlines,3-4flat shades per material, sparse quiet lowcontrast teal patches, hard square pixel clusters designed140x140 logical shown280x280. No smooth gradients, no isometric perspective, ground, props, text, signs, exterior glow or added outside shadows. Keep generous original transparent margins and existing roof geometry. Genuine transparent background. One sprite only.

