# 출발지 분리수거함 1개 도트풍 적용

- 대상: 월드(700,580)의 분리수거함1개. 기존 표시32×32·충돌24×24·위치를 유지한다.
- 원본 `assets/images/recycling_bin.png` 보존, 신규 `assets/images/recycling_bin_pixel_v1.png` 사용.
- 기존 녹색 몸체·크림색 테두리·투입구·재활용 기호와 투명 여백을 참고해 제작했다.
- 대상 전용 캐시에 초기화 시1회 로드하며 실패하면 기존 이미지를 사용한다. 다른 분리수거함은 기존 이미지 그대로다.
- 제작 도구: 내장 image_gen, transparent_background=true. 생성 자산의 정확한 픽셀 격자/실제32px 표시 가독성은 수동 확인 대상이다.
- 함께 수정: 배달소 수령·복귀 위치의 고객 캐릭터 표시를 제거했다. 배송지 고객 표정과 기존 판정은 변경하지 않았다.
- 게임 실행·테스트·커밋은 하지 않았다.

## 제작 프롬프트

Use case precise-object-edit/style-transfer. Image1 original recycling bin is EDIT TARGET. Image2 bench and Image3 depot are STYLE REFERENCES only. Redraw ONLY original overhead square recycling-bin lid as crisp low resolution pixel art. Preserve exact square1254x1254 transparent canvas and original footprint approx x165..1085,y170..1090 including original transparent margins. Preserve muted sage green body, cream rim, top and bottom hinges, dark horizontal rectangular slot at lower center, cream recycling three-arrow symbol above slot. Same top-down orientation, no facade, no perspective rotation. Designed for32x32 game display: prioritize bold readable silhouette, simple recycling glyph and slot, logical16x16 pixel density (about78px output blocks per2px screen) with limited3tone shades per material. Hard stepped corners, dark slate outlines, upper-left lighting, no smooth gradients, no glossy look. Match restrained palette of reference depot and bench. No ground, shadow outside footprint, extra props, labels, text or border outside object. Actual transparent background, original asset not overwritten.
