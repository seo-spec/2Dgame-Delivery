# 출발지 화분1개와 고객 등장 시점

- 대상: 월드(620,280), 기존 표시100×100, 충돌90×30 유지.
- `assets/images/planter.png` 보존, `assets/images/planter_pixel_v1.png`를 대상 전용 캐시로 초기화 시 로드한다. 실패하면 원본을 사용한다. 다른 화분은 바꾸지 않는다.
- 기존 크림색 가로 테두리·흙·녹색 잎·주황/노랑 꽃과 투명 여백을 참고해 도트풍으로 제작했다. 원본과 생성 파일은 모두1254×1254이며 모서리 알파0 확인. 정확한 격자와 실루엣 대응은 실제 표시에서 수동 확인 대상이다.
- 추가 요청: 수령 대기(`WAITING`) 중에는 배송지 고객과 머리 위 느낌표를 표시하지 않는다. 화물 수령 후 배송 상태로 전환되면 남녀 고객과 미배송 느낌표를 표시한다. 바닥 기호·구역·판정·기분 계산은 유지한다.
- 배송 완료 후에는 기존처럼 느낌표를 제거하고 당시 기분과 완료 표시를 유지한다. 배달소에는 사람을 표시하지 않는다.
- 게임 실행·테스트·커밋은 수행하지 않았다.

## 제작 도구와 프롬프트

내장 image_gen 편집, transparent_background=true. 원본 화분을 편집 대상으로, 새 벤치와 우편함을 화풍 참조로 사용했다.

Use case precise-object-edit/style-transfer. Image1 planter is EDIT TARGET, Image2 pixel bench and Image3 pixel mailbox are STYLE REFERENCES only. Redraw ONLY original top-down rectangular flower planter as crisp 2D pixel art. Preserve exact square1254x1254 transparent canvas, original long horizontal footprint approx x58..1195 y440..820 and large transparent top/bottom margins. Same beige cream stone rim, dark brown soil, three green leafy clusters and sparse orange/yellow flowers at same layout. No enlarging footprint, no perspective facade, overhead orthographic. Target game100x100 fullcanvas, logical50x50 native art, chunky output blocks about25px correspond2px screen. Limited3tone colors, stepped edges dark muted outline, upper-left light, simplify individual leaves to readable clusters. Match warm cream, muted green and terracotta reference palette. No smooth painterly gradients, no ground or outside shadow, no text, no extras. Actual transparent background, preserve original orientation and transparent padding.

## 수동 확인

- 대상 화분1개만 바뀌고 기존 위치·크기·충돌을 유지하는지.
- 게임 시작 직후와 재시작 직후에 배송지 고객/느낌표가 없는지.
- 화물 수령 직후 고객과 느낌표가 나타나는지.
- 배송 완료 후 느낌표 제거·기분별 표정·복귀 판정이 기존대로인지.
