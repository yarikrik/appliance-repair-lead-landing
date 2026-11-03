(function () {
  "use strict";
  const ICON = {
    fridge: '<rect x="11" y="4" width="26" height="40" rx="3"/><path d="M11 18h26M16 10v4M16 23v7"/>',
    washer: '<rect x="9" y="5" width="30" height="38" rx="3"/><circle cx="24" cy="27" r="10"/><path d="M9 13h30M15 9h3"/><path d="M18 28c2.5-2 4 2 6.5 0s4 2 5.5 0"/>',
    dryer: '<rect x="9" y="5" width="30" height="38" rx="3"/><circle cx="24" cy="27" r="10"/><circle cx="24" cy="27" r="5"/><path d="M9 13h30M31 9h3"/>',
    dishwasher: '<rect x="9" y="5" width="30" height="38" rx="3"/><path d="M9 14h30M14 9.5h8M15 22v14M21 22v14M27 22v14M33 22v14M13 36h22"/>',
    microwave: '<rect x="5" y="11" width="38" height="26" rx="3"/><rect x="10" y="16" width="22" height="16" rx="2"/><path d="M37 17v2M37 23v2M37 29v2"/>',
    oven: '<rect x="8" y="5" width="32" height="38" rx="3"/><path d="M8 15h32"/><circle cx="14" cy="10" r="1.6"/><circle cx="20" cy="10" r="1.6"/><circle cx="26" cy="10" r="1.6"/><rect x="13" y="20" width="22" height="16" rx="2"/>',
    range: '<rect x="7" y="9" width="34" height="34" rx="3"/><circle cx="17" cy="19" r="4"/><circle cx="31" cy="19" r="4"/><circle cx="17" cy="32" r="4"/><circle cx="31" cy="32" r="4"/>',
  };
  // Дані (техніка, поломки, ZIP-коди, бренди) генеруються з src/content.py у window.SITE
  const APPLIANCES = window.SITE.appliances;
  const OTHER = "Something else";
  const BRANDS = window.SITE.brands;
  const SERVICE_ZIPS = window.SITE.zips;

  const $ = (id) => document.getElementById(id);
  const form = $("lead"), appSel = $("appliance"), probSel = $("problem"), other = $("problem_other");
  window.dataLayer = window.dataLayer || [];

  APPLIANCES.forEach((a) => appSel.add(new Option(a.label, a.id)));
  BRANDS.forEach((b) => $("brands").append(new Option(b)));
  document.querySelectorAll(".app svg[data-icon]").forEach((el) => { el.innerHTML = ICON[el.dataset.icon]; });

  function onAppliance() {
    const a = APPLIANCES.find((x) => x.id === appSel.value);
    probSel.innerHTML = "";
    if (!a) { probSel.add(new Option("Choose appliance first", "")); probSel.disabled = true; other.classList.remove("on"); return; }
    probSel.add(new Option("Choose the problem", ""));
    a.problems.concat(OTHER).forEach((p) => probSel.add(new Option(p, p)));
    probSel.disabled = false;
    other.classList.remove("on");
    clearErr("appliance");
  }
  appSel.addEventListener("change", onAppliance);
  probSel.addEventListener("change", () => {
    other.classList.toggle("on", probSel.value === OTHER);
    if (probSel.value === OTHER) other.focus();
    clearErr("problem");
  });

  // Сторінки під рекламу (/refrigerator-repair) або ?appliance=washer — техніка вже обрана
  (function preselect() {
    const id = document.body.dataset.appliance || new URLSearchParams(location.search).get("appliance");
    if (APPLIANCES.some((x) => x.id === id)) { appSel.value = id; onAppliance(); }
  })();
  const startedAt = Date.now();

  const zip = $("zip"), note = $("zipNote");
  zip.addEventListener("input", () => {
    zip.value = zip.value.replace(/\D/g, "").slice(0, 5);
    clearErr("zip");
    if (zip.value.length < 5) { note.textContent = ""; note.className = "note"; return; }
    const city = SERVICE_ZIPS[zip.value];
    note.textContent = city ? `✓ We serve ${city}` : "We'll check availability in your area";
    note.className = "note " + (city ? "ok" : "warn");
  });

  const phone = $("phone");
  phone.addEventListener("input", () => {
    let d = phone.value.replace(/\D/g, "");
    if (d.length > 10 && d[0] === "1") d = d.slice(1);
    d = d.slice(0, 10);
    phone.value = d.length < 4 ? (d ? `(${d}` : "") : d.length < 7 ? `(${d.slice(0, 3)}) ${d.slice(3)}` : `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
  });
  form.addEventListener("input", (e) => { e.target.classList.remove("bad"); clearErr(e.target.id === "problem_other" ? "problem" : e.target.id); });

  function clearErr(k) { const el = form.querySelector(`.err[data-for="${k}"]`); if (el) el.textContent = ""; }
  function setErrors(errs) {
    form.querySelectorAll(".err[data-for]").forEach((el) => { el.textContent = errs[el.dataset.for] || ""; });
    Object.keys(errs).forEach((k) => { const el = $(k); if (el) el.classList.add("bad"); });
    const first = Object.keys(errs).find((k) => $(k));
    if (first) $(first).focus();
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const digits = phone.value.replace(/\D/g, "");
    const data = {
      appliance: appSel.value, brand: $("brand").value.trim(),
      problem: probSel.value === OTHER ? other.value.trim() : probSel.value,
      zip: zip.value, address: $("address").value.trim(), phone: digits,
      consent: $("consent").checked, website: form.website.value,
      utm: Object.fromEntries(["utm_source", "utm_medium", "utm_campaign", "utm_term", "gclid", "fbclid"]
        .map((k) => [k, new URLSearchParams(location.search).get(k) || ""])),
      page: location.href.slice(0, 300),
      elapsed: Math.round((Date.now() - startedAt) / 1000),
    };
    const e = {};
    if (!data.appliance) e.appliance = "Choose an appliance";
    if (!data.problem) e.problem = probSel.value === OTHER ? "Describe the problem in a few words" : "Choose the problem";
    if (!/^\d{5}$/.test(data.zip)) e.zip = "Enter a 5-digit ZIP";
    if (data.address.length < 4) e.address = "Enter your street address";
    if (digits.length !== 10 || /^[01]/.test(digits)) e.phone = "Enter a 10-digit US phone number";
    if (!data.consent) e.consent = "Please check the box so the technician can contact you";
    setErrors(e);
    if (Object.keys(e).length) return;
    const btn = $("submitBtn");
    btn.disabled = true; btn.textContent = "Sending…";
    try {
      const r = await fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
      if (!r.ok) {
        const res = await r.json().catch(() => ({}));
        if (res.errors) { setErrors(res.errors); btn.disabled = false; btn.textContent = "Request a technician"; return; }
        throw new Error(r.status);
      }
      window.dataLayer.push({ event: "lead_submitted", appliance: data.appliance, in_area: !!SERVICE_ZIPS[data.zip] });
      // окрема сторінка «Дякуємо» — по ній реклама рахує конверсії
      location.href = "/thank-you?a=" + encodeURIComponent(data.appliance);
    } catch (err) {
      setErrors({ form: "Couldn't send your request. Please try again or call us." });
      btn.disabled = false; btn.textContent = "Request a technician";
    }
  });
})();

// плавна поява блоків при прокрутці
(function () {
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const els = document.querySelectorAll("section.s h2.t, .app, .step, .probs li, .faq details, .areas a");
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("shown"); io.unobserve(en.target); } });
  }, { rootMargin: "0px 0px -40px 0px" });
  els.forEach((el) => {
    const i = [...el.parentElement.children].indexOf(el);
    el.style.animationDelay = Math.min(i, 7) * 60 + "ms";
    el.classList.add("reveal");
    io.observe(el);
  });
})();
// ведмідь стежить за курсором (на телефоні — за полем, яке заповнюють)
(function () {
  const svg = document.querySelector(".card .peek");
  if (!svg || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const head = svg.querySelector(".head"), eyes = svg.querySelectorAll(".look");
  let tx = 0, ty = 0, x = 0, y = 0, raf = 0;
  function aim(px, py) {
    const r = svg.getBoundingClientRect();
    const dx = px - (r.left + r.width / 2), dy = py - (r.top + r.height * 0.67);
    const d = Math.hypot(dx, dy) || 1, k = Math.min(1, d / 260);
    tx = dx / d * k; ty = dy / d * k;
    if (!raf) raf = requestAnimationFrame(step);
  }
  function step() {
    x += (tx - x) * 0.18; y += (ty - y) * 0.18;
    eyes.forEach((g) => g.setAttribute("transform", `translate(${(x * 2.6).toFixed(2)} ${(y * 2.4).toFixed(2)})`));
    head.setAttribute("transform", `rotate(${(x * 5).toFixed(2)} 60 70)`);
    raf = Math.abs(tx - x) + Math.abs(ty - y) > 0.002 ? requestAnimationFrame(step) : 0;
  }
  addEventListener("pointermove", (e) => { if (e.pointerType === "mouse") aim(e.clientX, e.clientY); }, { passive: true });
  document.documentElement.addEventListener("mouseleave", () => { tx = 0; ty = 0; if (!raf) raf = requestAnimationFrame(step); });
  document.addEventListener("focusin", (e) => {
    if (!e.target.closest || !e.target.closest(".card")) return;
    const r = e.target.getBoundingClientRect(); aim(r.left + r.width / 2, r.top + r.height / 2);
  });
})();