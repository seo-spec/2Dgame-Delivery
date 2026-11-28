# 도시 소품 생성 기록

내장 image_gen 도구를 사용했다. 배경 투명 PNG3종을 각각 생성해 원본을 덮어쓰지 않고 assets/images/title_match_v2에 저장했다. 실제 게임 화면 캡처가 아니다.

## parcel_locker

Create a SINGLE isolated 2D pixel-art game prop: a compact orange and warm cream neighborhood parcel locker bank, three columns of small parcel compartments and a tiny dark teal keypad, viewed from nearly straight overhead top-down (short south-facing front lip only, not isometric, no tall front elevation). Right-sized prop for a cozy Korean urban delivery game. Warm cream #E3D0A5, muted burnt orange #BE7448, dark outline #354744, muted teal accents #487D7A. Crisp large pixel clusters, restrained 3-tone shading with upper-left light, thin dark outline, tiny contact shadow integrated with object. Horizontal rectangular footprint, about 2.2 times as wide as deep. No text, no numbers, no logo, no background scene or ground tile. Transparent background; center one prop with generous transparent margin. Game-ready sprite, no frame or UI.

## utility_cabinet

Create a SINGLE isolated 2D pixel-art game prop: a small city electrical utility cabinet, two warm gray-cream metal doors with short ventilation slots and a discreet yellow warning triangle (no text), viewed nearly straight overhead in a TOP-DOWN 2D delivery game. A broad visible flat top and very short south front lip, no isometric perspective or tall facade. Muted warm gray #B7AE94, cream highlights #E3D0A5, dark thin outline #354744 and teal-gray shadow. Crisp low resolution pixel clusters, restrained 3-tone shading from upper left, small integrated contact shadow. Rectangular footprint about 1.5 times wide as deep. One compact cabinet only. Transparent background, centered with transparent margin. No people, no plants, no city scene, no ground tile, no letters or labels.

## cargo_pallet

Create a SINGLE isolated 2D pixel-art game prop: three modest brown cardboard delivery cartons sitting neatly on a small wooden shipping pallet, with one flat orange sealed carton, viewed almost directly from OVERHEAD TOP-DOWN, matching a cozy urban delivery game. Show tops and only a short south-facing edge; not isometric, not a tall pile. Muted cardboard #BE9363, warm wood #9F6744, cream tape #E3D0A5, thin dark #354744 outline. Crisp deliberate pixel clusters, restrained 3-tone upper-left lighting and short integrated contact shadow. Footprint horizontal rectangle about 1.7 times wide as deep. One small grouped prop only, no text, labels, shipping logos, background scene or ground. True transparent background with clear margin.

## 저장 파일

- assets/images/title_match_v2/parcel_locker_city_v1.png
- assets/images/title_match_v2/utility_cabinet_city_v1.png
- assets/images/title_match_v2/cargo_pallet_city_v1.png

PNG 알파128 이상 외곽을2px 간격으로 읽고2px 여유를 둔 좌표를 frames.json에 기록했다. 이미지 파일의 픽셀은 별도 편집하지 않았고, 기존 초기화 로더에서 최종 게임 표시 크기로 준비한다.

