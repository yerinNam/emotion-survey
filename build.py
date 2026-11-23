"""stimuli/ 의 PNG 13장과 CSV를 읽어 index.html 과 img/*.webp 를 만듭니다.

이미지는 index.html 에 넣지 않고 img/ 에 고화질 WebP(품질 90, 해상도 그대로)로 따로 저장합니다.
이렇게 하면 index.html 이 작아져 웹(GitHub Pages)에서 첫 화면이 바로 뜨고,
사진은 설문 1단계를 하는 동안 미리 받아 둡니다.
사용법:  pip install pillow  →  python build.py
"""
import csv, glob, json, os, re
from PIL import Image, ImageChops, ImageStat

QUALITY = 90
ROOT = os.path.dirname(os.path.abspath(__file__))
STIM = os.path.join(ROOT, 'stimuli')
OUT_IMG = os.path.join(ROOT, 'img')
os.makedirs(OUT_IMG, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(STIM, '00_감정단어_이미지_일람표.csv'), encoding='utf-8-sig')))
pngs = {int(os.path.basename(p)[:2]): p for p in glob.glob(os.path.join(STIM, '[0-9][0-9]_*.png'))}

items, total = [], 0
for r in rows:
    no, word = int(r['번호']), r['감정단어'].strip()
    p = pngs[no]
    assert re.match(rf'{no:02d}_{word}\.png$', os.path.basename(p)), f'CSV와 파일 이름이 다릅니다: {p} / {word}'
    im = Image.open(p).convert('RGB')
    rel = f'img/img{no:02d}.webp'
    out = os.path.join(ROOT, rel)
    im.save(out, 'WEBP', quality=QUALITY, method=6)
    back = Image.open(out).convert('RGB')
    assert back.size == im.size, f'해상도가 바뀌었습니다: {p}'
    diff = max(ImageStat.Stat(ImageChops.difference(im, back)).mean)   # 채널별 평균 오차(0~255)
    size = os.path.getsize(out); total += size
    print(f'{rel}  {im.size[0]}x{im.size[1]}  {size/1e3:.0f} KB  평균 오차 {diff:.2f}/255')
    items.append({'id': f'img{no:02d}', 'no': no, 'word': word, 'file': os.path.basename(p), 'src': rel})

tpl = open(os.path.join(ROOT, 'src', 'survey_template.html'), encoding='utf-8').read()
out = os.path.join(ROOT, 'index.html')
open(out, 'w', encoding='utf-8').write(tpl.replace('__ITEMS__', json.dumps(items, ensure_ascii=False)))
print(f'이미지 {len(items)}장 ({total/1e6:.1f} MB) → img/,  {out} ({os.path.getsize(out)/1e3:.0f} KB)')
