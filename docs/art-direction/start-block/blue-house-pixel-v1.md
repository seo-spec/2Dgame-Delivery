# 출발지 왼쪽 파란 지붕 주택1개 도트풍 적용

- 대상: `blue_house`, 월드(150,150)의1채만 적용한다. 기존 도트풍 배달소·북쪽 주택·카페와 다른 파란 주택은 변경하지 않는다.
- 기존 표시280×280, 충돌offset(0,0)/size250×144와 위치를 유지한다. 해당 건물에는 원래 배송 구역이 없으며 새로 추가하지 않는다.
- 원본 `assets/images/building_blue_house.png` 보존, 신규 `assets/images/building_blue_house_pixel_v1.png` 사용.
- 파란 기와·중앙/대각 용마루·크림 테두리·우측 천창·탑다운 시점을 유지하며 도트풍으로 제작했다. 원본과 생성 이미지는 모두1254×1254이며 모서리 알파0 확인.
- 투명 여백을 포함한 동일 캔버스와 기존 표시 크기를 사용한다. 생성 외곽의 픽셀 단위 일치·정확한 도트 격자·충돌 실루엣 대응은 미검증이므로 실제 화면에서 확인해야 한다.
- 대상 전용 캐시에 초기화 시1회 로드하고 실패하면 이미 로드된 원본으로 대체한다. 매 프레임 이미지 생성/파일 로딩은 없다.
- 게임 실행·테스트·커밋은 하지 않았다. 다른 건물·소품·HUD·게임 규칙은 변경하지 않았다.

## 제작 도구와 프롬프트

내장 image_gen, transparent_background=true. 원본 파란 주택을 편집 대상으로, 새 기본 주택·카페·배달소를 화풍 참조로 사용했다.

Use case precise-object-edit/style-transfer. Image1 BLUE HOUSE ROOF is EDIT TARGET. Image2 orange roof, Image3 cafe, Image4 depot are STYLE REFERENCES only. Redraw only original blue house roof as matching crisp 2D overhead pixel art. Preserve exact square1254x1254 transparent canvas, original horizontal roof footprint approx x64..1190 y300..950 and original large transparent top/bottom margins. Keep slate blue ceramic tiles, cream stone rim, horizontal dark blue central ridge, diagonal hip ridges meeting central ridge on both ends, small rectangular upper-right skylight. No parcel/coffee logo or facade. Same top-down orthographic angle and proportions, no enlargement, no rotation. Target game280x280 fullcanvas with native140x140 logical pixel density, approx9px output blocks per2px display pixel. Dark slate outline, cream rim same reference palette, muted blue roof3shades, upper-left lighting, clear stepped edges, simplified chunky tile seams, no painterly blending/soft gradients/gloss. No ground, cast shadows outside footprint, props, text, labels. Genuine transparent background. Keep identity and framing of Image1; do not recolor to orange.

## 수동 확인

- (150,150)의 주택1개만 도트풍으로 보이는지.
- 기와·천창·테두리가 같은 도트 밀도로 읽히고 투명 경계가 자연스러운지.
- 기존 위치·표시 크기·건물 충돌이 유지되는지.
- 다른 파란 주택과 기존 배달소·북쪽 주택·카페가 이전대로인지.
- 재시작 후 같은 위치에 정상 표시되는지.
