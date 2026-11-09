import sys, struct, os, glob
def boxes(f, start, end):
    pos = start
    while pos < end:
        f.seek(pos); hdr = f.read(8)
        if len(hdr) < 8: break
        size, typ = struct.unpack('>I4s', hdr); hl = 8
        if size == 1: size = struct.unpack('>Q', f.read(8))[0]; hl = 16
        elif size == 0: size = end - pos
        yield typ.decode('latin1'), pos, pos+hl, pos+size
        pos += size
def find(f, start, end, path):
    for typ, p, b, e in boxes(f, start, end):
        if typ == path[0]:
            if len(path) == 1: return (b, e)
            r = find(f, b, e, path[1:])
            if r: return r
    return None
def extract(src, dst):
    size = os.path.getsize(src)
    with open(src, 'rb') as f:
        moov = find(f, 0, size, ['moov'])
        traks = [(b, e) for t, p, b, e in boxes(f, *moov) if t == 'trak']
        b, e = traks[0]
        stbl = find(f, b, e, ['mdia', 'minf', 'stbl'])
        sz = find(f, *stbl, ['stsz']); co = find(f, *stbl, ['co64'])
        f.seek(sz[0] + 4); fixed, cnt = struct.unpack('>II', f.read(8))
        length = fixed if fixed else struct.unpack('>I', f.read(4))[0]
        f.seek(co[0] + 8); off = struct.unpack('>Q', f.read(8))[0]
        f.seek(off); data = f.read(length)
        assert data[:2] == b'\xff\xd8', 'not jpeg'
        open(dst, 'wb').write(data)
src_dir, out_dir = sys.argv[1], sys.argv[2]
for p in sorted(glob.glob(os.path.join(src_dir, '*.CR3'))):
    name = os.path.splitext(os.path.basename(p))[0]
    try:
        extract(p, os.path.join(out_dir, name + '.jpg')); print('ok', name)
    except Exception as ex: print('fail', name, ex)
