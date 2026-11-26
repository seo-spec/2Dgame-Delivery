# 벤치 1개와 기다리는 배송 고객

## 벤치

- 대상: 월드(630,580), 표시110×110, 충돌100×45. 기존 수치를 유지한다.
- `assets/images/bench.png` 원본 보존. `assets/images/bench_pixel_v1.png`를 대상 한 개의 전용 캐시로 로드하며 실패하면 원본을 사용한다.
- 원본/새 이미지 모두1254×1254이며 모서리 알파0을 확인했다. 전체 투명 여백의 픽셀 일치까지 보장한 것은 아니다. 표시 크기와 실루엣 대응은 수동 확인 대상이다.

## 배송 표시 변경

- 작고 흐린 기호만으로는 목적지를 알아보기 어렵다는 사용자 피드백에 따라 기다리는 고객을 주 표시로 변경했다.
- `assets/images/markers/customer_moods_v1.png`: 2172×724, 동일한724×724 셀3개. 만족/보통/불만 순서. 전체 셀을72×72로 표시하고 실제 인물은 투명 여백 안에서 약30×58px 크기다.
- 같은 캐릭터의 표정만 바뀌며 발 위치는 고정된다. 무작위 이동·회전·별도 충돌 영역은 없다.
- 고객 위치는 기존 배송 구역 안에 준비하며 차량 접근에 따라 갑자기 다른 모서리로 이동시키지 않는다. 그림은 오토바이보다 먼저 그려 차량이 가릴 수 있으며, 기존 조작 안내와 목적지 이름은 계속 제공한다.
- 수령 대기 중 표정은 보통. 배송 중 표정은 기존 `get_customer_mood(elapsed_time)`의 만족/보통/불만과 동일하다. 완료 고객은 `delivered_mood`를 유지하고 체크로 완료를 표시한다.
- 수령/복귀 위치에는 사람을 표시하지 않는다. 배달소는 아래 화살표/집 기호를 사용하고 고객 캐릭터는 배송지에만 표시한다. 복귀는 기존 자동 판정을 유지한다.
- 짧은 바닥선은 기존 실제 구역과 대응하는 보조 표시로 남기고 대비를 높였다. 활성 배송의 핀과 완료 체크는 얼굴 옆에 작게 표시한다.
- 고객 이미지가 없으면 기존 작은 기호로 표시한다. 이미지는 초기화 시1회 로드하고 모든 고객이 공유하며, 화면 밖 구역은 그리지 않는다.
- 기존 건물·지면·HUD 패널·수령/배송 판정은 변경하지 않았다. 벤치 대상1개와 마커만 변경했다.

## 제작 도구와 프롬프트

두 이미지 모두 내장 image_gen, transparent_background=true로 제작했다.

### 벤치

Edit target Image1 original park bench sprite, Image2 style reference pixel roof. Redraw bench only in crisp 2D overhead pixel art, keep original warm orange brown wooden slats and dark gray iron supports, exact horizontal orientation, original transparent square canvas1254x1254 and footprint approximately x48..1205 y372..890. Keep large transparent padding top and bottom, do not enlarge or crop bench. Six horizontal boards, simple wood tone3shades, hard stepped outlines, upper-left light. Pixel blocks about20px in output to correspond2px when displayed110x110. No ground, cast shadow, props or text, no perspective changes, actual transparent background.

### 고객

Create production transparent PNG SPRITE SHEET for cozy Korean top-down delivery game, matching muted terracotta/cream/dark slate pixel art reference. Landscape3:1 canvas, THREE EXACT EQUAL WIDTH COLUMNS and ONE ROW. Same identical waiting adult customer repeated, registered at same local position and scale in each cell. Left expression HAPPY smile; middle NEUTRAL straight mouth; right IMPATIENT annoyed eyebrows/frown. Same hair, clothes, pose, proportions, colors and feet baseline; ONLY face expression changes. No labels, no dividers, no text, no icons. Actual transparent background. Every character fully visible inside own cell with modest10% transparent padding. Cute readable chibi game sprite, 3/4 OVERHEAD RPG perspective facing south (toward player), big face to clearly read emotion at screen height56px, dark short hair, warm light skin, muted ochre shirt, blue-gray trousers, dark shoes. Standing still waiting, arms resting, no item held. Pixel blocks, dark1px native outlines, flat3tone shading, native character approx24x32 logical pixels. No painterly blending, no photorealism, no ground, no cast shadow. Face smile vs neutral vs annoyed MUST be visually distinct. Keep three frames centered at1/6,1/2,5/6 canvas width, identical feet baseline and full body size. Use reference ONLY for art palette, never depict building.

## 수동 확인 항목

- 벤치 한 개만 새 스타일로 바뀌고 기존 크기·충돌이 유지되는지.
- 같은 배송지에서 만족→보통→불만 표정이 오른쪽 HUD의 기분과 같은 시점에 바뀌는지.
- 대기 상태의 보통 표정과 완료 당시 표정 유지가 맞는지.
- 가로/세로 배송 구역에서 고객이 입구·건물·집 이름과 겹치지 않는지.
- 차량 접근 시 고객이 움직이지 않고 Space 안내·실제 배송 가능 조건이 기존과 같은지.
- 수령·복귀·완료 역할을 읽을 수 있고 카메라 가장자리에서 불필요한 표시가 남지 않는지.

게임 실행·자동 테스트·커밋은 수행하지 않았다. 특히 인물과 차량의 크기 관계 및 실제 합성 화면의 겹침은 미확인이다.
