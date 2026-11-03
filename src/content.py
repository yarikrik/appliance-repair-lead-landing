"""Весь текст сайту в одному місці. Після змін: python src/build.py → готовий сайт у dist/."""

BRAND = "Polar Fix Appliance Repair"
PHONE_DISPLAY = "(619) 555-0123"        # TODO: номер замовника
PHONE_TEL = "+16195550123"
HOURS = "Mon–Sat · 8am–7pm"              # TODO: години роботи замовника
EMAIL = "hello@example.com"              # TODO: пошта для Privacy Policy
DOMAIN = ""                              # TODO: https://… після покупки домену (для canonical і sitemap)
REGION = "San Diego County"

APPLIANCES = [
    {"id": "refrigerator", "slug": "refrigerator-repair", "label": "Refrigerator", "plural": "refrigerators",
     "icon": "fridge",
     "problems": [("Not cooling", "Warm inside, food spoiling, compressor running non-stop."),
                  ("Freezer not freezing", "Ice cream soft, frost buildup or no cold air in the freezer."),
                  ("Leaking water", "Puddles under the fridge or water inside the fresh-food section."),
                  ("Ice maker not working", "No ice, slow ice production or the dispenser is stuck."),
                  ("Loud noise", "Buzzing, clicking or grinding from the back or the freezer."),
                  ("Not turning on", "No lights, no sound — the fridge looks completely dead.")]},
    {"id": "washer", "slug": "washer-repair", "label": "Washer", "plural": "washers", "icon": "washer",
     "problems": [("Won't drain", "Water stays in the drum after the cycle ends."),
                  ("Won't spin", "Clothes come out soaking wet."),
                  ("Leaking", "Water on the floor during or after a cycle."),
                  ("Won't start", "Lights on but the cycle doesn't begin, or no power at all."),
                  ("Shaking / loud", "Banging, walking across the floor or loud noise during spin."),
                  ("Door won't open", "The door or lid stays locked after the cycle.")]},
    {"id": "dryer", "slug": "dryer-repair", "label": "Dryer", "plural": "dryers", "icon": "dryer",
     "problems": [("Not heating", "The drum turns but clothes stay damp and cold."),
                  ("Won't tumble", "Motor hums but the drum doesn't turn."),
                  ("Takes too long", "Two or three cycles to get a load dry."),
                  ("Won't start", "Nothing happens when you press start."),
                  ("Squeaking / noise", "Squealing, thumping or scraping while running.")]},
    {"id": "dishwasher", "slug": "dishwasher-repair", "label": "Dishwasher", "plural": "dishwashers",
     "icon": "dishwasher",
     "problems": [("Not cleaning", "Dishes come out dirty, cloudy or with food residue."),
                  ("Won't drain", "Standing water at the bottom after the cycle."),
                  ("Leaking", "Water under the dishwasher or around the door."),
                  ("Won't start", "No response from the panel, or the cycle stops midway."),
                  ("Error code", "A code on the display and the dishwasher won't run.")]},
    {"id": "microwave", "slug": "microwave-repair", "label": "Microwave", "plural": "microwaves",
     "icon": "microwave",
     "problems": [("Not heating", "Runs and lights up but food stays cold."),
                  ("Won't turn on", "Dead display, no response to buttons."),
                  ("Sparking", "Sparks or arcing inside — stop using it right away."),
                  ("Turntable not spinning", "The plate doesn't rotate during heating."),
                  ("Buttons not working", "Some or all keypad buttons don't respond.")]},
    {"id": "oven", "slug": "oven-repair", "label": "Oven", "plural": "ovens", "icon": "oven",
     "problems": [("Not heating", "The oven stays cold or never reaches temperature."),
                  ("Temperature is off", "Food burns or stays raw at the usual settings."),
                  ("Door won't close", "Broken hinge or the door doesn't seal."),
                  ("Error code", "A code on the display and the oven won't start."),
                  ("Won't turn on", "No power, no lights, no response.")]},
    {"id": "range", "slug": "stove-repair", "label": "Range / Stove", "plural": "ranges and stoves", "icon": "range",
     "problems": [("Burner won't light", "Gas burner clicks but doesn't ignite."),
                  ("Burner won't heat", "Electric burner or cooktop zone stays cold."),
                  ("Gas smell", "Smell of gas near the stove — turn it off, ventilate and call your gas company first."),
                  ("Igniter clicking", "Constant clicking even when the burner is off."),
                  ("Error code", "Error on the display, the cooktop won't work.")]},
]

CITIES = [
    {"slug": "la-mesa", "name": "La Mesa", "zips": ["91941", "91942", "91943", "91944"]},
    {"slug": "chula-vista", "name": "Chula Vista", "zips": ["91910", "91911", "91912", "91913", "91914", "91915"]},
    {"slug": "lakeside", "name": "Lakeside", "zips": ["92040"]},
    {"slug": "poway", "name": "Poway", "zips": ["92064"]},
]

BRANDS = ["Samsung", "LG", "Whirlpool", "GE", "Frigidaire", "Maytag", "Bosch", "KitchenAid", "Kenmore"]

# FAQ — тільки те, що точно відповідає правді. TODO: замовник має підтвердити кожну відповідь
FAQ_COMMON = [
    ("Is it free to submit a request?",
     "Yes. Submitting a request is free and there's no obligation. A local technician contacts you to discuss "
     "the problem and the visit."),
    ("How quickly will someone contact me?",
     "Requests are sent to local technicians right away. During business hours you'll usually get a call shortly "
     "after submitting."),
    ("Who does the repair?",
     f"{BRAND} is a referral service. Repairs are done by independent local technicians. Before the work starts, "
     "ask the technician about pricing, warranty, license and insurance."),
]


def faq_for_appliance(a: dict) -> list[tuple[str, str]]:
    return [
        (f"What {a['label'].lower()} problems can you help with?",
         "Common issues include: " + ", ".join(p[0].lower() for p in a["problems"]) +
         ". If your problem isn't on the list, choose “Something else” and describe it in a few words."),
        (f"Which {a['label'].lower()} brands do you work with?",
         "All major brands, including " + ", ".join(BRANDS[:7]) + " and more."),
    ] + FAQ_COMMON


def faq_for_city(c: dict) -> list[tuple[str, str]]:
    return [
        (f"Do you serve all of {c['name']}?",
         f"We connect homeowners in {c['name']} (ZIP {', '.join(c['zips'])}) with local technicians. Enter your ZIP "
         "code in the form to check availability."),
        ("What appliances can you help with?",
         "Refrigerators, washers, dryers, dishwashers, microwaves, ovens and ranges/stoves of all major brands."),
    ] + FAQ_COMMON
