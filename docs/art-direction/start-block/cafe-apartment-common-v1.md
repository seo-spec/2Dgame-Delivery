# 카페·아파트 공통 도트 자산 적용

## 자산과 적용 범위

- 카페 7개: 기존 building_cafe_pixel_v1.png를 재사용한다. 출발지 (450,150)의 이미지를 다시 제작하거나 덮어쓰지 않았다. 나머지 카페는 (750,1950), (2850,1050), (3450,1650), (150,2550), (1650,2550), (2250,2550)이다. 모두 표시 280×280이다.
- 아파트 10개: 새 assets/images/building_apartment_pixel_v1.png를 공유한다. 위치는 (1950,150), (150,1950), (1350,1950), (2250,1950), (2850,1650), (3450,2250), (450,2550), (1350,2550), (1950,2550), (3150,2550)이다. (2850,1650)만 기존 300×300, 나머지는 280×280을 유지한다.
- 원본 building_cafe.png, building_apartment.png와 출발지 카페 도트 PNG는 보존한다. 지면·소품·HUD·맵 좌표·충돌·배송 구역·고객·입력 조건은 수정하지 않았다.

## 미술 비교

타이틀과 기존 도트 건물/소품의 청회색 외곽선, 크림 테두리, 제한된 명암과 계단형 픽셀을 기준으로 했다. 카페는 적자색 지붕·커피잔 표식·둥근 천창·줄무늬 차양을 유지하는 기존 자산이 있어 재사용했다. 아파트는 회보라 평지붕·크림 난간·좌측 배기구 2개·우측 옥탑방·하단 실외기 2개와 배관을 유지하며 윤곽과 재질 표현을 도트풍으로 정리했다. 탑다운 시점과 좌상단 광원을 유지한다. 외벽 입구나 진입부는 추가하지 않았다.

## 이미지 메타데이터 확인

아래 외곽은 알파 128 이상을 2px 간격으로 읽은 표본 범위이며 완전한 픽셀 일치 검증은 아니다.

| 이미지 | 캔버스 | 표본 외곽 (left,top,right,bottom) |
|---|---|---|
| 아파트 원본 | 1254×1254 | (78,234,1176,1042) |
| 새 아파트 | 1254×1254 | (74,230,1178,1046) |
| 카페 원본 | 1254×1254 | (226,260,1028,1040) |
| 기존 도트 카페 | 1254×1254 | (218,254,1034,1048) |

네 이미지 모두 좌상단 모서리 알파 0이다. 아파트 외곽 차이는 원본 좌표 기준 최대 4px, 300×300 표시 기준 약 0.96px다. 넓은 투명 여백과 배치 구도는 호환되지만 최종 화면 정합은 미확인이다. 공유 이미지의 280/300 표시 크기 차이로 도트 밀도에 약 7% 차이가 있으며 기존 크기를 우선한다.

## 로드와 출력

- create_decorations 초기화 시 cafe/apartment 키별 1회 로드한다. 출발지 전용 중복 로드 분기를 제거해 카페 전체가 같은 이미지와 캐시를 사용한다.
- 새 자산 실패 시 해당 원본을 한 번 로드하고 실패 결과도 공유한다.
- 최근접 텍스처 필터를 명시한다. 전체 표시 캔버스가 화면 밖이면 이미지를 출력하지 않는다.
- 매 프레임 이미지 생성·파일 로딩은 없다. 표시되는 건물당 기존 1회 출력을 유지한다.
- 두 공유 PNG의 RGBA 환산 합계는 12,580,128바이트(약 12MiB)다. 건물 개수만큼 텍스처를 복제하지 않는다. 기존에는 카페 원본+출발지 도트 카페+아파트 원본이 함께 로드되었지만 성공 경로에서는 두 장만 로드한다. 메모리는 환산값이며 실측값은 아니다.

## 수동 확인

- 출발지 카페가 기존 모습이고 다른 카페도 같은 도트풍인지.
- 아파트의 지붕·옥탑방·배기구·실외기 배치와 투명 테두리가 자연스러운지.
- 300px 아파트와 280px 아파트의 밀도 차이가 과하지 않은지.
- 기존 충돌·배송 구역·고객·느낌표·입력 조건이 유지되는지.
- 카메라 이동·재시작 후 누락이나 잘림이 없는지.
- 다른 건물·지면·소품·HUD가 유지되는지.

실행 테스트와 커밋은 하지 않았다. 실제 합성 화면과 로드 실패 경로 실행 결과는 미확인이다.

## 제작 도구와 프롬프트

내장 image_gen 편집, transparent_background=true. 원본 building_apartment.png를 편집 대상으로 사용했다. 생성 파일 exec-2a32057a-7c00-4530-a091-f94446580acb.png를 프로젝트의 새 아파트 자산으로 복사했다. 카페는 이미지 생성 없이 기존 자산을 재사용했다.

Use case style-transfer. EDIT TARGET supplied top-down apartment rooftop sprite. Preserve exact1254x1254 square transparent canvas and existing silhouette approxx75..1178,y232..1042, no recentering or cropping. Keep gray-lavender flat roof, cream parapet, two small dark exhaust pipes upper-left, cream rooftop stairwell upper-right with gray roof and south-facing small door, two beige AC units lower-left and connecting pipes. Match established cozy2D delivery game pixel-art: dark blue-charcoal stepped outlines, limited3-4flat tones per material, upper-left light and short shadows inside footprint, large quiet low-contrast roof patches. Top-down orthographic roof view, no isometric building sides or extra facade. Approx140x140 logical grid shown280x280, 2pxscreen pixel clusters; sharp square stepped edges, no airbrushed shading or noise. Original positions/proportions/color identities and transparent margins must remain. No new ground, pathways, entrances on outer walls, people, props, signage, letters, external shadow or glow. Genuine transparent background outside silhouette. One apartment roof game asset only.

