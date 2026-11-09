import pymupdf, sys
d = pymupdf.open(r'C:\Users\shy38\Desktop\대무품장비클래시\품장\11월29일 이걸로 품장 작업해야댐.ai')
dr = d[0].get_drawings()
def path_d(x):
    out = []; cur = None
    def mv(p):
        nonlocal cur
        if cur is None or abs(cur.x-p.x) > 1e-3 or abs(cur.y-p.y) > 1e-3:
            out.append(f"M{p.x:.2f} {p.y:.2f}")
    for it in x['items']:
        k = it[0]
        if k == 'l':
            mv(it[1]); out.append(f"L{it[2].x:.2f} {it[2].y:.2f}"); cur = it[2]
        elif k == 'c':
            mv(it[1]); out.append(f"C{it[2].x:.2f} {it[2].y:.2f} {it[3].x:.2f} {it[3].y:.2f} {it[4].x:.2f} {it[4].y:.2f}"); cur = it[4]
        elif k == 're':
            r = it[1]; out.append(f"M{r.x0:.2f} {r.y0:.2f}H{r.x1:.2f}V{r.y1:.2f}H{r.x0:.2f}Z"); cur = None
        elif k == 'qu':
            q = it[1]; out.append(f"M{q.ul.x:.2f} {q.ul.y:.2f}L{q.ur.x:.2f} {q.ur.y:.2f}L{q.lr.x:.2f} {q.lr.y:.2f}L{q.ll.x:.2f} {q.ll.y:.2f}Z"); cur = None
    if x.get('closePath'): out.append('Z')
    return ''.join(out)
def hexc(c): return '#%02x%02x%02x' % tuple(round(v*255) for v in c)
def build(sel, fname, recolor=None):
    rect = None; paths = []
    for x in sel:
        rect = pymupdf.Rect(x['rect']) if rect is None else rect | x['rect']
        fc = hexc(x['fill'])
        if recolor: fc = recolor(x['fill'])
        rule = ' fill-rule="evenodd"' if x.get('even_odd') else ''
        op = x.get('fill_opacity', 1) or 1
        opa = f' fill-opacity="{op:.3f}"' if op < 0.999 else ''
        paths.append(f'<path d="{path_d(x)}" fill="{fc}"{rule}{opa}/>')
    pad = 1
    vb = f"{rect.x0-pad:.2f} {rect.y0-pad:.2f} {rect.width+2*pad:.2f} {rect.height+2*pad:.2f}"
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">' + ''.join(paths) + '</svg>'
    open(fname, 'w', encoding='utf-8').write(svg)
    print(fname, len(sel), 'paths', vb, len(svg)//1024, 'KB')
fills = lambda x: x.get('fill') is not None
# calligraphy: light gray paths above y=440
cal = [x for x in dr if fills(x) and tuple(round(v,3) for v in x['fill']) == (0.827,0.827,0.827) and x['rect'].y1 < 440]
red = [x for x in dr if fills(x) and x['fill'][0] > 0.5 and x['fill'][1] < 0.35 and x['fill'][2] < 0.35 and x['rect'].y0 > 300 and x['rect'].y1 < 460]
print('cal', len(cal), 'red', len(red), [hexc(x['fill']) for x in red][:5], [ (round(x['rect'].x0),round(x['rect'].y0),round(x['rect'].x1),round(x['rect'].y1)) for x in red][:5])
# white glyph inside seal?
wht = [x for x in dr if fills(x) and min(x['fill']) > 0.95 and x['rect'].y0 > 300 and x['rect'].y1 < 460 and x['rect'].x0 > 150 and x['rect'].x1 < 280]
print('white in seal', len(wht))
# order preserved as in doc
order = {id(x): i for i, x in enumerate(dr)}
wm = sorted(cal + red + wht, key=lambda x: order[id(x)])
build(wm, r'C:\shy\pumjang\assets\logo\pumjang-wordmark.svg', recolor=lambda c: ('currentColor' if tuple(round(v,3) for v in c)==(0.827,0.827,0.827) else hexc(c)))
ens_box = pymupdf.Rect(-20, 915, 70, 1005)
ens = [x for x in dr if fills(x) and ens_box.contains(x['rect'])]
build(ens, r'C:\shy\pumjang\assets\logo\pumjang-enso.svg')
