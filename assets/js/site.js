/* 품장 — 공통 스크립트
   GSAP·ScrollTrigger·Lenis가 없거나 '모션 줄이기'면 정적인 페이지로 동작합니다. */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasGsap = !!(window.gsap && window.ScrollTrigger);
  var desktopMQ = window.matchMedia('(min-width: 961px)');
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  if (hasGsap) gsap.registerPlugin(ScrollTrigger);

  /* ---------- 부드러운 스크롤 ---------- */
  var lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ duration: 1.15, smoothWheel: true });
    if (hasGsap) {
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    } else {
      var raf = function (t) { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
  }
  var scrollToTarget = function (target) {
    if (lenis) lenis.scrollTo(target, { offset: 0 });
    else if (typeof target === 'number') window.scrollTo({ top: target, behavior: reduce ? 'auto' : 'smooth' });
    else target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
  };
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      if (id.length < 2) return;
      var t = document.querySelector(id);
      if (!t) return;
      e.preventDefault();
      scrollToTarget(t);
    });
  });

  /* ---------- 헤더 ---------- */
  var header = $('.site-header');
  var hero = $('.hero, .sub-hero');
  var toTop = $('.to-top');
  var navOpen = false;
  var lastY = window.scrollY;
  var onScroll = function () {
    var y = window.scrollY;
    var limit = hero ? hero.offsetHeight - header.offsetHeight - 2 : 0;
    header.classList.toggle('is-solid', !hero || y > limit);
    header.classList.toggle('is-hidden', !navOpen && y > lastY && y > window.innerHeight * 0.6);
    if (toTop) toTop.classList.toggle('is-visible', y > window.innerHeight);
    lastY = y;
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener('click', function () { scrollToTarget(0); });

  /* ---------- 모바일 메뉴 ---------- */
  var toggle = $('.nav-toggle');
  var gnb = $('#gnb');
  if (toggle && gnb) {
    var label = $('.sr-only', toggle);
    var setOpen = function (open) {
      navOpen = open;
      toggle.setAttribute('aria-expanded', String(open));
      gnb.classList.toggle('is-open', open);
      if (label) label.textContent = open ? '메뉴 닫기' : '메뉴 열기';
      document.body.style.overflow = open ? 'hidden' : '';
      if (lenis) open ? lenis.stop() : lenis.start();
      header.classList.remove('is-hidden');
    };
    toggle.addEventListener('click', function () { setOpen(!navOpen); });
    gnb.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navOpen) { setOpen(false); toggle.focus(); }
    });
    desktopMQ.addEventListener('change', function (mq) { if (mq.matches && navOpen) setOpen(false); });
  }

  /* ---------- 영상: 화면에 보일 때만 재생 ---------- */
  var autoVideos = $$('video[data-autoplay]');
  if (!reduce && 'IntersectionObserver' in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var v = en.target;
        if (v.closest('.hero__slide')) return; // 히어로 영상은 슬라이드가 관리
        if (en.isIntersecting) { var p = v.play(); if (p) p.catch(function () {}); } else v.pause();
      });
    }, { threshold: 0.15 });
    autoVideos.forEach(function (v) { vio.observe(v); });
  }

  /* ---------- 홈 히어로 슬라이드 ---------- */
  var heroSlider = $('[data-hero-slider]');
  if (heroSlider) {
    var slides = $$('.hero__slide', heroSlider);
    var tabs = $$('.hero__tab', heroSlider);
    var current = -1;
    var timer = null;
    var bars = tabs.map(function (t) { return $('.hero__progress i', t); });

    var durationOf = function (slide) {
      var v = $('video', slide);
      if (v && v.duration && isFinite(v.duration)) return Math.max(v.duration - 0.6, 4);
      return parseFloat(slide.getAttribute('data-duration') || '6');
    };

    var go = function (index) {
      index = (index + slides.length) % slides.length;
      if (index === current) return;
      var prev = slides[current];
      var next = slides[index];
      current = index;
      clearTimeout(timer);

      tabs.forEach(function (t, i) {
        t.classList.toggle('is-active', i === index);
        t.setAttribute('aria-selected', String(i === index));
      });
      slides.forEach(function (s) { s.setAttribute('aria-hidden', String(s !== next)); });

      var media = $('.hero__media img, .hero__media video', next);
      var lines = $$('.line > span', next);
      var video = $('video', next);

      if (prev) {
        var pv = $('video', prev);
        if (hasGsap && !reduce) {
          gsap.to(prev, { opacity: 0, duration: 1.1, ease: 'power2.inOut', onComplete: function () {
            prev.classList.remove('is-active'); gsap.set(prev, { clearProps: 'opacity,visibility' });
            if (pv) { pv.pause(); }
          } });
        } else { prev.classList.remove('is-active'); if (pv) pv.pause(); }
      }

      if (prev) prev.style.zIndex = '1';
      next.style.zIndex = '2';
      next.classList.add('is-active');
      if (video && !reduce) { try { video.currentTime = 0; } catch (e) {} var p = video.play(); if (p) p.catch(function () {}); }

      var start = function () {
        var dur = durationOf(next);
        if (hasGsap && !reduce) {
          gsap.fromTo(next, { opacity: 0 }, { opacity: 1, duration: 1.1, ease: 'power2.inOut' });
          if (media && media.tagName === 'IMG') gsap.fromTo(media, { scale: 1.14 }, { scale: 1, duration: dur + 1.2, ease: 'none' });
          gsap.fromTo(lines, { yPercent: 110 }, { yPercent: 0, duration: 1.3, ease: 'power3.out', stagger: 0.12, delay: 0.25 });
          bars.forEach(function (b, i) { if (!b) return; gsap.killTweensOf(b); gsap.set(b, { scaleX: i < index ? 1 : 0 }); });
          if (bars[index]) gsap.to(bars[index], { scaleX: 1, duration: dur, ease: 'none' });
        }
        if (!reduce) timer = setTimeout(function () { go(current + 1); }, dur * 1000);
      };

      if (video && !(video.duration > 0)) video.addEventListener('loadedmetadata', start, { once: true });
      else start();
    };

    tabs.forEach(function (t, i) { t.addEventListener('click', function () { go(i); }); });
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { clearTimeout(timer); if (hasGsap) gsap.globalTimeline.pause(); }
      else { if (hasGsap) gsap.globalTimeline.resume(); var c = current; current = -1; go(c); }
    });
    go(0);
  }

  /* ---------- 스크롤에 맞춰 사진 바뀌는 영역 ---------- */
  $$('[data-sticky-switch]').forEach(function (block) {
    var items = $$('.switch-item', block);
    var figs = $$('.sticky-switch__media figure', block);
    var set = function (i) {
      items.forEach(function (it, k) { it.classList.toggle('is-active', k === i); });
      figs.forEach(function (f, k) { f.classList.toggle('is-active', k === i); });
    };
    if (!('IntersectionObserver' in window)) { set(0); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) set(items.indexOf(en.target)); });
    }, { rootMargin: '-45% 0px -45% 0px' });
    items.forEach(function (it) { io.observe(it); });
    set(0);
  });

  /* ---------- 갤러리: 끌어서 넘기기 + 버튼 ---------- */
  $$('[data-gallery]').forEach(function (g) {
    var track = $('.gallery__track', g);
    var step = function (dir) {
      var item = $('.gallery__item', track);
      var w = item ? item.getBoundingClientRect().width + 14 : 400;
      track.scrollBy({ left: dir * w, behavior: reduce ? 'auto' : 'smooth' });
    };
    $$('[data-gallery-prev]', g).forEach(function (b) { b.addEventListener('click', function () { step(-1); }); });
    $$('[data-gallery-next]', g).forEach(function (b) { b.addEventListener('click', function () { step(1); }); });
    var down = false, sx = 0, sl = 0, moved = false;
    track.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse') return;
      down = true; moved = false; sx = e.clientX; sl = track.scrollLeft;
      track.classList.add('is-dragging');
    });
    window.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - sx;
      if (Math.abs(dx) > 4) moved = true;
      track.scrollLeft = sl - dx;
    });
    window.addEventListener('pointerup', function () {
      if (!down) return;
      down = false; track.classList.remove('is-dragging');
    });
    track.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);
    // Lenis가 가로 휠을 가로채지 않도록
    track.setAttribute('data-lenis-prevent-wheel', '');
  });

  if (!hasGsap || reduce) return;

  /* ===================== 이하 스크롤 모션 ===================== */

  /* 문장 마스크 등장 */
  $$('[data-reveal]').forEach(function (el) {
    var lines = $$('.line > span', el);
    if (!lines.length) return;
    gsap.fromTo(lines, { yPercent: 110 }, {
      yPercent: 0, duration: 1.15, ease: 'power3.out', stagger: 0.1,
      scrollTrigger: { trigger: el, start: 'top 86%' }
    });
  });

  /* 서브 히어로 첫 등장 */
  var subHero = $('.sub-hero');
  if (subHero) {
    var shMedia = $('.sub-hero__media img, .sub-hero__media video', subHero);
    if (shMedia) gsap.fromTo(shMedia, { scale: 1.12 }, { scale: 1, duration: 2.4, ease: 'power3.out' });
    gsap.fromTo($$('.sub-hero__copy .line > span', subHero), { yPercent: 110 }, { yPercent: 0, duration: 1.2, ease: 'power3.out', stagger: 0.1, delay: 0.2 });
    if (shMedia) gsap.to(shMedia, { yPercent: 10, ease: 'none', scrollTrigger: { trigger: subHero, start: 'top top', end: 'bottom top', scrub: true } });
  }

  /* 그림이 위에서 열리며 등장 */
  $$('[data-clip]').forEach(function (el) {
    var inner = $('img, video', el);
    var tl = gsap.timeline({ scrollTrigger: { trigger: el, start: 'top 82%' } });
    tl.fromTo(el, { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, ease: 'power3.inOut' });
    if (inner) tl.fromTo(inner, { scale: 1.22 }, { scale: 1, duration: 1.8, ease: 'power3.out' }, 0);
  });

  /* 느린 시차 */
  $$('[data-parallax]').forEach(function (el) {
    var inner = $('img, video', el);
    if (!inner) return;
    gsap.fromTo(inner, { yPercent: -7, scale: 1.16 }, {
      yPercent: 7, scale: 1.16, ease: 'none',
      scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true }
    });
  });

  /* 숫자 세기 */
  $$('[data-count]').forEach(function (el) {
    var to = parseFloat(el.getAttribute('data-count'));
    var from = parseFloat(el.getAttribute('data-from') || '0');
    var obj = { v: from };
    el.textContent = String(Math.round(from));
    gsap.to(obj, {
      v: to, duration: 2, ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 88%' },
      onUpdate: function () { el.textContent = String(Math.round(obj.v)); }
    });
  });

  /* 크게 열리는 영상 */
  $$('.expand').forEach(function (sec) {
    var frame = $('.expand__frame', sec);
    var mm = gsap.matchMedia();
    mm.add('(min-width: 961px)', function () {
      gsap.fromTo(frame, { clipPath: 'inset(14% 12% 14% 12% round 6px)' }, {
        clipPath: 'inset(0% 0% 0% 0% round 0px)', ease: 'none',
        scrollTrigger: { trigger: sec, start: 'top top', end: '+=90%', scrub: true, pin: true, anticipatePin: 1 }
      });
    });
  });

  /* 가로 스크롤 단계 (데스크톱) */
  $$('[data-hscroll]').forEach(function (sec) {
    var track = $('.hscroll__track', sec);
    var mm = gsap.matchMedia();
    mm.add('(min-width: 961px)', function () {
      var dist = function () { return Math.max(0, track.scrollWidth - window.innerWidth); };
      gsap.to(track, {
        x: function () { return -dist(); }, ease: 'none',
        scrollTrigger: { trigger: sec, start: 'top top', end: function () { return '+=' + dist(); }, scrub: 1, pin: true, invalidateOnRefresh: true, anticipatePin: 1 }
      });
    });
  });

  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();
