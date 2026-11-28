# 이미지 생성 기록

도구: 내장 image_gen, transparent_background=false. 게임 자산이 아닌 docs 아래의 미술 시안만 제작했다.

## 1차 시안

참조1: assets/images/title/title_city_v1.png — 스타일 우선.
참조2: assets/images/building_delivery_depot_pixel_v1.png — 배달소 정체성.
참조3: docs/art-direction/start-block/concept-v2.png — 초기 구도 참고. 잘못된 도로 연결을 따라간 문제가 있어 보정했다.

생성 파일 exec-ef2b6eea-5c3e-4140-96f0-f65bf8653bbb.png를 scene-draft.png로 복사했다.

Use case: ui-mock scene illustration, production art-direction concept only. Image1 PRIMARY STYLE REFERENCE city title pixel art. Image2 current orange delivery depot DESIGN IDENTITY reference only, must redesign to city style not copy huge icon. Image3 previous concept GEOMETRY reference only; don't copy its extra props or front-facing trees.

Create exactly1000x720pixel landscape GAME WORLD scene, NO HUD or text panels at all, genuine crisp2D pixel art, warm coherent cozy urban Korean delivery neighborhood. Maintain TRUE ORTHOGRAPHIC TOP-DOWN roofs, not isometric and no long frontal facades. World view corresponds to worldx250..1250,worldy90..810 with top-leftscreenpixelorigin. Road horizontal center screeny360, asphaltwidth120 => y300..420. Vertical roads centers screenx200 and800,width120 =>x140..260 and740..860. Both full-height verticals and horizontal are connected at (200,360),(800,360); cream curb14px eachside. Do not move roads, make extra lanes or invent links. Sidewalk pattern24pxsubtlewarm limestone slabs.

Scene layout in screenpixels (these are constraints):
- delivery depot center(500,660),320x320 TRANSPARENT-display-equivalentcanvas, roof actualpaint approx x355..645,y515..800 => cropped atbottom. Warm terracotta standing-seam roof with small cream box emblem only28x28, cream parapet NOT thickblack, short cream entrance/eave at north/top edge screeny520. No tall frontal wall. Readable northentry connects to quiet packed-paving forecourtx340..660,y420..590. Keep center approachcorridorx440..560,y420..550 clear; small pickup symbol at(500,460),not yellow hazardrectangle.
- rear/north orange house atcenter(500,-90),280squarecanvas, only narrow bottomroofedge visibleattopmiddle. No extra house in central lawn.
- cafe atcenter(200,660),280squarecanvas, only existingroof footprint in bottomleft behind verticalroad (on its SOUTH extension world layout; don't obscure roadcenter). blue housecenter(-100,660) largelyoffleft.
- bench at(380,230),display110square but actualpaint100x45centered; muted warmwood, slimmetal, topview.
- green recyclebin at(450,230),32square.
- tree at(650,210),110squaretopview canopy, clustered olive/yellowgreen masses with darktealunderside, no long visible trunk, no giant lime blob; shape and scale title foliagetranslatedtopdown.
- mailboxcenter(370,480),64squarecanvas,paintedbodyapprox34x32. Muted rustyred, cream mailmark.
- player topviewmotorcycle+riderat(500,360),canvas88square; minthelmet/orangeparcel, recognizable and highcontrast, no cars or extraNPC.
- remaining grassspaces lowcontrast olivegreen patches and subtle connected pavingedges; avoid brightflatneon lawn and busy randomnoise. Very sparse small weathering beside walls only, not new collisionprops.
- no flowerbed beside depot, no new lamp, fence, crates, parkedvehicle, street furniture or people beyondspecifiedexistingassets.

Art direction: match PRIMARY city title's cream/ochre/terracotta/teal family, darkdesaturatedasphalt#454B49, limestone#C8BEA5, cream#E3D0A5, grass#82965A/#A2AD68, foliage#597B43/#8EA848/#C2C76A, roofterracotta#BE7448, teal#487D7A, outlines#354744, upper-leftlight, short2-6pxdownright contactshadows limitedtoobjectfootprints. 2pxscreenpixelgrid, thin2pxoutlines, flat3toneclusters, believable smallscale integrated citymaterials. Detail concentrated on entries and useful shapes; quiet roadway and pickuparea. No airbrush, bloom, photoreal textures, big black borders, overlarge roofpictograms or pasted-on standalone iconobjects. No UI, lettering, labels or numbers in raster. This scene will be placed beneath an exact1280x720 HUD layout separately.

## 2차 보정 — 최종 방향안

편집 대상 scene-draft.png를 먼저 확인한 뒤 도로 연결과 화면 밖 건물/장식을 보정했다. 생성 파일 exec-5a1c75ca-c1c2-4837-a5db-776085d3503c.png를 scene-concept.png로 복사했다. 원본1478×1064이며 preview.svg에서1000×720 플레이 영역에 배치한다.

Use case precise-object-edit for game art-direction concept. Edit supplied scene draft to CORRECT MAP GEOMETRY. Keep overall1478x1064canvas and warm pixel-art style. Coordinates below are LOGICAL1000x720 units (multiply1.478 for actualimagepixels). Maintain true top-down no frontfacades.
CRITICAL remove LEFT FOUR-WAY INTERSECTION. Actual leftroad is a smooth NORTH-TO-EAST ELBOW ONLY: arc center logical(350,210), centerline radius150, quartercircle connecting(200,210)to(350,360). Roadwidth120 with14creamcurb. Leftverticalroad runs ONLY x200,y0..210, then curves southeast along arc to horizontalroad y360,x350..1000. There is NO road across logicalx0..140,y300..420 and NO verticalroad down logicalx140..260,y420..720. Replace those nonexistent west/south branches and crosswalks with muted olivegreen lawn and appropriate existing cafe footprint, seamless warm curb around curve. No crosswalk on this elbow. Keep RIGHT actual4way intersection at logical(800,360), verticalroadx800fullheight,width120. Rightcrosswalks may remain.
Remove all extra buildings in top-left, top-middle and rightedge; actual north house is OFFSCREEN. Main left lawn should be quiet lowcontrastgrasses, no steppingstones, no newtree orprops. Maintain only benchcenter(380,230)display110canvas actual100x45, bincenter(450,230)32square, treecenter(650,210)110crown, playerbikecenter(500,360)88square, mailboxcenter(370,480)64canvas. No extra shrubs or flowerbeds.
Place actual cafe center(200,660),280canvas with paintedfootprint approxlogicalx110..290,y576..755, top-down burgundyroof, creamtrim, smallcupmark and shortcream/burgundyawning only atbottom; bottomclipped. No facade. Not bluehouse.
Keep deliverydepotcenter(500,660),320canvas, actualpaint approxx355..645,y515..800,bottomclipped. Orange standingseamroof, smallboxemblem, northcreamdoor/eave, not tallfrontwall. Quiet forecourt logicalx340..660,y420..590 with clear approachx440..560, pickupsmallsymbolcenter(500,460), no hazardborder. Do not expand forecourt allthewaybetweenroads.
Keep lowcontrast warmolivegrass, limestonecreamcurbs, warmwood and terracotta, thin darktealoutlines, compacttopdownfoliageclusters. No UI, text, numbers, newprops, NPC or cars. Retain2pxscreenpixelstyle. This is feasible artwork proposal matched to actual startcamera; remove erroneous branches even if layout becomes asymmetrical.

## 한계

정확한 좌표·원근·픽셀 그리드 준수 여부는 프롬프트로 보장되지 않는다. 도로 중심 y위치, 오브젝트 크기, 카페 형태, 화분 생략 등은 art-direction.md에 명시했다. 실제 적용은 코드/맵과 layout-guide.svg를 우선한다. HUD는 생성 글자를 사용하지 않고 SVG로 기존 정보/비율을 표시한 예시다. 고객은 수령 대기 상태의 주화면에 임의 배치하지 않고 asset-board.svg에서 외형 참고로 표시했다.

