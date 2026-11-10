"""stimuli/ 의 PNG 13장과 CSV를 읽어 index.html(자체 포함 설문 파일)을 만듭니다.

이미지는 무손실 WebP로 바꿔 넣으며, 원본과 픽셀 단위로 같은지 확인합니다.
사용법:  pip install pillow  →  python build.py
"""
import base64, csv, glob, io, json, os, re
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.abspath(__file__))
STIM = os.path.join(ROOT, 'stimuli')
rows = list(csv.DictReader(open(os.path.join(STIM, '00_감정단어_이미지_일람표.csv'), encoding='utf-8-sig')))
pngs = {int(os.path.basename(p)[:2]): p for p in glob.glob(os.path.join(STIM, '[0-9][0-9]_*.png'))}

items = []
for r in rows:
    no, word = int(r['번호']), r['감정단어'].strip()
    p = pngs[no]
    assert re.match(rf'{no:02d}_{word}\.png$', os.path.basename(p)), f'CSV와 파일 이름이 다릅니다: {p} / {word}'
    im = Image.open(p).convert('RGB')
    buf = io.BytesIO(); im.save(buf, 'WEBP', lossless=True, quality=100, method=6); data = buf.getvalue()
    back = Image.open(io.BytesIO(data)).convert('RGB')
    assert ImageChops.difference(im, back).getbbox() is None, f'무손실 변환 실패: {p}'
    items.append({'id': f'img{no:02d}', 'no': no, 'word': word, 'file': os.path.basename(p),
                  'src': 'data:image/webp;base64,' + base64.b64encode(data).decode()})

tpl = open(os.path.join(ROOT, 'src', 'survey_template.html'), encoding='utf-8').read()
out = os.path.join(ROOT, 'index.html')
open(out, 'w', encoding='utf-8').write(tpl.replace('__ITEMS__', json.dumps(items, ensure_ascii=False)))
print(f'이미지 {len(items)}장 → {out} ({os.path.getsize(out)/1e6:.1f} MB)')
