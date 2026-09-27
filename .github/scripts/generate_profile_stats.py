import json, os, urllib.request, urllib.parse, html
from datetime import datetime, timezone

USER = os.environ.get("PROFILE_USER", "Suryakanta-Creator")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "suryakanta-profile-stats",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

user = get(f"https://api.github.com/users/{USER}")
repos = []
page = 1
while True:
    batch = get(f"https://api.github.com/users/{USER}/repos?type=owner&sort=updated&per_page=100&page={page}")
    repos.extend(batch)
    if len(batch) < 100:
        break
    page += 1

owned = [r for r in repos if not r.get("fork")]
stars = sum(r.get("stargazers_count", 0) for r in owned)
forks = sum(r.get("forks_count", 0) for r in owned)
languages = {}

for repo in owned[:40]:
    try:
        data = get(repo["languages_url"])
        for lang, count in data.items():
            languages[lang] = languages.get(lang, 0) + int(count)
    except Exception:
        pass

top = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
total = sum(v for _, v in top) or 1
palette = ["#00E5FF", "#8B5CF6", "#35F2B1", "#F7C948", "#FF6B9A"]
bars = []
for i, (lang, value) in enumerate(top):
    pct = value / total * 100
    y = 235 + i * 25
    width = max(8, round(pct * 4.25, 1))
    safe = html.escape(lang)
    bars.append(f'''
      <text x="640" y="{y+12}" class="small" fill="#C9D1D9">{safe}</text>
      <rect x="760" y="{y}" width="425" height="12" rx="6" fill="#0B2233"/>
      <rect x="760" y="{y}" width="0" height="12" rx="6" fill="{palette[i]}">
        <animate attributeName="width" from="0" to="{width}" dur="{1.0+i*0.18}s" fill="freeze"/>
      </rect>
      <text x="1175" y="{y+11}" text-anchor="end" class="tiny" fill="#8198A8">{pct:.1f}%</text>
    ''')

sync = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="390" viewBox="0 0 1200 390">
<defs>
  <linearGradient id="bg" x1="0" x2="1"><stop stop-color="#02070D"/><stop offset=".52" stop-color="#071522"/><stop offset="1" stop-color="#02070D"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .head{{font-weight:800;font-size:22px}} .num{{font-weight:800;font-size:34px}}
  .label{{font-size:13px}} .small{{font-size:14px}} .tiny{{font-size:12px}}
  .pulse{{animation:p 2.4s ease-in-out infinite}} .scan{{animation:s 4s linear infinite}}
  @keyframes p{{50%{{opacity:.35}}}} @keyframes s{{from{{transform:translateX(-180px)}}to{{transform:translateX(1380px)}}}}
</style>
<rect width="1200" height="390" rx="24" fill="url(#bg)" stroke="#00E5FF" stroke-opacity=".34"/>
<text x="34" y="48" class="head" fill="#EAFBFF">LIVE_GITHUB // TELEMETRY</text>
<circle cx="376" cy="41" r="6" fill="#00E5FF" class="pulse"/>
<text x="393" y="47" class="label" fill="#62EFFF">AUTO-SYNC ONLINE</text>
<text x="1165" y="47" text-anchor="end" class="tiny" fill="#667D8D">{sync}</text>

<g transform="translate(34 78)">
  <rect width="252" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">PUBLIC REPOS</text>
  <text x="20" y="82" class="num" fill="#00E5FF" filter="url(#glow)">{user.get("public_repos", len(owned))}</text>
</g>
<g transform="translate(303 78)">
  <rect width="252" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">FOLLOWERS</text>
  <text x="20" y="82" class="num" fill="#8B5CF6" filter="url(#glow)">{user.get("followers", 0)}</text>
</g>
<g transform="translate(572 78)">
  <rect width="252" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">STARS EARNED</text>
  <text x="20" y="82" class="num" fill="#35F2B1" filter="url(#glow)">{stars}</text>
</g>
<g transform="translate(841 78)">
  <rect width="325" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">REPO FORKS</text>
  <text x="20" y="82" class="num" fill="#F7C948" filter="url(#glow)">{forks}</text>
</g>

<text x="34" y="234" class="label" fill="#62EFFF">CURRENT SIGNAL</text>
<text x="34" y="268" class="small" fill="#D8E7F0">Full Stack Development × AI × Real-world Projects</text>
<text x="34" y="303" class="label" fill="#8198A8">BUILDING</text>
<text x="34" y="330" class="small" fill="#00E5FF">KRUSHI SEVA</text>
<text x="34" y="362" class="tiny" fill="#667D8D">Data generated directly from GitHub API — no fake counters.</text>

<text x="640" y="214" class="label" fill="#62EFFF">LANGUAGE SIGNAL</text>
{''.join(bars) if bars else '<text x="640" y="255" class="small" fill="#8198A8">Language data will appear after the next sync.</text>'}

<rect width="150" height="390" fill="#00E5FF" opacity=".025" class="scan"/>
</svg>'''

os.makedirs("assets", exist_ok=True)
with open("assets/live-stats.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("generated assets/live-stats.svg")
