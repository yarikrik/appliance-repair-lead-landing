// node tests/lead.test.mjs — перевірка функції заявок без Cloudflare (fetch підмінено)
import assert from "node:assert/strict";
import { onRequestPost, validate, formatLead } from "../functions/api/lead.js";

const sent = [];
globalThis.fetch = async (url, opts) => { sent.push({ url, body: JSON.parse(opts.body) }); return { ok: !url.includes("FAIL") }; };
const env = { TELEGRAM_BOT_TOKEN: "123:ABC", TELEGRAM_CHAT_ID: "111, -1002" };
const good = { appliance: "refrigerator", brand: "Samsung", problem: "Not cooling", zip: "91941", address: "8420 Grossmont Blvd",
  phone: "(619) 555-0123", consent: true, website: "", elapsed: 12, utm: { utm_source: "google", utm_medium: "cpc", gclid: "x" },
  page: "https://site.test/refrigerator-repair?utm_source=google" };
const req = (b) => ({ request: new Request("https://x/api/lead", { method: "POST", body: typeof b === "string" ? b : JSON.stringify(b) }), env });

let r = await onRequestPost(req(good));
assert.equal(r.status, 200);
assert.equal(sent.length, 2, "у два чати");
const text = sent[0].body.text;
for (const part of ["Refrigerator · Samsung", "Not cooling", "La Mesa", "+1 (619) 555-0123", "google / cpc", "Page: refrigerator-repair"]) assert.ok(text.includes(part), part);

sent.length = 0;
r = await onRequestPost(req({ ...good, website: "spam" }));            // honeypot
assert.equal(r.status, 200); assert.equal(sent.length, 0);
r = await onRequestPost(req({ ...good, elapsed: 1 }));                 // занадто швидко
assert.equal(sent.length, 0);
r = await onRequestPost(req({ ...good, phone: "555-0123", consent: false, appliance: "car" }));
assert.equal(r.status, 422);
assert.deepEqual(Object.keys((await r.json()).errors).sort(), ["appliance", "consent", "phone"]);
r = await onRequestPost(req("not json")); assert.equal(r.status, 400);
r = await onRequestPost(req({ ...good, zip: "10001" }));
assert.ok(sent.at(-1).body.text.includes("outside listed areas"));
r = await onRequestPost(req({ ...good, address: "<b>1</b> Main <script>" }));
assert.ok(!sent.at(-1).body.text.includes("<script>"), "HTML вирізано");
r = await onRequestPost({ request: req(good).request, env: { ...env, TELEGRAM_BOT_TOKEN: "FAIL" } });
assert.equal(r.status, 502, "Telegram недоступний — помилка, а не тихий успіх");
assert.equal(validate({ ...good, phone: "+1 619 555 0123" }).d.phone, "6195550123");
console.log("OK — усі перевірки пройшли\n\n" + formatLead(validate(good).d, good.utm, good.page));
