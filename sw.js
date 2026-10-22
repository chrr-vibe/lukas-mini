/* LUCASGOTCHI mini service worker
   - 파일을 고쳐서 올릴 때마다 아래 VERSION 숫자를 하나씩 올려 주세요. */
const VERSION = 'v1';
const PREFIX = 'lgmini-';   // 원래 LUCASGOTCHI(같은 github.io 주소)의 캐시와 섞이지 않게 다른 이름
const CACHE = PREFIX + VERSION;
const CORE = [
  './',
  './index.html',
  './sprites.js',
  './backgrounds.js',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './maskable-512.png',
  './apple-touch-icon.png',
  './favicon-64.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith(PREFIX) && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // 페이지·js·아이콘: 네트워크 우선 (새 버전 바로 반영), 오프라인이면 캐시
  if (req.mode === 'navigate' || (url.origin === location.origin && /\.(js|png|webmanifest)$/.test(url.pathname) && !/sw\.js$/.test(url.pathname))) {
    e.respondWith(
      fetch(req.mode === 'navigate' ? req.url : req, { cache: 'no-cache' }).then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req.mode === 'navigate' ? './index.html' : req, copy)); }
        return res;
      }).catch(() => caches.match(req.mode === 'navigate' ? './index.html' : req))
    );
    return;
  }

  // 같은 사이트 다른 파일: 캐시 우선
  if (url.origin === location.origin) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
    return;
  }

  // 외부 파일(픽셀 폰트): 캐시 먼저 보여 주고 뒤에서 갱신
  e.respondWith(caches.open(CACHE).then(c => c.match(req).then(hit => {
    const net = fetch(req).then(res => { if (res && (res.ok || res.type === 'opaque')) c.put(req, res.clone()); return res; }).catch(() => hit);
    return hit || net;
  })));
});
