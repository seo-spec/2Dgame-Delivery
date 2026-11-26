# 우편함 1개와 남녀 대기 고객

- 우편함: 월드(620,330)의1개만 새 `assets/images/mailbox_pixel_v1.png` 적용. 기존 원본·표시64×64·충돌34×32·위치는 유지한다. 초기화 시 전용 캐시 로드, 실패하면 원본 사용.
- 원본과 새 우편함은1254×1254이며 모서리 알파0 확인. 전체 실루엣과 표시 가독성은 실제 화면에서 수동 확인해야 한다.
- 고객: 기존 남성3표정과 새 `assets/images/markers/customer_female_moods_v1.png`를 공유한다. 여성 시트는2172×724로 남성 시트와 같은724×724 셀3개이며 만족/보통/불만 순서다.
- 배송지 목록 순서대로 남녀를 번갈아 배정한다. 기본5곳이면 남성3명·여성2명이며, 실행 중 외형은 바뀌지 않는다. 게임 재시작 때 배송지 추첨 결과가 달라지면 물리적 건물의 외형 배정도 달라질 수 있다. 외형 저장 기능은 추가하지 않았다.
- 표정은 기존 기분 계산을 따르고 완료 당시 기분을 유지한다. 배달소에는 사람을 표시하지 않는다.
- 미배송 고객 머리 위에는 거리와 무관하게 어두운 바탕의 밝은 `!`를 표시하며, 완료 즉시 없앤다. 실제 상호작용 가능 여부를 나타내는 기존 조작 안내/강조와 미배송 표시는 별개다.
- 고객은 기존 구역의 오른쪽 안쪽에 고정 배치해 구역 왼쪽에서 시작하는 집 이름표와 가로 위치를 분리했다. 모든 문구 길이·지형에서 겹치지 않는다는 실행 검증은 미수행이다.
- 위치·충돌·수령/배송 조건·지면·HUD 패널은 변경하지 않았다. 캐릭터에 새로운 충돌은 없다.
- 이미지는 초기화 시 로드하고 공유한다. 외형 하나 로드 실패 시 다른 외형, 둘 다 실패하면 기존 바닥 기호를 사용한다. 카메라 밖 출력 생략에는 머리 위 표시 범위도 포함한다.
- 실행 테스트와 커밋은 수행하지 않았다.

## 제작 도구와 프롬프트

내장 image_gen 도구, 두 이미지 모두 transparent_background=true.

### 우편함

Edit target Image1 red mailbox sprite; Image2 recycling bin style reference only. Redraw same mailbox as crisp overhead 2D pixel art matching muted palette. Preserve square1254x1254 transparent canvas, footprint x285..965 y310..955, same rounded red top lid, cream envelope symbol, horizontal dark slot below, two short mounting tabs. No enlarging subject, same transparent margins and orientation. Designed64x64 display, chunky output blocks about40px for2px screen, dark slate outline, limited3shade red/terracotta, upper-left light. No smooth gradients, no ground, no external shadow, no text, no extra props. Actual transparent background. Preserve original shape and colors.

### 여성 고객

Edit target reference male customer mood sprite sheet. Create matching FEMALE CUSTOMER sheet, same exact3:1 landscape canvas, THREE equal square columns ONE row, identical local body center and feet baseline as reference. Change all three characters to same adult woman with short chestnut bob haircut, muted teal blouse, dark blue-gray trousers and dark shoes. Same chibi body/head proportions, same top-down RPG standing south-facing perspective, same scale/padding (head near10% cellheight feet90%), pixel density, outlines, flat shading and warm skin. LEFT happy smiling face, MIDDLE neutral straight-mouth, RIGHT impatient annoyed eyebrows/frown. Within this sheet ONLY expression changes, body/hair/clothing/position must match across all3frames. Faces clearly readable at game sprite height58px. Actual transparent background. No text, labels, separator, ground, outside shadows, speech bubbles or extra props. Preserve frame registration exactly so existing equal-third clip and72x72 canvas display can be shared.

## 수동 확인

- 대상 우편함1개만 바뀌고 기존 위치·표시 크기·충돌이 유지되는지.
- 남녀 고객이 섞이고 기분에 따라 각각 세 표정이 나오는지.
- 미배송 `!`가 접근 전부터 보이고 배송 완료 후 사라지는지.
- `!`·기존 집 이름·차체 위 상호작용 표시가 겹치지 않는지.
- 배달소에 사람이 없고 수령·배송·복귀 조건이 유지되는지.
