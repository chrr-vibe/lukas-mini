"""LUCASGOTCHI 카카오톡 테마(안드로이드) 그림·색 만들기.

    python3 kakao-theme/gen.py          → kakao-theme/theme/res/ 와 AndroidManifest.xml
    python3 kakao-theme/gen.py --preview → 위 + kakao-theme/preview.png (확인용 화면 흉내)

그림을 고치면 이걸 다시 돌려 theme/ 를 같이 올려야 APK 에 반영됨 (Pillow 필요).

재료는 kakao-theme/src/ 의 PNG 다.
  - 캐릭터 그림(768×768): 원래 LUCASGOTCHI 의 sprites.js 그림을 4배로 합성한 것
    (루카스 앞머리 이음새는 다듬었고, lucasFull 은 고양이 귀·꼬리·딸기 장식을 단 것)
  - starry90.png: 페이지 배경 '별밤' (90×160 도트)

리소스 이름·색 이름은 카카오 공식 안드로이드 테마 가이드(9.2.5)를 따른다.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.join(HERE, 'theme')   # 만든 결과. 저장소에 같이 올리고, 빌드할 땐 이것만 묶음
DP = 3                       # xxhdpi: 1dp = 3px
SS = 4                       # 매끈한 테두리용 확대 그리기

PKG = 'lucasgotchi_starnight'
TITLE = '루카스고치 별밤'
VERSION = '1.0'

# ---- 색 (테마 5 분홍 + 별밤) ----
NAVY = '#2b2050'
C = {
    'bg': '#3d3a7a', 'bg_deep': '#2f2d63', 'surface': '#4d4890', 'pressed': '#5a52a3',
    'border': '#4b4690', 'text': '#fff4fb', 'text_hi': '#ffd1ea', 'subtext': '#cbbdf0',
    'subtext_hi': '#e6dcff', 'accent': '#ff8fc8', 'accent_dim': '#e46aa9', 'on_accent': '#ffffff',
    'button_text': '#f06aa8', 'button_text_hi': '#ffd1ea', 'line': '#00000000',
}
ME = '#ffb8de'      # 보낸 말풍선 (분홍)
YOU = '#e9defd'     # 받은 말풍선 (연보라)
SKIN = '#fff1ea'

COLORS = [
    ('theme_background_color', 'bg', None),
    ('theme_header_color', 'text', None),
    ('theme_header_cell_color', 'bg', None),
    ('theme_feature_browse_tab_color', 'subtext', None),
    ('theme_feature_browse_tab_focused_color', 'accent', None),
    ('theme_tab_bannerbadge_background_color', 'accent', None),
    ('theme_tab_lightbannerbadge_background_color', 'accent', None),
    ('theme_section_title_color', 'subtext', None),
    ('theme_title_color', 'text', None),
    ('theme_title_pressed_color', 'text_hi', None),
    ('theme_paragraph_color', 'subtext', None),
    ('theme_paragraph_pressed_color', 'subtext_hi', None),
    ('theme_description_color', 'subtext', None),
    ('theme_description_pressed_color', 'subtext_hi', None),
    ('theme_feature_primary_color', 'button_text', None),        # '선물하기'·'안읽음' 같은 흰 단추의 글자 → 진한 분홍
    ('theme_feature_primary_pressed_color', 'button_text_hi', None),
    ('theme_body_cell_color', 'bg', 0x00),          # 목록 칸 투명 → 별밤 그림이 그대로 보임 (색을 넣으면 그림이 가려지고 칸마다 끊김)
    ('theme_body_cell_pressed_color', 'pressed', None),
    ('theme_body_cell_border_color', 'line', None),
    ('theme_body_secondary_cell_color', 'surface', None),
    ('theme_maintab_cell_color', 'bg_deep', None),
    ('theme_chatroom_background_color', 'bg_deep', None),
    ('theme_chatroom_unread_count_color', 'accent', None),
    ('theme_chatroom_input_bar_color', 'text', None),
    ('theme_chatroom_input_bar_background_color', 'surface', None),
    ('theme_chatroom_input_bar_menu_icon_color', 'subtext', None),
    ('theme_chatroom_input_bar_menu_button_color', 'surface', None),
    ('theme_chatroom_input_bar_send_button_color', 'accent', None),
    ('theme_chatroom_input_bar_send_icon_color', 'on_accent', None),
    ('theme_direct_share_color', 'text', None),
    ('theme_direct_share_button_color', 'accent', None),
    ('theme_direct_share_background_color', 'surface', None),
    ('theme_notification_color', 'text', None),
    ('theme_notification_background_color', 'surface', None),
    ('theme_notification_background_pressed_color', 'pressed', None),
    ('theme_passcode_color', 'text', None),
    ('theme_passcode_background_color', 'bg_deep', None),
    ('theme_passcode_keypad_color', 'text', None),
    ('theme_passcode_keypad_pressed_color', 'accent', None),
    ('theme_passcode_keypad_background_color', 'surface', None),
    ('theme_passcode_keypad_pressed_background_color', 'pressed', None),
    ('theme_passcode_pattern_line_color', 'accent', None),
]

# 캐릭터 그림(768) 안에서 머리만 자를 아랫선(턱 바로 아래)
CHIN = {'lucas': 440, 'leo': 432, 'leoAcad': 432, 'meck': 420, 'adr': 446, 'eli': 438}
# 말풍선에 올라앉는 캐릭터는 가슴까지
PEEK = {'lucasSuit': 560, 'leoAcad': 560}
CHIN_PEEK = {'lucasSuit': 440, 'leoAcad': 452}

# 아래 탭 아이콘 = 게임 소품 (도트는 원래 게임 그림 그대로, 딸기 장식은 루카스 머리 장식 그림)
#   친구=딸기 장식, 채팅=독병(플레로마 미니게임), 지금=마법사 완드(미니게임), 쇼핑=딸기 케이크, 더보기=게임 하트
#   통화 탭이 보이는 폰이면 딸기 장식. browse/find/piccoma 는 예전 카톡 버전용 이름
OUTLINE = '#22102e'
PIX = {
    'poison': (['..KKK..', '..KCK..', '.KKKKK.', 'KGGGGGK', 'KGWGWGK', 'KGGWGGK', 'KGWGWGK', 'KGGGGGK', '.KKKKK.'],
               {'K': '#22102e', 'C': '#c9a24a', 'G': '#9b5cff', 'W': '#e8ddff'}, None),
    'wand': (['..Y..', '.YWY.', '..Y..', '..B..', '..B..', '..B..', '..B..'],
             {'Y': '#ffe066', 'W': '#ffffff', 'B': '#8a5a2b'}, OUTLINE),
    'cake': (['........o.......', '........y.......', '........c.......', '...kkk..c.ss....', '..kkkkk.sssssw..',
              '.wwwwwwwwwwwwww.', '.wwwwwwwwwwwwww.', '.bbbbbbbbbbbbbw.', '.bbbbbbbbbbbbbw.', '.wrrwwrrwwrrwww.',
              '.bbbbbbbbbbbbbw.', '.bbbbbbbbbbbbbw.', 'pppppppppppppppp', '.pppppppppppppp.'],
             {'o': '#ffb347', 'y': '#fff3a0', 'c': '#ff8fb1', 'k': '#6b3a2a', 's': '#e8343f', 'w': '#ffffff',
              'b': '#f7dc8c', 'r': '#ff5a6a', 'p': '#ffc4d6'}, '#5a2a3a'),
    # 게임 속 하트 (미니게임 목숨 하트)
    'heart': (['.KK.KK.', 'KPPKPPK', 'KPWPPPK', 'KPPPPPK', '.KPPPK.', '..KPK..', '...K...'],
              {'K': '#5a1030', 'P': '#ff4f8f', 'W': '#ffd6e8'}, None),
}
TABS = {'friends': 'berry', 'chats': 'poison', 'now': 'wand', 'shopping': 'cake', 'more': 'heart', 'call': 'berry',
        'browse': 'wand', 'find': 'wand', 'piccoma': 'cake', 'game': 'wand'}
# 요즘 카톡이 읽는 탭 선택기 이름 → 위 그림 이름
TAB_SELECTORS = {'friend': 'friends', 'chats': 'chats', 'now': 'now', 'shopping': 'shopping', 'more': 'more', 'call': 'call',
                 'browse': 'browse', 'find': 'find', 'piccoma': 'piccoma', 'game': 'game'}
COLOR_SELECTORS = ['title', 'paragraph', 'description', 'feature_primary', 'passcode_keypad']


def rgb(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def char(name):
    return Image.open(os.path.join(SRC, name + '.png')).convert('RGBA')


def crop_to(name, bottom, fade=10):
    """캐릭터 그림을 위에서 bottom 까지 자르고 옆 여백을 걷어냄. 아랫단은 살짝 흐리게 끊음."""
    im = char(name)
    x0, y0, x1, _ = im.getbbox()
    part = im.crop((0, y0, im.width, bottom))
    if fade:
        a = part.getchannel('A')
        px = a.load()
        for y in range(part.height - fade, part.height):
            k = (part.height - y) / fade
            for x in range(part.width):
                px[x, y] = int(px[x, y] * k)
        part.putalpha(a)
    bx = part.getbbox()
    return part.crop((bx[0], 0, bx[2], part.height))


def fit(im, w, h):
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


def sparkle(d, cx, cy, r, col):
    d.polygon([(cx, cy - r), (cx + r * .28, cy - r * .28), (cx + r, cy), (cx + r * .28, cy + r * .28),
               (cx, cy + r), (cx - r * .28, cy + r * .28), (cx - r, cy), (cx - r * .28, cy - r * .28)], fill=col)


def ninepatch(img, sx, sy, pad):
    """sx, sy: 늘어나는 한 줄(x, y). pad: 글자 자리 (왼, 위, 오른, 아래)."""
    w, h = img.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    out.paste(img, (1, 1))
    d = ImageDraw.Draw(out)
    k = (0, 0, 0, 255)
    d.line([(1 + sx, 0), (1 + sx, 0)], fill=k)
    d.line([(0, 1 + sy), (0, 1 + sy)], fill=k)
    l, t, r, b = pad
    d.line([(1 + l, h + 1), (w - r, h + 1)], fill=k)
    d.line([(w + 1, 1 + t), (w + 1, h - b)], fill=k)
    return out


# ---- 말풍선 ----
BODY_H, RAD, LINE = 36, 12, 1.5         # dp
TOP = 35                                # 캐릭터 머리가 올라오는 자리 (dp)
SIDE = 60                               # 캐릭터가 차지하는 쪽의 고정 폭 (dp)
OTHER = 16                              # 반대쪽 고정 폭 (dp)
PEEK_H = 46                             # 말풍선 위로 보이는 캐릭터 전체 높이 (dp)


def body(w, h, fill, top=0):
    """둥근 말풍선 몸통 (SS 배로 그려서 줄임)."""
    S = DP * SS
    big = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([LINE * S / 2, top * S + LINE * S / 2, w * S - LINE * S / 2, h * S - LINE * S / 2],
                        radius=RAD * S, fill=rgb(fill), outline=rgb(NAVY), width=int(LINE * S))
    return big.resize((w * DP, h * DP), Image.LANCZOS)


def paws(img, cx_list, y):
    """말풍선 윗변에 걸친 두 손 (dp 좌표)."""
    S = DP * SS
    big = Image.new('RGBA', (img.width * SS, img.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    for cx in cx_list:
        d.ellipse([(cx - 5) * S, (y - 3.8) * S, (cx + 5) * S, (y + 3.8) * S],
                  fill=rgb(SKIN), outline=rgb(NAVY), width=int(1.2 * S))
        for dx in (-1.6, 1.6):   # 손가락 금
            d.line([((cx + dx) * S, (y + .6) * S), ((cx + dx) * S, (y + 3.0) * S)], fill=rgb(NAVY), width=int(.8 * S))
    img.alpha_composite(big.resize(img.size, Image.LANCZOS))


def glitter(img, pts):
    S = DP * SS
    big = Image.new('RGBA', (img.width * SS, img.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    for (x, y, r) in pts:
        sparkle(d, x * S, y * S, r * S, (255, 255, 255, 230))
    img.alpha_composite(big.resize(img.size, Image.LANCZOS))


def bubble(who, first):
    """who: 'me'(오른쪽, 교복 루카스) / 'you'(왼쪽, 교복 레오). first: 01(묶음 첫 말) 이면 캐릭터를 얹음."""
    fill = ME if who == 'me' else YOU
    w = SIDE + 1 + OTHER if first else 2 * OTHER + 1
    top = TOP if first else 0
    h = top + BODY_H
    img = body(w, h, fill, top)
    if first:
        name = 'lucasSuit' if who == 'me' else 'leoAcad'
        y0 = char(name).getbbox()[1]
        raw = crop_to(name, PEEK[name], 14)
        fig = fit(raw, (SIDE - 4) * DP, PEEK_H * DP)
        chin = (CHIN_PEEK[name] - y0) * fig.height / raw.height / DP     # 그림 안 턱 높이 (dp)
        # 턱이 말풍선 윗변에 오도록 → 얼굴은 다 보이고 몸은 말풍선 뒤에 숨음
        fx = (2 if who == 'you' else w - 2 - fig.width / DP)
        fy = top + 1 - chin
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        layer.alpha_composite(fig, (round(fx * DP), round(fy * DP)))
        cover = body(w, h, fill, top)
        mask = Image.new('L', img.size, 0)
        ImageDraw.Draw(mask).rectangle([0, top * DP, img.width, img.height], fill=255)
        img = Image.alpha_composite(img, layer)
        img.paste(cover, (0, 0), Image.composite(cover.getchannel('A'), Image.new('L', img.size, 0), mask))
        cx = fx + fig.width / DP / 2
        paws(img, (cx - 13, cx + 13), top + 1.2)
        sx = SIDE if who == 'you' else OTHER                       # 늘어나는 세로줄은 캐릭터 반대쪽 칸
        gl = [(w - 9, h - 9, 2.6), (w - 14, h - 6, 1.4)] if who == 'you' else [(8, h - 9, 2.6), (13, h - 6, 1.4)]
    else:
        sx = OTHER
        gl = [(w - 8, h - 9, 2.2)] if who == 'you' else [(8, h - 9, 2.2)]
    glitter(img, gl)
    sy = top + RAD + 2
    pad = (12 * DP, (top + 8) * DP, 12 * DP, 8 * DP)
    return ninepatch(img, sx * DP, sy * DP, pad)


def pressed(nine):
    """누르고 있을 때 말풍선: 살짝 어둡게 (9-patch 테두리 표시는 그대로)."""
    inner = nine.crop((1, 1, nine.width - 1, nine.height - 1))
    r, g, b, a = inner.split()
    dark = Image.merge('RGB', (r, g, b)).point(lambda v: int(v * .88))
    out = nine.copy()
    out.paste(Image.merge('RGBA', (*dark.split(), a)), (1, 1))
    return out


# ---- 아이콘·프로필 ----
def head(name):
    return crop_to(name, CHIN[name], fade=6)


def pixel_art(rows, pal, outline, cell):
    """도트 그림을 cell 배 칸으로 (테두리 한 칸 자동)."""
    w, h = len(rows[0]) + 2, len(rows) + 2
    img = Image.new('RGBA', (w * cell, h * cell), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    on = lambda i, j: 0 <= j < len(rows) and 0 <= i < len(rows[0]) and rows[j][i] in pal
    for j in range(-1, len(rows) + 1):
        for i in range(-1, len(rows[0]) + 1):
            if on(i, j):
                col = pal[rows[j][i]]
            elif outline and (on(i - 1, j) or on(i + 1, j) or on(i, j - 1) or on(i, j + 1)):
                col = outline
            else:
                continue
            d.rectangle([(i + 1) * cell, (j + 1) * cell, (i + 2) * cell - 1, (j + 2) * cell - 1], fill=rgb(col))
    return img.crop(img.getbbox())


def item(name, box):
    if name == 'berry':
        return fit(Image.open(os.path.join(SRC, 'berry.png')).convert('RGBA'), box, box)
    rows, pal, outline = PIX[name]
    cell = max(1, box // (max(len(rows), len(rows[0])) + 2))
    return pixel_art(rows, pal, outline, cell)


def tab_icon(name, focused):
    size = 114
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    h = item(name, 92) if focused else item(name, 74)
    if not focused:   # 고르지 않은 탭: 살짝 작고 흐리게
        r, g, b, a = h.split()
        h = Image.merge('RGBA', (r, g, b, a.point(lambda v: int(v * .62))))
    else:             # 고른 탭: 분홍 빛
        a = h.getchannel('A').filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(4))
        halo = Image.new('RGBA', h.size, rgb(C['accent']))
        halo.putalpha(a.point(lambda v: int(v * .8)))
        pad = Image.new('RGBA', (h.width + 16, h.height + 16), (0, 0, 0, 0))
        pad.alpha_composite(halo, (8, 8))
        pad = pad.filter(ImageFilter.GaussianBlur(3))
        pad.alpha_composite(h, (8, 8))
        h = pad
    out.alpha_composite(h, ((size - h.width) // 2, (size - h.height) // 2))
    return out


def profile(name, color):
    size = 162
    out = Image.new('RGBA', (size, size), rgb(color))
    d = ImageDraw.Draw(out)
    for (x, y, r) in [(24, 26, 7), (136, 34, 5), (128, 132, 6), (30, 128, 4)]:
        sparkle(d, x, y, r, (255, 255, 255, 200))
    h = fit(head(name), 128, 128)
    out.alpha_composite(h, ((size - h.width) // 2, size - h.height - 8))
    return out


# ---- 배경 ----
def starry(w, h, bare=False):
    """별밤 도트 배경을 칸 그대로 키움. bare: 달·언덕 없이 별 하늘만 (목록용)."""
    src = Image.open(os.path.join(SRC, 'starry90.png')).convert('RGBA')
    if bare:
        src = src.copy()
        d = ImageDraw.Draw(src)
        d.rectangle([52, 8, 82, 36], fill=rgb('#3d3a7a'))      # 달 자리
        for (x, y) in [(70, 4), (12, 18), (40, 30)]:
            d.point((x, y), fill=rgb('#fff6c8'))
    k = max(w / 90, h / 160)
    big = src.resize((round(90 * k), round(160 * k)), Image.NEAREST)
    return big.crop(((big.width - w) // 2, (big.height - h) // 2, (big.width - w) // 2 + w, (big.height - h) // 2 + h))


def splash(w=1080, h=1920):
    img = starry(w, h)
    d = ImageDraw.Draw(img, 'RGBA')
    leo = fit(char('leo').crop(char('leo').getbbox()), 360, 400)
    luc = fit(char('lucasFull').crop(char('lucasFull').getbbox()), 360, 440)
    base = int(h * .58)
    # 발밑 분홍 빛
    glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * .14, base - 40, w * .86, base + 60], fill=rgb(C['accent'], 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    img.alpha_composite(leo, (int(w * .30 - leo.width / 2), base - leo.height))
    img.alpha_composite(luc, (int(w * .70 - luc.width / 2), base - luc.height))
    # 가운데 하트
    hx, hy, s = w // 2, base - 230, 6
    HEART = ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...']
    for j, row in enumerate(HEART):
        for i, ch in enumerate(row):
            if ch == '#':
                d.rectangle([hx + (i - 3.5) * s * 2, hy + j * s * 2, hx + (i - 2.5) * s * 2 - 1, hy + (j + 1) * s * 2 - 1],
                            fill=rgb('#ff8fc8'))
    for (x, y, r) in [(w * .5 - 70, base - 300, 14), (w * .5 + 64, base - 168, 10)]:
        sparkle(d, x, y, r, (255, 246, 200, 240))
    try:
        f = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 40)
    except Exception:
        f = ImageFont.load_default()
    t = 'LUCASGOTCHI'
    tw = d.textlength(t, font=f)
    d.text(((w - tw) / 2, base + 70), t, font=f, fill=rgb('#ffd1ea', 235))
    return img.convert('RGB')


MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<!-- 카카오톡 테마: 코드 없는 리소스 전용 APK. 카카오톡은 com.kakao.talk.theme.* 패키지를 테마로 인식한다. 권한 없음. -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.kakao.talk.theme.{pkg}"
    android:versionCode="{code}"
    android:versionName="{ver}">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="34" />
    <application android:label="@string/app_name" android:hasCode="false" android:allowBackup="false" />
</manifest>
"""


def argb(hexcol, a=None):
    h = hexcol.lstrip('#').upper()
    return '#' + (('%02X' % a) if a is not None else '') + h


def main():
    code = int(os.environ.get('VERSION_CODE', '1'))
    res = os.path.join(OUT, 'res')
    draw = os.path.join(res, 'drawable-xxhdpi')
    vals = os.path.join(res, 'values')
    os.makedirs(draw, exist_ok=True)
    os.makedirs(vals, exist_ok=True)
    for f in os.listdir(draw):
        os.remove(os.path.join(draw, f))

    old = os.path.join(OUT, 'AndroidManifest.xml')   # 예전 방식(리소스만 든 APK)의 매니페스트는 이제 apk/ 쪽에 있음
    if os.path.exists(old):
        os.remove(old)
    with open(os.path.join(vals, 'strings.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
                '    <string name="theme_title">%s</string>\n    <string name="app_name">%s</string>\n</resources>\n' % (TITLE, TITLE))
    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<resources>']
    for name, tok, a in COLORS:
        lines.append('    <color name="%s">%s</color>' % (name, argb(C[tok], a)))
    lines.append('    <color name="theme_chatroom_bubble_me_color">%s</color>' % argb(NAVY))
    lines.append('    <color name="theme_chatroom_bubble_you_color">%s</color>' % argb(NAVY))
    lines.append('</resources>\n')
    with open(os.path.join(vals, 'colors.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    for who in ('me', 'you'):
        for first, no in ((True, '01'), (False, '02')):
            b = bubble(who, first)
            b.save(os.path.join(draw, 'theme_chatroom_bubble_%s_%s_image.9.png' % (who, no)))
            pressed(b).save(os.path.join(draw, 'theme_chatroom_bubble_%s_%s_pressed_image.9.png' % (who, no)))
    for kind, name in TABS.items():
        tab_icon(name, False).save(os.path.join(draw, 'theme_maintab_ico_%s_image.png' % kind))
        tab_icon(name, True).save(os.path.join(draw, 'theme_maintab_ico_%s_focused_image.png' % kind))
    for i, (name, col) in enumerate([('lucas', '#ffc7e4'), ('leo', '#e3d8ff'), ('meck', '#ffe3c2')]):
        profile(name, col).save(os.path.join(draw, 'theme_profile_%02d_image.png' % (i + 1)))
    profile('lucas', '#ffc7e4').save(os.path.join(draw, 'theme_icon.png'))   # 카톡 테마 목록·앱 아이콘
    sel = os.path.join(res, 'drawable')
    os.makedirs(sel, exist_ok=True)
    for tab, img in TAB_SELECTORS.items():
        with open(os.path.join(sel, 'theme_tab_%s_icon.xml' % tab), 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<selector xmlns:android="http://schemas.android.com/apk/res/android">\n'
                    '    <item android:state_selected="true" android:drawable="@drawable/theme_maintab_ico_%s_focused_image" />\n'
                    '    <item android:drawable="@drawable/theme_maintab_ico_%s_image" />\n</selector>\n' % (img, img))
    cdir = os.path.join(res, 'color')
    os.makedirs(cdir, exist_ok=True)
    for k in COLOR_SELECTORS:
        with open(os.path.join(cdir, 'theme_%s_color_selector.xml' % k), 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<selector xmlns:android="http://schemas.android.com/apk/res/android">\n'
                    '    <item android:state_pressed="true" android:color="@color/theme_%s_pressed_color" />\n'
                    '    <item android:color="@color/theme_%s_color" />\n</selector>\n' % (k, k))
    # 공식 샘플의 theme-adv 와 같은 선택기들. 특히 theme_body_cell_color_selector 가 없으면
    # 채팅 목록 칸을 카톡이 기본 흰색으로 칠해 버림.
    adv = {
        'drawable/theme_body_cell_color_selector.xml':   # 앱 minSdk 26 이라 리플 판 하나만
            '<selector xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <item android:drawable="@color/theme_body_cell_pressed_color" android:state_selected="true" />\n'
            '    <item android:drawable="@color/theme_body_cell_pressed_color" android:state_focused="true" />\n'
            '    <item>\n        <ripple android:color="@color/theme_body_cell_pressed_color">\n'
            '            <item android:id="@android:id/mask" android:drawable="@android:color/white" />\n'
            '            <item android:drawable="@color/theme_body_cell_color" />\n        </ripple>\n    </item>\n</selector>\n',
        'drawable/theme_notification_background.xml':
            '<selector xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <item android:state_pressed="true" android:drawable="@color/theme_notification_background_pressed_color" />\n'
            '    <item android:drawable="@color/theme_notification_background_color" />\n</selector>\n',
        'drawable/theme_passcode_keypad_background_color_land.xml':
            '<shape xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <solid android:color="@color/theme_passcode_keypad_background_color" />\n    <corners android:radius="4dp" />\n</shape>\n',
        'drawable/theme_passcode_keypad_pressed_background_color_selector.xml':
            '<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="@color/theme_passcode_keypad_pressed_background_color">\n'
            '    <item android:id="@android:id/mask" android:gravity="center">\n        <shape android:shape="oval">\n'
            '            <solid android:color="@color/theme_passcode_keypad_pressed_background_color" />\n'
            '            <size android:width="58dp" android:height="58dp" />\n        </shape>\n    </item>\n'
            '    <item android:drawable="@android:color/transparent" />\n</ripple>\n',
    }
    for k in ('gift', 'music'):
        adv['color/theme_feature_%s_color_selector.xml' % k] = (
            '<selector xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <item android:state_pressed="true" android:color="@color/theme_feature_primary_pressed_color" />\n'
            '    <item android:color="@color/theme_feature_primary_color" />\n</selector>\n')
    for rel, body_xml in adv.items():
        path = os.path.join(res, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n' + body_xml)
    starry(1080, 1920).convert('RGB').save(os.path.join(draw, 'theme_chatroom_background_image.png'), optimize=True)
    starry(1080, 1920).convert('RGB').save(os.path.join(draw, 'theme_passcode_background_image.png'), optimize=True)
    starry(1080, 1920).convert('RGB').save(os.path.join(draw, 'theme_background_image.png'), optimize=True)   # 목록도 채팅방과 같은 별밤
    splash().save(os.path.join(draw, 'theme_splash_image.png'), optimize=True)
    print('리소스', len(os.listdir(draw)), '장 →', res)

    if '--preview' in sys.argv:
        import preview
        preview.make(OUT, os.path.join(HERE, 'preview.png'))


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    main()
