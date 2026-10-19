/* Offline app: the lab pages, their scripts, three.js, and the scene data are cached on first visit and served from
   the cache afterwards, refreshed in the background whenever the network answers. Bump VERSION on release. */
const VERSION = "qll-lab-0.59.0";
const CORE = ["./", "./index.html", "./lab.css", "./scenes.json", "./catalog.json", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png",
  "./link/", "./link/index.html", "./circuits/", "./circuits/index.html", "./channel/", "./channel/index.html", "../js/lab_channel.js", "./outdoor/", "./outdoor/index.html", "../js/lab_outdoor.js", "./frontier/", "./frontier/index.html", "../js/lab_frontier.js", "./messenger/", "./messenger/index.html", "../js/lab_messenger.js", "../space.css", "../js/lab_twin.js", "../js/lab_quantum.js", "../js/lab_ui.js", "../js/nav.js",
  "../js/lab3d.js", "../vendor/three/three.module.js", "../vendor/three/three.core.js", "../vendor/three/addons/controls/OrbitControls.js"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(VERSION).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.open(VERSION).then(async (cache) => {
    const hit = await cache.match(e.request, { ignoreSearch: true });
    const net = fetch(e.request).then((r) => { if (r.ok) cache.put(e.request, r.clone()); return r; }).catch(() => hit);
    return hit || net;
  }));
});
