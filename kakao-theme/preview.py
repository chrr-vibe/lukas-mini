"""확인용 화면 흉내: 채팅방 · 아래 탭 · 실행화면을 한 장에. 카톡과 똑같지는 않음 (대략 배치)."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'


def load9(path):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    px = im.load()
    sx = [x - 1 for x in range(1, w - 1) if px[x, 0][3] > 0][0]
    sy = [y - 1 for y in range(1, h - 1) if px[0, y][3] > 0][0]
    pl = [x - 1 for x in range(1, w - 1) if px[x, h - 1][3] > 0]
    pt = [y - 1 for y in range(1, h - 1) if px[w - 1, y][3] > 0]
    body = im.crop((1, 1, w - 1, h - 1))
    return body, sx, sy, (pl[0], pt[0], body.width - 1 - pl[-1], body.height - 1 - pt[-1])


def stretch(body, sx, sy, W, H):
    W, H = max(W, body.width), max(H, body.height)
    out = Image.new('RGBA', (W, H))
    xs = [(0, sx, 0, sx), (sx, sx + 1, sx, W - (body.width - sx - 1)), (sx + 1, body.width, W - (body.width - sx - 1), W)]
    ys = [(0, sy, 0, sy), (sy, sy + 1, sy, H - (body.height - sy - 1)), (sy + 1, body.height, H - (body.height - sy - 1), H)]
    for (a0, a1, b0, b1) in xs:
        for (c0, c1, d0, d1) in ys:
            if a1 > a0 and c1 > c0 and b1 > b0 and d1 > d0:
                out.paste(body.crop((a0, c0, a1, c1)).resize((b1 - b0, d1 - d0), Image.NEAREST), (b0, d0))
    return out


def make(out_dir, path):
    d9 = os.path.join(out_dir, 'res', 'drawable-xxhdpi')
    W, H = 1080, 1920
    chat = Image.open(os.path.join(d9, 'theme_chatroom_background_image.png')).convert('RGBA')
    dr = ImageDraw.Draw(chat)
    f = ImageFont.truetype(FONT, 45)
    fs = ImageFont.truetype(FONT, 33)
    msgs = [('you', '루카스, 오늘 기분은 어때.', True), ('you', '함께 나가자.', False),
            ('me', '…나쁘지 않아. 방금 전까지는.', True), ('me', 'ㅋ', False),
            ('you', '사랑하는 자여...', True), ('me', '그 호칭은 좀 그만둬.', True)]
    prof = Image.open(os.path.join(d9, 'theme_profile_02_image.png')).convert('RGBA').resize((120, 120))
    pm = Image.new('L', prof.size, 0)
    ImageDraw.Draw(pm).rounded_rectangle([0, 0, 119, 119], radius=46, fill=255)
    y = 230
    for who, text, first in msgs:
        body, sx, sy, (pl, pt, pr, pb) = load9(os.path.join(d9, 'theme_chatroom_bubble_%s_%s_image.9.png' % (who, '01' if first else '02')))
        tw = int(dr.textlength(text, font=f))
        bw, bh = tw + pl + pr, 60 + pt + pb
        b = stretch(body, sx, sy, bw, bh)
        if who == 'you':
            x = 190
            if first:
                chat.paste(prof, (40, y), pm)
                dr.text((x, y - 4), '레오나르드', font=fs, fill=(230, 220, 250))
                y += 50
        else:
            x = W - 40 - b.width
        chat.alpha_composite(b, (x, y))
        dr.text((x + pl, y + pt + 2), text, font=f, fill=(43, 32, 80))
        dr.text((x - 120 if who == 'me' else x + b.width + 14, y + b.height - 44), '오후 1:36', font=fs, fill=(220, 210, 245))
        y += b.height + (18 if not first else 14)
        if who == 'me' and not first or who == 'you' and not first:
            y += 20
    # 아래 탭
    tab = Image.new('RGBA', (W, 200), (47, 45, 99, 255))
    for i, k in enumerate(['friends', 'chats', 'browse', 'shopping', 'more']):
        ic = Image.open(os.path.join(d9, 'theme_maintab_ico_%s%s_image.png' % (k, '_focused' if i == 0 else ''))).convert('RGBA').resize((100, 100))
        tab.alpha_composite(ic, (int(W / 5 * (i + .5) - 50), 50))
    chat.alpha_composite(tab, (0, H - 200))
    sp = Image.open(os.path.join(d9, 'theme_splash_image.png')).convert('RGBA')
    sheet = Image.new('RGBA', (W * 2 + 60, H), (30, 28, 50, 255))
    sheet.alpha_composite(chat, (0, 0))
    sheet.alpha_composite(sp, (W + 60, 0))
    sheet.convert('RGB').resize(((W * 2 + 60) // 2, H // 2), Image.LANCZOS).save(path)
    print('미리보기 →', path)
