// Cloudflare Pages Function: POST /api/lead → перевірка → повідомлення в Telegram.
// Змінні середовища (Cloudflare → Pages → Settings → Variables):
//   TELEGRAM_BOT_TOKEN — токен бота від @BotFather
//   TELEGRAM_CHAT_ID   — куди слати заявки (ID людини або групи; кілька — через кому)

const APPLIANCES = {
  refrigerator: "🧊 Refrigerator", washer: "🫧 Washer", dryer: "🌀 Dryer", dishwasher: "🍽 Dishwasher",
  microwave: "📡 Microwave", oven: "🔥 Oven", range: "🍳 Range / Stove",
};
const SERVICE_ZIPS = {
  91941: "La Mesa", 91942: "La Mesa", 91943: "La Mesa", 91944: "La Mesa",
  91910: "Chula Vista", 91911: "Chula Vista", 91912: "Chula Vista", 91913: "Chula Vista", 91914: "Chula Vista", 91915: "Chula Vista",
  92040: "Lakeside", 92064: "Poway",
};

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json" } });
const clean = (v, max) => String(v ?? "").replace(/[<>]/g, "").replace(/\s+/g, " ").trim().slice(0, max);
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export function validate(body) {
  const d = {
    appliance: clean(body.appliance, 20),
    brand: clean(body.brand, 40),
    problem: clean(body.problem, 60),
    zip: clean(body.zip, 5),
    address: clean(body.address, 120),
    phone: String(body.phone ?? "").replace(/\D/g, "").replace(/^1(?=\d{10}$)/, ""),
    consent: body.consent === true,
  };
  const errors = {};
  if (!APPLIANCES[d.appliance]) errors.appliance = "Choose an appliance";
  if (d.problem.length < 2) errors.problem = "Describe the problem in a few words";
  if (!/^\d{5}$/.test(d.zip)) errors.zip = "Enter a 5-digit ZIP";
  if (d.address.length < 4) errors.address = "Enter your street address";
  if (!/^[2-9]\d{2}[2-9]\d{6}$/.test(d.phone)) errors.phone = "Enter a 10-digit US phone number";
  if (!d.consent) errors.consent = "Please check the box so the technician can contact you";
  return { d, errors };
}

export function formatLead(d, utm = {}, page = "") {
  const city = SERVICE_ZIPS[d.zip];
  const phone = `(${d.phone.slice(0, 3)}) ${d.phone.slice(3, 6)}-${d.phone.slice(6)}`;
  const src = [utm.utm_source, utm.utm_medium, utm.utm_campaign, utm.utm_term].filter(Boolean).map((x) => clean(x, 60));
  const lines = [
    "🔔 <b>New repair request</b>",
    "",
    `${APPLIANCES[d.appliance]}${d.brand ? " · " + esc(d.brand) : ""}`,
    `⚠️ ${esc(d.problem)}`,
    `📍 ${esc(d.address)}, ${d.zip}${city ? " · " + city : " · ⚠️ outside listed areas"}`,
    `📞 +1 ${phone}`,
  ];
  if (src.length || utm.gclid || utm.fbclid) {
    lines.push("", `📈 ${esc(src.join(" / ") || (utm.gclid ? "google ads" : "facebook"))}${utm.gclid ? " · gclid" : ""}${utm.fbclid ? " · fbclid" : ""}`);
  }
  if (page) {
    try { lines.push(`🌐 Page: ${new URL(page).pathname.slice(1) || "home"}`); } catch { /* ігноруємо */ }
  }
  return lines.join("\n");
}

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: "Bad request" }, 400);
  }
  // Пастка для ботів: приховане поле заповнене або форму «заповнили» швидше ніж за 3 секунди
  if (body.website || (typeof body.elapsed === "number" && body.elapsed < 3)) return json({ ok: true });

  const { d, errors } = validate(body);
  if (Object.keys(errors).length) return json({ ok: false, errors }, 422);

  const text = formatLead(d, body.utm || {}, body.page || "");
  const chats = String(env.TELEGRAM_CHAT_ID || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (!env.TELEGRAM_BOT_TOKEN || !chats.length) return json({ ok: false, error: "Not configured" }, 500);

  const results = await Promise.all(chats.map((chat_id) =>
    fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id, text, parse_mode: "HTML", disable_web_page_preview: true }),
    }).then((r) => r.ok).catch(() => false)));

  // Якщо Telegram недоступний — просимо клієнта подзвонити, а не губимо заявку мовчки
  return results.some(Boolean) ? json({ ok: true }) : json({ ok: false, error: "Delivery failed" }, 502);
}
