# 출발지 카페1개 도트풍 교체

## 대상 선정

- 종류: 카페, ID `delivery_candidate_cafe_450_150`.
- 월드(450,150), 배달소(750,150) 바로 왼쪽의 기존 미교체 건물이다.
- 원본 `assets/images/building_cafe.png` 보존, 신규 `assets/images/building_cafe_pixel_v1.png` 사용.
- 기존 표시280×280, 충돌 offset(0,-5)/size180×174, 배송 구역 offset(0,200)/size180×90을 모두 유지한다. 실제 배송 대상으로 추첨되는 조건도 유지한다.

## 적용 범위

- 해당 ID에만 전용 이미지 캐시를 사용한다. 다른 카페와 기존 도트풍 배달소·북쪽 주택은 변경하지 않는다.
- 초기화 시 새 이미지를1회 로드하고 OSError 발생 시 이미 준비된 원본을 사용한다. 매 프레임 파일 로딩은 없다.
- 자주색 지붕·커피잔/김 표식·크림색 테두리·우측 천창·하단 차양과 탑다운 방향을 유지하며 도트풍으로 제작했다.
- 원본과 새 이미지 모두1254×1254, 모서리 알파0을 확인했다. 투명 여백을 포함한 같은 캔버스로 같은 표시 크기에 출력한다. 생성 결과의 외곽이 원본과 픽셀 단위로 동일하다는 의미는 아니며 실제 실루엣/충돌 대응은 수동 확인 대상이다.
- 게임 실행·테스트·커밋은 수행하지 않았다. 소품·HUD·지면·게임 규칙은 변경하지 않았다.

## 제작 도구와 프롬프트

내장 image_gen 편집, transparent_background=true. 원본 카페가 편집 대상, 새 배달소·기본 주택이 스타일 참조다.

Use case precise-object-edit/style-transfer. Image1 cafe is EDIT TARGET. Image2 depot and Image3 orange house are STYLE REFERENCES only. Redraw ONLY cafe as matching crisp 2D top-down pixel art. Preserve square1254x1254 transparent canvas and subject bounds approximately x220..1030 y260..1040, same large transparent margins. Keep burgundy red/purple flat roof, cream stone frame, centered cream coffee cup and steam emblem, upper-right round skylight, burgundy/cream striped awning along SOUTH BOTTOM edge. Keep overhead orthographic orientation, original proportions, no new structures or facade perspective. This is game sprite displayed280x280 fullcanvas, aim native140x140 density, about9px output blocks for2px screen. Hard stepped outlines, dark slate outlines #28383B, flat limited3shades per material, upper-left lighting; preserve original burgundy identity while harmonizing cream rim with reference. Simplify curves into pixel steps, no soft painted gradients or glossy rendering. No ground, external shadow, text, props, labels. Genuine transparent background. Do not enlarge artwork to fill canvas, do not copy depot parcel logo or orange roof. Standalone cafe sprite only.

## 수동 확인

- 배달소 왼쪽(450,150) 카페1개만 도트풍으로 보이는지.
- 기존 지붕/커피 표식/차양이 읽히고 크기·투명 테두리가 자연스러운지.
- 같은 자산을 쓰는 다른 카페는 원본으로 유지되는지.
- 기존 충돌과 배송 대상으로 선택된 경우의 고객/배송 위치·Space 판정이 유지되는지.
- 재시작 후 동일한 위치에 정상 표시되는지.
