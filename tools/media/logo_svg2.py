import pymupdf, re
exec(open('logo_svg.py', encoding='utf-8').read().split('fills = lambda')[0])  # reuse helpers: d, dr, path_d, hexc, build
fills = lambda x: x.get('fill') is not None
key = lambda x: tuple(round(v,3) for v in x['fill'])
order = {id(x): i for i, x in enumerate(dr)}
def svg(sel, fname, color, prec=1, pad=1):
    rect = None; paths = []
    for x in sorted(sel, key=lambda x: order[id(x)]):
        rect = pymupdf.Rect(x['rect']) if rect is None else rect | x['rect']
        dd = re.sub(r'-?\d+\.\d+', lambda m: (f"{float(m.group()):.{prec}f}").rstrip('0').rstrip('.'), path_d(x))
        rule = ' fill-rule="evenodd"' if x.get('even_odd') else ''
        paths.append(f'<path d="{dd}" fill="{color(x)}"{rule}/>')
    vb = f"{rect.x0-pad:.1f} {rect.y0-pad:.1f} {rect.width+2*pad:.1f} {rect.height+2*pad:.1f}"
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">' + ''.join(paths) + '</svg>'
    open(fname, 'w', encoding='utf-8').write(s); print(fname, len(sel), len(s)//1024, 'KB', vb)
    return s
L = r'C:\shy\pumjang\assets\logo'
cal = [x for x in dr if fills(x) and key(x) == (0.827,0.827,0.827) and x['rect'].y1 < 440]
red = [x for x in dr if fills(x) and x['fill'][0] > 0.5 and x['fill'][1] < 0.35 and x['fill'][2] < 0.35 and x['rect'].y0 > 300 and x['rect'].y1 < 460]
wht = [x for x in dr if fills(x) and min(x['fill']) > 0.95 and x['rect'].y0 > 300 and x['rect'].y1 < 460 and x['rect'].x0 > 150 and x['rect'].x1 < 280]
svg(cal + red + wht, L + r'\pumjang-wordmark.svg', lambda x: 'currentColor' if x in cal else hexc(x['fill']))
svg(red + wht, L + r'\seal.svg', lambda x: hexc(x['fill']), prec=2)
box = pymupdf.Rect(-20, 915, 70, 1005)
ens = [x for x in dr if fills(x) and box.contains(x['rect'])]
han = [x for x in ens if key(x) == (0.059,0.204,0.247)]
ring = [x for x in ens if x not in han]
svg(han, L + r'\pumjang-hanja.svg', lambda x: 'currentColor', prec=2)
# ring: render big raster with alpha, keep same viewBox as full enso so ring+hanja align
rs = svg(ring, 'ring_tmp.svg', lambda x: hexc(x['fill']), prec=2)
full = pymupdf.Rect(-12.44, 922.46, -12.44+69.49, 922.46+75.80)
print('ring bbox vs full enso:', 'ring svg viewbox printed above')
doc = pymupdf.open('ring_tmp.svg'); pg = doc[0]; z = 900 / pg.rect.width
pg.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True).save('ring_tmp.png')
# wordmark ivory raster for OG image
s = open(L + r'\pumjang-wordmark.svg', encoding='utf-8').read().replace('currentColor', '#EAE6DC')
open('wm_ivory.svg', 'w', encoding='utf-8').write(s)
doc = pymupdf.open('wm_ivory.svg'); pg = doc[0]; z = 420 / pg.rect.width
pg.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True).save('wm_ivory.png')
