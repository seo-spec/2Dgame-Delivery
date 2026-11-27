# 북쪽 기본 주택 도트풍 1차 적용

## 추가 적용: 왼쪽 기본 주택(150,450)

- 원본과 도트 자산을 직접 비교해 같은 가로 지붕 구도·중앙 용마루·우측 환기구와 유사한 투명 여백을 확인했다. 두 파일 모두1254×1254, 모서리 알파0이다. 외곽이 픽셀 단위로 동일하다는 검증은 아니다.
- 기존 `building_sample_pixel_v1.png`를 재사용한다. 북쪽 주택과 같은 캐시 키를 사용해 초기화 시 이미지1개만 로드하며, 실패 시 원본 캐시도 공유한다.
- 추가 대상은(150,450)의 기본 주택1개다. 기존 표시260×260, 충돌offset(0,-3)/size195×136, 위치를 유지한다. 다른 건물·소품·HUD·규칙은 변경하지 않았다. 신규 이미지 제작도 없다.
- 실행 테스트·커밋은 하지 않았다. 대상 주택의 크기·실루엣·충돌 대응과 다른 주택의 유지 여부는 수동 확인 대상이다.

## 최초 적용 기록

### 추가 재사용: 북서쪽 기본 주택(150,750)

원본과 도트 자산의 가로 지붕 구도·투명 여백을 다시 확인해 기존 자산과 동일 캐시를 재사용했다. 이 주택의 기존 표시240×240, 충돌offset(0,-2)/size180×124, 위치를 유지한다. 신규 파일 로드 경로는 추가하지 않고 기존 공유 캐시의 원본 폴백을 그대로 사용한다. 다른 건물·지면·소품·HUD·규칙은 변경하지 않았다. 실행 테스트·커밋은 하지 않았다.

후속 검토: 길·풀은 현재 출발지 일부의 절차적2px 질감만 적용되어 있어 타이틀의 포장 패턴·풀 덩어리·재질 경계와 차이가 남아 있다. 다음 작업에서 타이틀 이미지를 기준으로 출발지 지면의 실제 패턴과 팔레트를 재검토한다. 색상만 밝게 바꿔 구역 경계가 어둡게 보이는 문제를 반복하지 않도록 기존 지면과 경계 색도 함께 검토한다. 이번 주택 작업에서는 지면을 변경하지 않았다.

- 대상: `collision_preview_house` 한 채, 월드(750,900), 표시280×280.
- 원본: `assets/images/building_sample.png` 보존.
- 새 자산: `assets/images/building_sample_pixel_v1.png`.
- 기존 지붕 색·중앙 용마루·우측 환기구와 투명 여백을 참고해 별도 제작했다. 이미지 전체를 같은 표시 크기로 사용하며 다른 주택의 공유 원본은 교체하지 않는다.
- 초기화 시 대상 전용 키로 로드/캐시하고 OSError 발생 시 기존 이미지를 캐시한다. 위치·표시 크기·충돌·배송 구역은 그대로 사용한다.
- 제작 도구: 내장 image_gen, transparent_background=true. 화면2px 기준을 목표로 제작했으며 생성 자산의 완전한 격자 일치는 미검증이다.
- 실행 테스트와 커밋은 수행하지 않았다. 실제 합성 화면·투명 경계·충돌 실루엣 대응은 수동 확인 대상이다.

## 제작 프롬프트

Use case style-transfer precise-object-edit. Image1 is edit target: overhead house roof sprite. Image2 is STYLE REFERENCE ONLY: new delivery depot sprite. Redraw ONLY image1 as crisp top-down pixel art matching image2 palette density and hard edges. Preserve exact image1 square canvas, transparent padding, roof footprint and position: terracotta rectangle roughly x155..1095 y315..965 on a1254x1254 canvas, centered horizontally, original roof occupies about75% width and52% height. DO NOT expand roof to fill canvas. Preserve horizontal central ridge, orange/red ceramic tile pattern with simple chunky pixel seams, thin cream rim and small charcoal rectangular vent at upper-right. No parcel logo, no windows or new structures. Keep orthographic overhead, no facade/isometric perspective. Limited3-4 color shades, upper-left light, hard stepped edges, no glossy gradients. Native logical sprite140x140 scaled to280x280 game display, aim output blocks about9px for2px screen pixels. Outer outline dark #28383B, roof terracotta #C77543 and #9F5635, cream rim #C8BDA4. Actual transparent background and large original transparent top/bottom margins. No ground, no cast shadow outside footprint, no text, no surrounding props. Preserve identity and exact transparent footprint alignment so current collision and delivery zone remain usable. Final image is standalone house sprite only.

## 별도 후속 항목

사용자 캡처의 큰 노란 사선 배송 마커는 이번에 변경하지 않았다. 입구와 연결되는 작은 목적지 기호·짧은 바닥선·접근 시 조작 안내로 개선하는 요구사항을 `art-direction.md`에 추가했다.
