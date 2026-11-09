# 품장 정적 페이지 생성기: 공통 머리/꼬리 + tools/pages/*.html 본문 → 저장소 루트의 *.html
# 사용법: python tools/build.py
import os, re, io

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # 저장소 루트

ICON = {
    'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>',
    'up': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 20V5M6 11l6-6 6 6"/></svg>',
    'left': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    'right': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
    'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
}

HEAD = '''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{{title}}</title>
  <meta name="description" content="{{desc}}">
  <meta name="theme-color" content="#0E2A31">
  <link rel="icon" href="assets/logo/seal.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{{title}}">
  <meta property="og:description" content="{{desc}}">
  <meta property="og:image" content="assets/og-image.jpg">
  <meta property="og:locale" content="ko_KR">
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hahmlet:wght@300..600&display=swap">
{{preload}}  <link rel="stylesheet" href="assets/css/site.css">
{{jsonld}}</head>
<body class="page-{{key}}">
  <a class="skip-link" href="#main">본문으로 건너뛰기</a>

  <header class="site-header">
    <div class="site-header__inner">
      <a class="site-header__logo" href="index.html" aria-label="품장 홈">
        <img src="assets/logo/pumjang-wordmark-light.svg" alt="품장" width="148" height="100">
      </a>
      <nav class="gnb" id="gnb" aria-label="주요 메뉴">
        <ul class="gnb__list">
          <li class="gnb__item"><a class="gnb__link" href="samwon.html"{{cur_samwon}}>삼원수산</a></li>
          <li class="gnb__item"><a class="gnb__link" href="eel.html"{{cur_eel}}>장어 이야기</a></li>
          <li class="gnb__item">
            <a class="gnb__link" href="naju.html"{{cur_store}}>매장</a>
            <div class="gnb__sub">
              <a href="naju.html"{{cur_naju}}>나주점</a>
              <a href="eulwang.html"{{cur_eulwang}}>을왕리점</a>
            </div>
          </li>
        </ul>
        <a class="gnb__cta" href="reservation.html"{{cur_reservation}}>예약하기</a>
      </nav>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="gnb">
        <span class="sr-only">메뉴 열기</span>
        <span class="nav-toggle__bar" aria-hidden="true"></span>
      </button>
    </div>
  </header>

  <main id="main">
'''

FOOT = '''  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="site-footer__top">
        <div class="site-footer__brand">
          <img src="assets/logo/pumjang-wordmark-light.svg" alt="품장" width="140" height="95" loading="lazy">
          <p>품질 좋은 장어, 품격 있는 장소</p>
        </div>
        <div class="site-footer__cols">
          <div>
            <h2>나주점</h2>
            <p>전남 나주시 노안면 건재로 524-11<br><a href="tel:0613341300">061-334-1300</a></p>
          </div>
          <div>
            <h2>을왕리점</h2>
            <p>인천 중구 용유서로 402-11<br><a href="tel:0327511239">032-751-1239</a></p>
          </div>
          <div>
            <h2>바로가기</h2>
            <ul>
              <li><a href="reservation.html">예약 안내</a></li>
              <li><a href="https://naver.me/5apDLo7h" target="_blank" rel="noopener">네이버 플레이스</a></li>
              <li><a href="https://smartstore.naver.com/samwon1238/" target="_blank" rel="noopener">스마트스토어</a></li>
              <li><a href="https://www.instagram.com/pumjang_eel" target="_blank" rel="noopener">인스타그램</a></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="site-footer__bottom">
        <p>© 2026 품장. 장어 생산 삼원수산</p>
        <p>삼원수산 061-334-0073</p>
      </div>
    </div>
  </footer>

  <button class="to-top" type="button" aria-label="맨 위로">{{icon_up}}</button>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
  <script src="https://unpkg.com/lenis@1.1.13/dist/lenis.min.js" defer></script>
  <script src="assets/js/site.js" defer></script>
</body>
</html>
'''

def build(fname):
    src = io.open(os.path.join(HERE, 'pages', fname), encoding='utf-8').read()
    meta, body = src.split('\n---\n', 1)
    m = dict(l.split(': ', 1) for l in meta.strip().splitlines())
    key = m['key']
    cur = lambda k: ' aria-current="page"' if k == key else ''
    out = HEAD
    for k in ['samwon', 'eel', 'naju', 'eulwang', 'reservation']:
        out = out.replace('{{cur_%s}}' % k, cur(k))
    out = out.replace('{{cur_store}}', ' aria-current="page"' if key in ('naju', 'eulwang') else '')
    out = out.replace('{{title}}', m['title']).replace('{{desc}}', m['desc']).replace('{{key}}', key)
    out = out.replace('{{preload}}', ('  <link rel="preload" as="image" href="%s" fetchpriority="high">\n' % m['preload']) if m.get('preload') else '')
    jsonld = ''
    jl = os.path.join(HERE, 'pages', fname.replace('.html', '.jsonld'))
    if os.path.exists(jl):
        jsonld = '  <script type="application/ld+json">\n' + io.open(jl, encoding='utf-8').read().strip() + '\n  </script>\n'
    out = out.replace('{{jsonld}}', jsonld)
    for k, v in ICON.items():
        body = body.replace('{{icon_%s}}' % k, v)
    out += body.rstrip() + '\n' + FOOT.replace('{{icon_up}}', ICON['up'])
    assert '{{' not in out, (fname, re.findall(r'\{\{\w+\}\}', out))
    io.open(os.path.join(ROOT, fname), 'w', encoding='utf-8', newline='\n').write(out)
    print('built', fname, len(out))

for f in sorted(os.listdir(os.path.join(HERE, 'pages'))):
    if f.endswith('.html'):
        build(f)
