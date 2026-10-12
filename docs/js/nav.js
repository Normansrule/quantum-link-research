// Site navigation on small screens (audit U02). Below 860 CSS pixels the header has room only for the brand and the
// GitHub link, so this adds a real disclosure button: it reports aria-expanded, opens a list of ordinary links,
// moves focus to the first link, and closes on Escape (returning focus to the button), on a link, or on a click
// outside. Without JavaScript the links simply wrap under the brand (space.css), so nothing becomes unreachable.
(function () {
  document.documentElement.classList.add("js");
  function init() {
    const header = document.querySelector("header.top");
    const nav = header && header.querySelector("nav");
    if (!nav || header.querySelector(".nav-toggle")) return;
    nav.id = nav.id || "site-nav";
    if (!nav.hasAttribute("aria-label")) nav.setAttribute("aria-label", "Site");
    const b = document.createElement("button");
    b.type = "button"; b.className = "nav-toggle";
    b.setAttribute("aria-expanded", "false"); b.setAttribute("aria-controls", nav.id);
    b.innerHTML = '<span aria-hidden="true">☰</span> Menu';
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
