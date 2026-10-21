// Site navigation on small screens (audit U02). Below 860 CSS pixels the header has room only for the brand and the
// GitHub link, so this adds a real disclosure button: it reports aria-expanded, opens a list of ordinary links,
// moves focus to the first link, and closes on Escape (returning focus to the button), on a link, or on a click
// outside. Without JavaScript the links simply wrap under the brand (space.css), so nothing becomes unreachable.
// It also adds the light/dark switch: the site follows the system setting until the reader picks one, and the choice
// is remembered in this browser only (localStorage, wrapped so a private window simply falls back to the system).
(function () {
  const root = document.documentElement;
  root.classList.add("js");
  const store = { get() { try { return localStorage.getItem("qll-theme"); } catch (e) { return null; } },
                  set(v) { try { localStorage.setItem("qll-theme", v); } catch (e) { /* not remembered */ } } };
  const saved = store.get();
  if (saved === "light" || saved === "dark") root.dataset.theme = saved;
  const dark = () => root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  const SUN = '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.8v2M10 16.2v2M1.8 10h2M16.2 10h2M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M4.2 15.8l1.4-1.4M14.4 5.6l1.4-1.4"/></svg>';
  const MOON = '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M16.5 12.6A7 7 0 0 1 7.4 3.5a7 7 0 1 0 9.1 9.1z"/></svg>';
  function themeButton(header) {
    const t = document.createElement("button");
    t.type = "button"; t.className = "theme-toggle";
    const paint = () => { const d = dark(); t.innerHTML = d ? SUN : MOON; t.setAttribute("aria-label", d ? "Switch to light mode" : "Switch to dark mode"); t.title = t.getAttribute("aria-label"); };
    t.addEventListener("click", () => { const next = dark() ? "light" : "dark"; root.dataset.theme = next; store.set(next); paint(); document.dispatchEvent(new CustomEvent("qll-theme", { detail: next })); });
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", paint);
    paint(); header.appendChild(t);
  }
  function init() {
    const header = document.querySelector("header.top");
    const nav = header && header.querySelector("nav");
    if (!nav || header.querySelector(".nav-toggle")) return;
    themeButton(header);
    nav.id = nav.id || "site-nav";
    if (!nav.hasAttribute("aria-label")) nav.setAttribute("aria-label", "Site");
    const b = document.createElement("button");
    b.type = "button"; b.className = "nav-toggle";
    b.setAttribute("aria-expanded", "false"); b.setAttribute("aria-controls", nav.id);
    b.innerHTML = '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2 4.5h12M2 8h12M2 11.5h12"/></svg><span class="nt-label">Menu</span>';
    header.insertBefore(b, nav);
    const set = (open, focusButton) => {
      nav.classList.toggle("open", open); b.setAttribute("aria-expanded", String(open));
      if (open) { const a = nav.querySelector("a"); if (a) a.focus(); } else if (focusButton) b.focus();
    };
    b.addEventListener("click", () => set(!nav.classList.contains("open"), false));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && nav.classList.contains("open")) set(false, true); });
    nav.addEventListener("click", (e) => { if (e.target.closest("a")) set(false, false); });
    document.addEventListener("click", (e) => { if (nav.classList.contains("open") && !header.contains(e.target)) set(false, false); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
