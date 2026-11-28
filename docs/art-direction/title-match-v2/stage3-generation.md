# 3단계 이미지 제작 기록

2026-11-28. image_gen 도구로 기존 v1/v2와 타이틀을 참고해 부족한 종류 9종을 제작했다. 기존 PNG는 덮어쓰지 않았다.

공통 주택·파란 주택·상점·아파트는 기존 탑다운 형태와 색상을 유지하며 따뜻한 재질·얇은 윤곽·절제된 명암으로 제작했다. 공통 지붕에 임의 입구를 추가하지 않았다. 입구 변형 3종과 버스 정류장·분수는 아래 제작 지시를 사용했다.

## house_entrance

Use case precise-object-edit. Keeporiginaltransparentcanvas, existingtopdowngeometry/footprint/margins. Warmcozycitypixelart, matteflat3tones, upperleftlight, thin2screenpixel darkteal#354744outlines, cream#E3D0A5trim (totalrim24sourcepixels for1254canvas), short2..4screenpixelcontactshadewithinfootprint. No newground/props/people, no newdoor ororientationchange, no airbrush/glow. 1254squarecanvas, orangehippedroof footprintx148..1104,y312..970, centralridge andupperrightvent. Mutedterracotta#8E513C/#BE7448/#DA9A60, quietlargertileclusters. PRESERVE existing small SOUTH wooddoor centeredx627,bottomy970 facingSCREENBOTTOM, narrowcreamwallinbottomroofband. Doorbottom,widthandlocationstay; no porch/path added. Thinnercreamriminsideexistingfootprint.

## blue_house_entrance

Use case precise-object-edit. Keeporiginaltransparentcanvas, existingtopdowngeometry/footprint/margins. Warmcozycitypixelart, matteflat3tones, upperleftlight, thin2screenpixel darkteal#354744outlines, cream#E3D0A5trim (totalrim24sourcepixels for1254canvas), short2..4screenpixelcontactshadewithinfootprint. No newground/props/people, no newdoor ororientationchange, no airbrush/glow. 1254squarecanvas, bluehippedroof footprintx58..1196,y298..978, centralridge/upperrightskylight. Mutedslateblue#405B67/#627E8C/#8CA0A4; quieterfewerhighcontrasttilemarks. PRESERVE existing SOUTHwooddoor centeredx627,bottomy978 andbottomcreamwallstrip. Same doorlocation/sizeandorientationSCREENBOTTOM; no path.

## shop_entrance

Use case precise-object-edit. Keeporiginaltransparentcanvas, existingtopdowngeometry/footprint/margins. Warmcozycitypixelart, matteflat3tones, upperleftlight, thin2screenpixel darkteal#354744outlines, cream#E3D0A5trim (totalrim24sourcepixels for1254canvas), short2..4screenpixelcontactshadewithinfootprint. No newground/props/people, no newdoor ororientationchange, no airbrush/glow. 1254squarecanvas, tealflatrooffootprintx88..1164,y292..962, two upperleftvents andupperrightACwithpipe. Palette#355B5A/#487D7A/#6A9990. PreserveEXISTINGSOUTHglassdouble door centeredx627,y930 bottomy962, facingscreenbottom. Keepdoorlocationandwidth, no addedpath. Narrowcreamriminsideoriginalfootprint, sparseflatquietroofpatches.

## bus_stop

Use case precise-object-edit. Keeporiginaltransparentcanvas, existingtopdowngeometry/footprint/margins. Warmcozycitypixelart, matteflat3tones, upperleftlight, thin2screenpixel darkteal#354744outlines, cream#E3D0A5trim (totalrim24sourcepixels for1254canvas), short2..4screenpixelcontactshadewithinfootprint. No newground/props/people, no newdoor ororientationchange, no airbrush/glow. 1536x1024landscapecanvas, same shelterfootprintx98..1438,y336..704. Keepteal6panelcanopy, creamframe, shortglassbackpanel, brownbench, rightbuspictogram, allpositions. Mutedteal#355B5A/#487D7A/#6A9990, warmwood#A9794F, cream#E3D0A5. Thinrimsandquietglassreflection, no tallfrontwall, preserveoverheadview. Outerhalomustbezeroalphatransparent, no shadowoutsidefootprint.

## fountain

Use case precise-object-edit. Keeporiginaltransparentcanvas, existingtopdowngeometry/footprint/margins. Warmcozycitypixelart, matteflat3tones, upperleftlight, thin2screenpixel darkteal#354744outlines, cream#E3D0A5trim (totalrim24sourcepixels for1254canvas), short2..4screenpixelcontactshadewithinfootprint. No newground/props/people, no newdoor ororientationchange, no airbrush/glow. 1254squarecanvas, trueoverheadcircularpool footprintx100..1146,y108..1160. Preservecreamstonerim,fourcardinalsquareblocksandterracottadiamonds, smallcentralnozzle. Thinouteroutline, mutedstone#A69C86/#C8BEA5/#E3D0A5, calmwater#487D7A/#6A9990 withfewshortangularripplemarks. Reducecyanbrightnessandmanyconcentricrings. Sameproportions, no bigjet, no newobjects.

## 상점 알파 보완

상점 공통/입구 PNG의 지붕 중앙에 투명 오류가 남았다. 입구 이미지 재생성 후에도 남아, 파일을 변조하지 않고 SDL 초기화 합성으로 지붕 기본 면을 채우고 설비를 다시 얹는다. 좌표·색은 frames.json의 opaque_roof에 기록했다. 매 프레임 추가 출력은 없다. 합성 경계는 실제 화면 미확인이다.

## 여백과 해상도

frames.json에 각 PNG 실제 크기, 알파128 이상 외곽(2px 간격 표본+2px 여유), v1 기준 외곽을 기록했다. 파일을 자르거나 리사이즈하지 않고 초기화 표면에서 기존 외곽 기준으로 맞춘다. 생성 해상도와 게임 텍스처 해상도는 다르다. stage3-assets.svg는 이 정규화와 상점 합성을 설명하는 참고 보드이며 게임 캡처가 아니다.

