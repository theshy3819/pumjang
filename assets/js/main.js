(function () {
  'use strict';

  var root = document.documentElement;

  /* ---------- 인트로 ---------- */
  var intro = document.querySelector('.intro');
  if (intro && root.classList.contains('has-intro')) {
    var finish = function () {
      try { sessionStorage.setItem('pumjang-intro', '1'); } catch (e) {}
      if (intro.parentNode) intro.parentNode.removeChild(intro);
      document.removeEventListener('keydown', skip);
    };
    var skip = function () { intro.classList.add('is-skipped'); };
    intro.addEventListener('animationend', function (e) {
      if (e.target === intro) finish();
    });
    intro.addEventListener('click', skip);
    document.addEventListener('keydown', skip);
    // 애니메이션 이벤트가 오지 않는 환경 대비
    setTimeout(finish, 4000);
  } else if (intro) {
    intro.parentNode.removeChild(intro);
  }

  /* ---------- 헤더: 히어로를 지나면 배경 채움 ---------- */
  var header = document.querySelector('[data-header]');
  var hero = document.querySelector('.hero');
  if (header && hero && 'IntersectionObserver' in window) {
    var headerH = header.offsetHeight;
    new IntersectionObserver(function (entries) {
      header.classList.toggle('is-solid', !entries[0].isIntersecting);
    }, { rootMargin: '-' + (headerH + 1) + 'px 0px 0px 0px' }).observe(hero);
  }

  /* ---------- 모바일 내비게이션 ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    var label = toggle.querySelector('.nav-toggle__label');
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
      label.textContent = open ? '메뉴 닫기' : '메뉴 열기';
      document.body.style.overflow = open ? 'hidden' : '';
    };
    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        setOpen(false);
        toggle.focus();
      }
    });
    window.matchMedia('(min-width: 901px)').addEventListener('change', function (mq) {
      if (mq.matches) setOpen(false);
    });
  }

  /* ---------- 메뉴: 이름을 고르면 오른쪽 사진이 바뀜 (데스크톱) ---------- */
  var items = Array.prototype.slice.call(document.querySelectorAll('.menu-item'));
  var stageImgs = Array.prototype.slice.call(document.querySelectorAll('.menu__stage img'));
  var desktop = window.matchMedia('(min-width: 901px)');

  var activate = function (key) {
    items.forEach(function (item) {
      var on = item.getAttribute('data-menu') === key;
      item.classList.toggle('is-active', on);
      item.querySelector('.menu-item__trigger').setAttribute('aria-pressed', String(on));
    });
    stageImgs.forEach(function (img) {
      img.classList.toggle('is-active', img.getAttribute('data-menu') === key);
    });
  };

  items.forEach(function (item) {
    var key = item.getAttribute('data-menu');
    var trigger = item.querySelector('.menu-item__trigger');
    trigger.addEventListener('click', function () { activate(key); });
    trigger.addEventListener('focus', function () { if (desktop.matches) activate(key); });
    trigger.addEventListener('mouseenter', function () { if (desktop.matches) activate(key); });
  });
})();
