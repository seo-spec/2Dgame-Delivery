# 배송 위치 마커 이미지

내장 `image_gen` 도구로 생성한 투명 PNG 4종이다. 원본 생성 파일의 알파 채널을 보존하여 프로젝트에 복사했다. 기존 배달소·배송지와 어울리는 페인트/금속 질감이며 글자는 없다.

| 파일 | 용도 | 색상 |
| --- | --- | --- |
| `pickup_zone_v1.png` | 적재 지점 | 노란 상자 |
| `delivery_zone_v1.png` | 미배송 지점 | 파란 화살표와 받침 |
| `return_zone_v1.png` | 배달소 복귀 | 민트색 배달소와 복귀 화살표 |
| `complete_zone_v1.png` | 배송 완료 | 차분한 초록 체크 |

네 파일은 모두 1774×887이다. 모서리와 중앙 빈 공간의 알파 0을 확인했다. `game/config/delivery_markers.py`의 UV 영역으로 바깥 투명 여백을 제외해 실제 구역 크기에 맞춰 그린다. PNG 파일 자체는 자르거나 재도색하지 않았다.

`ZoneMarkers`는 시작 시 이미지 4장을 한 번 로드해 공유한다. BACKGROUND의 건물 다음에 배치하여 ACTORS의 오토바이가 위에 그려진다. 대상 진입은 불투명도를 높이고 배송 완료는 낮춰 구분한다. 실제 판정 영역·입력·보상은 변경하지 않는다.

## 최종 생성 프롬프트

각 이미지마다 아래 공통 프롬프트 뒤에 해당 변형 문장을 붙여 독립적으로 생성했다. 모든 호출은 `transparent_background=true`를 사용했다.

공통:

> Use case: stylized-concept. Asset type: production-ready transparent PNG ground interaction marker for a top-down 2D Korean neighborhood motorbike delivery game. Single isolated marker centered on transparent canvas, orthographic directly overhead, aspect ratio about 2:1. Cohesive hand-painted game sprite style, softly shaded bevelled painted metal/road-paint details, restrained worn edges, crisp silhouettes readable at 120x80 pixels. A low flat rectangular landing pad frame made of four thick separated corner brackets with a generous transparent open middle, plus one compact raised-looking symbolic medallion in the center. The whole marker is a subtle game-world floor decal, NOT a floating app button or map pin. No tall objects, no scenery, no asphalt background, no text, no letters, no numbers, no watermark, no drop shadow outside the shape. Keep alpha transparency both around the marker and throughout most of its open center. Composition: outer bracket envelope from 6% to 94% of canvas width and 10% to 90% of height; avoid large empty margins. All symbols and details completely inside the outer frame. High-quality finished game UI asset, not thin wireframe lines, not neon hologram, not photorealistic.

적재:

> Variant: pickup. Main palette: warm amber yellow, with cream highlights and dark desaturated outlines. Center symbol: a dimensional cardboard parcel with a short loading arrow, ready to collect.

배송:

> Variant: delivery. Main palette: cool sky blue, with cream highlights and dark desaturated outlines. Center symbol: a clean parcel drop-off symbol, a downward arrow entering a shallow receiving tray.

복귀:

> Variant: return. Main palette: soft mint green, with cream highlights and dark desaturated outlines. Center symbol: a small depot house silhouette with a returning curved arrow.

완료:

> Variant: complete. Main palette: muted sage green, with cream highlights and dark desaturated outlines. Center symbol: a bold elegant completion checkmark.

## 수동 확인

- 시작 시 배달소에 노란 적재 마커가 보이는지 확인한다.
- 미배송 지점은 파란 이미지, 배송 후에는 초록 체크로 바뀌는지 확인한다.
- 복귀 단계에서 배달소에 민트색 복귀 이미지가 표시되는지 확인한다.
- 바닥과 중앙 빈 공간에 검은 사각 배경이 생기지 않는지 확인한다.
- 마커 안에 진입해도 오토바이가 이미지에 가려지지 않는지 확인한다.
- 기존 구역 안 Space 수령·배송과 자동 복귀 판정이 유지되는지 확인한다.

이미지 자체의 시각·알파 검사는 수행했다. 게임 실행·플레이 검증은 수행하지 않았다.
