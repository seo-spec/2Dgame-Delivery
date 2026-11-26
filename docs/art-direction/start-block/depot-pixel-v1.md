# 배달소 도트풍 자산 1차 적용

- 자산: `assets/images/building_delivery_depot_pixel_v1.png`
- 원본 보존: `assets/images/building_delivery_depot.png`
- 제작: 내장 image_gen 편집 도구, transparent_background=true.
- 원본/신규 파일 크기: 모두1254×1254. 모서리와 위쪽 중앙 픽셀의 알파0 확인. 투명 여백의 모든 픽셀이 원본과 동일하다는 뜻은 아니다.
- 게임 표시: 기존320×320, 기존 중심/충돌/수령 구역 유지.
- 새 자산 우선 로드, OSError 발생 시 원본 로드. 선택된 자산에 맞춰 출입구 조명과 환기구 수증기 부착 비율 적용.
- 도트 밀도는 화면2px 기준을 목표로 생성했다. 생성 자산의 모든 픽셀이 정확한2px 격자라는 검증은 하지 않았으며 실제 표시 가독성은 수동 확인 대상이다.
- 게임 실행·테스트·커밋은 수행하지 않았다.

## 제작 프롬프트

Use case style-transfer / precise-object-edit. Edit target supplied overhead delivery depot transparent sprite. Keep exact square1280x1280 canvas, outer footprint bounds approximately x64..1195 y64..1130 and original transparent padding. Keep top-down orthographic orientation and same geometry, cream roof rim, orange roof, centered cream parcel box symbol, small entrance structure on north/top center and vent at upper-right roof. Redraw as CRISP LOW RES PIXEL ART: imagine native160x160 sprite scaled8x nearest to1280x1280, all strokes and blocks about8px multiples on output (equals2px when displayed320x320 in game). Hard stepped pixel edges, flat limited palette 3tones/material, no antialias smooth gradients, no glossy painted render. Orange muted terracotta roof #C77543 darker #9F5635, cream rim #C8BDA4 and #E0CFAB, outlines #28383B. Single upper-left light, small dark bottom/right edges only within building footprint, no cast ground shadow. Add sparse straight pixel roof seams, preserve simple large central parcel logo so it reads at320px. Entrance light/window centered at image(640,205), vent center at image(1000,405), keep these attachment points and structures clearly readable. Keep original proportions so unchanged game collision remains plausible. No ground, no yard, no vegetation, no props around building, no text, no perspective facade. Actual transparent background, preserve transparent margins. This is production game sprite, not mockup.

요청한 크기와 달리 생성 결과는1254×1254이며 런타임 부착점은 실제 생성 이미지 기준으로 맞췄다.

## 잔디 경계 조정

개선 구역 잔디(130,150,91)와 바깥 기본 잔디(75,112,82)의 큰 색상 차이가 코드에서 확인되었다. 개선 구역 기본색만(81,117,83)으로 조정하고 기존 경계 페이드와 풀 무늬는 유지했다. 바깥 잔디·맵 형상·판정은 변경하지 않았다. 사용자가 지적한 왼쪽 어두운 부분이 이 조정으로 해소되는지는 실제 실행 화면에서 확인해야 한다.
