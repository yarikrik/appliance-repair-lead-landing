"""Збирає статичний сайт з src/ у dist/: головна, 7 сторінок техніки, 4 сторінки міст, службові сторінки.

Запуск: python src/build.py
"""
from __future__ import annotations

import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

import content as C

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
DIST = ROOT / "dist"

BEAR = """<svg class="peek" viewBox="0 0 120 70" aria-hidden="true">
<g class="head">
  <circle cx="26" cy="22" r="13" fill="#fff" stroke="#d6e6ef" stroke-width="2"/><circle cx="94" cy="22" r="13" fill="#fff" stroke="#d6e6ef" stroke-width="2"/>
  <circle cx="26" cy="22" r="5.5" fill="#d4ebf5"/><circle cx="94" cy="22" r="5.5" fill="#d4ebf5"/>
  <ellipse cx="60" cy="66" rx="46" ry="44" fill="#fff" stroke="#d6e6ef" stroke-width="2"/>
  <g class="look"><g class="blink"><circle cx="45" cy="47" r="4.4" fill="#0b2545"/><circle cx="46.3" cy="45.7" r="1.3" fill="#fff"/></g></g>
  <g class="look"><g class="blink"><circle cx="75" cy="47" r="4.4" fill="#0b2545"/><circle cx="76.3" cy="45.7" r="1.3" fill="#fff"/></g></g>
  <ellipse cx="60" cy="63" rx="14" ry="9" fill="#eaf5fa"/>
  <path d="M53.8 57.8c0-2.4 2.8-3.7 6.2-3.7s6.2 1.3 6.2 3.7c0 2.2-3.4 5-6.2 5s-6.2-2.8-6.2-5z" fill="#0b2545"/>
</g>
</svg>"""


def e(s: str) -> str:
    return escape(str(s), quote=False)


def site_json() -> str:
    data = {
        "appliances": [{"id": a["id"], "label": a["label"], "slug": a["slug"],
                        "problems": [p[0] for p in a["problems"]]} for a in C.APPLIANCES],
        "brands": C.BRANDS + ["Electrolux", "Amana", "Sub-Zero", "Thermador", "Viking", "Wolf", "Haier", "Speed Queen"],
        "zips": {z: c["name"] for c in C.CITIES for z in c["zips"]},
    }
    return json.dumps(data, ensure_ascii=False)


def head(title: str, description: str, path: str, noindex: bool = False) -> str:
    canonical = f'<link rel="canonical" href="{C.DOMAIN}{path}">' if C.DOMAIN else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{escape(description)}">
  {canonical}{robots}
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:image" content="/og.png">
  <meta name="theme-color" content="#0b2545">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/style.css">
  <!-- GTM: сюди спеціаліст з реклами вставить код Google Tag Manager -->
</head>"""


HEADER = f"""<header class="top">
  <div class="wrap">
    <a class="logo" href="/"><img src="/icon.svg" alt="" width="44" height="44"><span><b>Polar Fix</b><small>APPLIANCE REPAIR</small></span></a>
    <a class="call" href="tel:{C.PHONE_TEL}">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>
      <span>{C.PHONE_DISPLAY}<small>{C.HOURS}</small></span>
    </a>
  </div>
</header>"""


def footer() -> str:
    apps = "".join(f'<a href="/{a["slug"]}">{e(a["label"])} repair</a>' for a in C.APPLIANCES)
    cities = "".join(f'<a href="/{c["slug"]}">Appliance repair in {e(c["name"])}</a>' for c in C.CITIES)
    return f"""<footer>
  <div class="wrap">
    <div class="fcols">
      <div><a class="logo light" href="/"><img src="/icon.svg" alt="" width="40" height="40"><span><b>Polar Fix</b><small>APPLIANCE REPAIR</small></span></a>
        <p class="fphone"><a href="tel:{C.PHONE_TEL}">{C.PHONE_DISPLAY}</a><br>{C.HOURS}</p></div>
      <div><h4>Services</h4>{apps}</div>
      <div><h4>Areas</h4>{cities}</div>
      <div><h4>Company</h4><a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Service</a></div>
    </div>
    <p class="disc">{C.BRAND} is a free referral service that connects users with local service providers. All contractors are independent and {C.BRAND} does not warrant or guarantee any work performed. It is the responsibility of the homeowner to verify that the hired contractor furnishes the necessary license and insurance required for the work being performed.</p>
    <p class="disc">© {date.today().year} {C.BRAND} · {C.REGION}, CA</p>
  </div>
</footer>"""


def scripts() -> str:
    return f'<script>window.SITE={site_json()};</script>\n<script src="/app.js" defer></script>'


def form_card() -> str:
    raw = (SRC / "body_raw.html").read_text()
    card = raw[raw.index('<div class="card" id="card">'):raw.index('<div class="meta">')]
    card = card.replace('<div class="card" id="card">', f'<div class="card" id="card">\n        {BEAR}', 1)
    return card.rstrip()


def hero(h1: str, sub: str) -> str:
    return f"""<section class="hero">
    <div class="wrap">
      <h1>{h1}</h1>
      <p class="sub">{e(sub)}</p>
      {form_card()}
      <div class="meta"><span>Free request</span><span>No obligation</span><span>Takes under a minute</span></div>
    </div>
  </section>"""


def apps_section(title: str = "We fix all major appliances", current: str = "") -> str:
    tiles = "".join(
        f'<a class="app{" on" if a["id"] == current else ""}" href="/{a["slug"]}"><svg viewBox="0 0 48 48" data-icon="{a["icon"]}"></svg>{e(a["label"])}</a>'
        for a in C.APPLIANCES)
    return f"""<section class="s"><div class="wrap">
      <h2 class="t">{e(title)}</h2><p class="ts">Pick your appliance to see common problems</p>
      <div class="apps">{tiles}</div></div></section>"""


HOW = """<section class="s alt"><div class="wrap">
      <h2 class="t">How it works</h2>
      <p class="ts">Three simple steps — no long forms, no waiting on hold</p>
      <div class="steps">
        <div class="step"><h3>Tell us what's wrong</h3><p>Appliance, brand and the problem in a few words. Takes under a minute.</p></div>
        <div class="step"><h3>Get a call back</h3><p>A local technician calls you to confirm the visit time and answer your questions.</p></div>
        <div class="step"><h3>Get it fixed</h3><p>The technician comes to your home and repairs your appliance on site.</p></div>
      </div></div></section>"""


def areas_brands() -> str:
    areas = "".join(f'<a href="/{c["slug"]}">{e(c["name"])}</a>' for c in C.CITIES)
    brands = "".join(f"<span>{b}</span>" for b in C.BRANDS)
    return f"""<section class="s"><div class="wrap">
      <h2 class="t">Areas we serve</h2><p class="ts">{C.REGION}</p>
      <div class="areas">{areas}</div>
      <h2 class="t" style="margin-top:46px">All major brands</h2><p class="ts">and many more</p>
      <div class="brands">{brands}</div>
      <div class="cta2"><a href="#card">Request a technician</a></div></div></section>"""


def faq(items: list[tuple[str, str]], title: str = "Questions & answers") -> str:
    qa = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    return f"""<section class="s alt"><div class="wrap narrow">
      <h2 class="t">{e(title)}</h2><div class="faq">{qa}</div></div></section>
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>"""


def problems_section(a: dict) -> str:
    items = "".join(f'<li><b>{e(t)}</b><span>{e(d)}</span></li>' for t, d in a["problems"])
    return f"""<section class="s"><div class="wrap narrow">
      <h2 class="t">Common {e(a["label"].lower())} problems</h2>
      <p class="ts">Recognize your issue? Pick it in the form above — the technician will know what to bring.</p>
      <ul class="probs">{items}</ul></div></section>"""


def page(path: str, title: str, desc: str, main: str, appliance: str = "", noindex: bool = False) -> str:
    data = f' data-appliance="{appliance}"' if appliance else ""
    return f"""{head(title, desc, path, noindex)}
<body{data}>
{HEADER}
<main>
  {main}
</main>
{footer()}
{scripts()}
</body>
</html>
"""


def simple(path: str, title: str, body: str, noindex: bool = False) -> str:
    return f"""{head(title + " · " + C.BRAND, title, path, noindex)}
<body>
{HEADER}
<main><section class="s"><div class="wrap narrow prose">{body}</div></section></main>
{footer()}
</body>
</html>
"""


def build() -> list[str]:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    out: dict[str, str] = {}
    cities = ", ".join(c["name"] for c in C.CITIES)

    out["index.html"] = page(
        "/", f"Appliance Repair in San Diego County · {C.BRAND}",
        f"Refrigerator, washer, dryer, dishwasher, microwave, oven and stove repair in {cities}. "
        "Request a local technician in under a minute.",
        hero("Appliance repair in San Diego — request a technician in 60 seconds",
             "Fridge not cooling? Washer won't drain? Tell us what's wrong and a local technician will call you back.")
        + apps_section() + HOW + areas_brands() + faq(FAQ_HOME))

    for a in C.APPLIANCES:
        lbl = a["label"]
        out[f"{a['slug']}.html"] = page(
            f"/{a['slug']}", f"{lbl} Repair in San Diego County · {C.BRAND}",
            f"{lbl} not working? " + ", ".join(p[0] for p in a["problems"][:3]) +
            f" — request a local {lbl.lower()} repair technician in {cities}. Takes under a minute.",
            hero(f"{e(lbl)} repair in San Diego — request a technician in 60 seconds",
                 f"{a['problems'][0][0]}? {a['problems'][1][0]}? Tell us what's wrong and a local technician will call you back.")
            + problems_section(a) + HOW + apps_section("Other appliances we fix", a["id"]) + areas_brands()
            + faq(C.faq_for_appliance(a)),
            appliance=a["id"])

    for c in C.CITIES:
        out[f"{c['slug']}.html"] = page(
            f"/{c['slug']}", f"Appliance Repair in {c['name']}, CA · {C.BRAND}",
            f"Appliance repair in {c['name']}, CA: refrigerators, washers, dryers, dishwashers, microwaves, ovens and "
            "stoves. Request a local technician in under a minute.",
            hero(f"Appliance repair in {e(c['name'])} — request a technician in 60 seconds",
                 f"Serving {c['name']} (ZIP {', '.join(c['zips'])}). Tell us what's wrong and a local technician will call you back.")
            + apps_section() + HOW + areas_brands() + faq(C.faq_for_city(c)))

    out["thank-you.html"] = simple("/thank-you", "Thank you", THANKS, noindex=True)
    out["privacy.html"] = simple("/privacy", "Privacy Policy", PRIVACY)
    out["terms.html"] = simple("/terms", "Terms of Service", TERMS)
    out["404.html"] = simple("/404", "Page not found",
                             '<h1>Page not found</h1><p>The page you are looking for doesn\'t exist.</p>'
                             '<p><a class="btnlink" href="/">Go to the homepage</a></p>', noindex=True)

    for name, html in out.items():
        (DIST / name).write_text(html, encoding="utf-8")
    for f in ("style.css", "app.js", "icon.svg", "og.png", "_headers"):
        if (SRC / f).exists():
            shutil.copy(SRC / f, DIST / f)
    if (SRC / "functions").exists():
        shutil.copytree(SRC / "functions", ROOT / "functions", dirs_exist_ok=True)
    urls = ["/"] + [f"/{a['slug']}" for a in C.APPLIANCES] + [f"/{c['slug']}" for c in C.CITIES] + ["/privacy", "/terms"]
    if C.DOMAIN:
        (DIST / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(f"<url><loc>{C.DOMAIN}{u}</loc></url>" for u in urls) + "</urlset>\n")
        (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {C.DOMAIN}/sitemap.xml\n")
    return sorted(out)


FAQ_HOME = C.FAQ_COMMON + [
    ("Which appliances can you help with?",
     "Refrigerators, washers, dryers, dishwashers, microwaves, ovens and ranges/stoves of all major brands."),
    ("Which areas do you serve?",
     ", ".join(c["name"] for c in C.CITIES) + f" and nearby areas of {C.REGION}. Enter your ZIP code in the form to check."),
]

THANKS = f"""<div class="thanks">
  <div class="ic">✓</div>
  <h1>Thanks! Your request is in.</h1>
  <p>A local technician will call you shortly to confirm the visit time. Keep your phone nearby.</p>
  <p class="muted">Need help right now? Call <a href="tel:{C.PHONE_TEL}"><b>{C.PHONE_DISPLAY}</b></a></p>
  <p><a class="btnlink" href="/">Back to the homepage</a></p>
</div>"""

PRIVACY = f"""<h1>Privacy Policy</h1>
<p class="muted">Last updated: {date.today():%B %d, %Y}</p>
<p>This Privacy Policy explains how {C.BRAND} (“we”, “us”) collects and uses information when you use this website.</p>
<h2>Information we collect</h2>
<p>When you submit a repair request we collect the information you enter: appliance type, brand, a short description of the problem, ZIP code, street address and phone number. We also automatically collect technical information such as your browser type, pages visited and the advertising campaign that brought you to the site (UTM parameters, click identifiers).</p>
<h2>How we use your information</h2>
<ul><li>to pass your request to independent local service providers so they can contact you about the repair;</li>
<li>to contact you by phone or text message about your request, if you gave consent;</li>
<li>to measure and improve our website and advertising.</li></ul>
<h2>Sharing</h2>
<p>We share your request details with independent service providers in our network so they can contact you and perform the service. We use third-party services such as Google Analytics, Google Ads and Meta (Facebook) for analytics and advertising; they may use cookies and similar technologies.</p>
<h2>Calls and text messages</h2>
<p>By checking the consent box you agree to be contacted by phone or SMS about your request. Consent is not a condition of purchase. You can opt out of text messages at any time by replying STOP.</p>
<h2>Your California privacy rights</h2>
<p>If you are a California resident, you have the right to request access to or deletion of your personal information and to opt out of its sale or sharing. To make a request, email us at <a href="mailto:{C.EMAIL}">{C.EMAIL}</a>.</p>
<h2>Data retention and security</h2>
<p>We keep request information only as long as needed for the purposes above and use reasonable measures to protect it.</p>
<h2>Contact</h2>
<p>Questions about this policy: <a href="mailto:{C.EMAIL}">{C.EMAIL}</a>.</p>"""

TERMS = f"""<h1>Terms of Service</h1>
<p class="muted">Last updated: {date.today():%B %d, %Y}</p>
<p>By using this website you agree to these Terms.</p>
<h2>Our service</h2>
<p>{C.BRAND} is a free referral service that connects homeowners with independent local appliance repair providers. We do not perform repairs ourselves.</p>
<h2>Independent providers</h2>
<p>All service providers are independent contractors. We do not warrant or guarantee any work performed. Pricing, scheduling, warranty and the quality of the work are agreed directly between you and the provider. It is your responsibility to verify that the provider has the license and insurance required for the work.</p>
<h2>Your information</h2>
<p>You agree to provide accurate information in your request. How we handle it is described in our <a href="/privacy">Privacy Policy</a>.</p>
<h2>Limitation of liability</h2>
<p>To the fullest extent permitted by law, {C.BRAND} is not liable for any damages arising from services performed by independent providers or from the use of this website.</p>
<h2>Changes</h2>
<p>We may update these Terms from time to time. Continued use of the website means you accept the updated Terms.</p>
<h2>Contact</h2>
<p><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></p>"""


if __name__ == "__main__":
    pages = build()
    print(f"Зібрано {len(pages)} сторінок у {DIST}")
