# LUCASGOTCHI mini 작업 규칙
- 다마고치 웹앱(PWA) + 안드로이드 앱(WebView) + 홈 화면 위젯. GitHub Pages로 배포. 응답은 한국어로.
- 내 방만 있음. 버튼: 왼쪽 쓰다듬기(bA) · 가운데 재우기(bB) · 오른쪽 밥 먹기(bC). 아래에서 옷·배경·테마만 변경.
- sprites.js는 base64 그림 데이터라 큼. 그림을 추가/수정하는 작업이 아니면 열지 말 것.
- index.html이나 다른 웹 파일을 수정하면 sw.js의 VERSION을 항상 하나 올릴 것.
- 오프라인에서도 동작해야 함.
- 기존 저장 데이터(localStorage `lucasgotchi-mini:v1`)는 지우거나 초기화하지 말 것. 새 항목은 없을 때 기본값으로 처리.
- 요청받은 부분만 수정하고, 관련 없는 코드는 건드리지 말 것.

## 파일 구조
- `index.html`: 화면 전체. `renderLCD(c,V,t)` 가 LCD 한 장을 그림 (앱 화면·위젯 그림 공용).
  - 위젯 그림은 앱 안(window.LGAndroid 있을 때)에서 `widgetSync()` 가 만들어 넘김: LCD 프레임(`wVariants`), 껍데기 `shell.img`, 배경 `bg.img`.
  - LCD 그림 규칙을 바꾸면 `LCD_VER` 를 하나 올려야 위젯 그림이 다시 만들어짐.
- `backgrounds.js`: 내 방 그림(`makeRoom`), 페이지 배경 프리셋(`PAGE_BG`).
- `sw.js`: 오프라인 캐시 (캐시 이름 접두어 `lgmini-`).
- `android/`: WebView 앱 + 위젯 (Java, AndroidX 없음).
  - `GameState.java`: 위젯 쪽 상태 규칙 (index.html 메인 루프와 같아야 함).
  - `LgWidget.java`: 위젯 그리기·버튼. `widget.xml` 의 weight 숫자는 index.html `WBOX`(398×518) 기준.
  - android 폴더를 고치면 GitHub Actions 가 APK 를 새로 만들어 Releases 에 올림.
- `kakao-theme/`: 카카오톡 안드로이드 테마. `gen.py` 가 `src/` 그림으로 `theme/`(res + 매니페스트)를 만듦 → 고친 뒤 꼭 다시 돌려 `theme/` 도 커밋.
  리소스·색 이름은 카카오 공식 안드로이드 테마 가이드(9.2.5)에 있는 것만 씀. Actions(`kakao-theme.yml`)가 `kakao-theme/apk`(Gradle)로 APK 를 묶어 Releases(theme-vN)에 올림.
  카톡이 테마로 알아보는 표시(`com.kakao.talk.v2.theme` 권한, `com.kakao.talk.theme.action.MAIN` 화면)를 매니페스트에서 빼면 안 됨.
