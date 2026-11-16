import os, re, json, hashlib, urllib.request

# ---- നിങ്ങൾക്ക് മാറ്റാവുന്നത് ----
KEYWORDS = ["anuv jain"]  # ആർട്ടിസ്റ്റിൻ്റെ പേര് (ചെറിയ അക്ഷരത്തിൽ)
PLACES = ["kochi", "kerala", "cochin", "trivandrum", "thiruvananthapuram",
          "kozhikode", "calicut", "thrissur"]
URLS = [
    "PASTE_LINK_1",
    # "PASTE_LINK_2",
]
# --------------------------------

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
STATE_FILE = "state.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"


def send(msg):
    req = urllib.request.Request(
        WEBHOOK,
        data=json.dumps({"content": msg}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "ConcertAlert/1.0"},
    )
    urllib.request.urlopen(req, timeout=20)


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).lower()


def find_hits(text):
    windows = set()
    for kw in KEYWORDS:
        for m in re.finditer(re.escape(kw), text):
            w = text[max(0, m.start() - 200): m.end() + 200]
            if any(p in w for p in PLACES):
                windows.add(w[:400])
    return sorted(windows)


first_run = not os.path.exists(STATE_FILE)
state = {} if first_run else json.load(open(STATE_FILE))

if first_run:
    send("✅ Concert alert set up ആയി. പുതിയ ഷോ വന്നാൽ ഇവിടെ അറിയിക്കും.")

for url in URLS:
    if url.startswith("PASTE_"):
        continue
    s = state.setdefault(url, {"hash": "", "error": False})
    try:
        hits = find_hits(fetch_text(url))
        s["error"] = False
        if hits:
            h = hashlib.md5("|".join(hits).encode()).hexdigest()
            if h != s["hash"]:
                s["hash"] = h
                send(f"🎟️ പുതിയ അപ്ഡേറ്റ്! Kerala ഷോയെ കുറിച്ച് പേജിൽ കണ്ടു:\n{url}")
    except Exception as e:
        if not s["error"]:
            send(f"⚠️ ഈ പേജ് വായിക്കാൻ പറ്റിയില്ല: {url}\n({type(e).__name__})")
        s["error"] = True

json.dump(state, open(STATE_FILE, "w"), indent=1)
