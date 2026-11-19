# 도트 도시 타이틀 자산

2026-11-19 사용자 요청에 따라 탑뷰 도트 도시와 자동차·오토바이의 순환 주행으로 제작했다. 내장 `image_gen` 도구를 사용했다. 기존 `title_background_v1.png`는 대체 배경으로 보존한다.

| 파일 | 실제 크기 | 용도 |
| --- | --- | --- |
| `title_city_v1.png` | 1672×941 | 차량이 없는 도시 배경, 1280×720으로 출력 |
| `title_car.png` | 926×1698, 실제 투명 알파 | 위쪽을 바라보는 자동차, 이미지 하나를 3대가 공유 |
| `title_motorcycle.png` | 962×1635, 실제 투명 알파 | 위쪽을 바라보는 배달 오토바이, 이미지 하나를 3대가 공유 |

모든 크기는 생성 결과를 그대로 보존했다. 차량의 투명 여백은 `game/config/title_animation.py`의 clip 영역으로 제외하고 회전 중심을 맞춘다. 차량 위치·출력 크기·속도·차선은 같은 설정 파일에서 관리한다. 텍스처는 최근접 보간으로 출력한다. RGBA 환산 합계는 약 18MiB이며 배경 1회·차량 6회 출력이다.

아래는 최종 선택 자산의 생성 프롬프트다.

`title_city_v1.png`는 참고 이미지 없이 생성했다. 도구에는 불투명 배경을 요청했다.

```text
Create a production PIXEL ART 2D game title background, 16:9 landscape, exactly 1280x720 if possible. Strict 90-degree bird's eye TOP DOWN orthographic city map, no perspective or isometric. Authentic detailed 16-bit pixel art with crisp visible square pixels, limited palette, hard edges, no gradients or antialiasing, no painterly brushes. Korean neighborhood courier delivery game, cheerful daytime muted sage grass, charcoal gray asphalt, cream sidewalks, small orange brick and teal roof shops, delivery depot with stacked boxes, trees, crosswalks, lane dashed lines. The city fills entire screen. Layout precise for moving vehicle overlays: left 62 percent contains a connected RECTANGULAR ROAD LOOP: vertical road centerlines x=145 and x=690 pixels, horizontal road centerlines y=185 and y=580 pixels on a1280x720 canvas, each road width 76 pixels, clean straight asphalt center portions and broad square intersections. Four intersections at145,185 /690,185 /690,580 /145,580. Add crosswalks near junctions. Road loop is continuous and fully unobstructed, no parked vehicles on asphalt. Middle block between roads contains small shop roofs, courtyard and colorful parcel depot. Top edge and bottom edge show cropped city blocks. Right side x=800..1280 is a single large low-contrast dark slate-teal warehouse rooftop surrounded by small quiet curb details, leave x=800..1240 y=230..580 completely plain dark roof surface for readable overlaid game menu. This dark area must be integrated naturally as a warehouse roof in the city map. No title text, no letters, no UI, no cars, no motorcycles, no moving objects, no people. Vehicle overlays will be added in engine. Crisp charming polished coherent sprite-based indie 2D city game environment. Pixel art, pixel art, visible square pixel clusters.
```

`title_car.png`는 `title_city_v1.png`를 화풍 참고로 사용했다. 도구에는 투명 배경을 요청했다.

```text
ONE isolated 16-bit PIXEL ART compact coral-orange sedan car sprite on actual fully transparent background. Match reference city pixel art style and crisp square pixel clusters. Strict directly overhead 90-degree TOP DOWN view, car hood faces the TOP of image, symmetric roof, dark windshield, small dark wheels, tiny cream headlights at top, red taillights bottom, very subtle 1pixel shadow close to body. NO perspective, no isometric, no road, no ground rectangle, no UI, no text, no multiple cars, no sprite sheet. Single centered small game car silhouette in transparent canvas with useful tight framing and 10% transparent margin. Crisp discrete pixel clusters, limited color palette, no smooth airbrushed or realistic details. Intended final displayed size 24px wide by44px tall.
```

`title_motorcycle.png`는 도시 배경을 화풍 참고로, `assets/images/motorcycle/motorcycle_16.png`를 헬멧·옷·배달 상자 색 참고로 사용했다. 도구에는 투명 배경을 요청했다.

```text
ONE isolated strict top-down PIXEL ART motorcycle courier sprite on actual transparent background. Match the FIRST reference pixel city style, use SECOND reference only for mint green helmet, navy jacket, orange parcel box identity. Exactly vertical, bike front wheel and tiny cream headlight point UPWARD to TOP edge, rear orange delivery cargo box at BOTTOM. Seen directly overhead 90 degrees, symmetrical, rider hands on handlebar, mint round helmet center, navy shoulders. Compact dark motorcycle with black wheels, tiny light. Authentic 16-bit game sprite, crisp square pixel clusters, discrete limited palette, NO painterly texture, no perspective or isometric. Single centered cutout, no ground, no backdrop, no text, no multiple views, no sheet, useful tight framing with about 10% transparent margin. Intended in-game silhouette20 pixels wide by34 tall.
```

도구에 요청한 크기·좌표와 실제 출력은 차이가 있어 실제 도로 위치를 기준으로 주행 경로를 맞췄다. 최종 차량 출력은 원본 비율에 맞춰 자동차 24×48, 오토바이 18×36으로 설정했다. 프롬프트의 초기 출력 크기와 현재 설정을 구분한다.
