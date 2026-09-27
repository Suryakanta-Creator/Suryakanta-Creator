import json, os, urllib.request, html
from datetime import datetime, timezone, date, timedelta

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

def graphql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    headers = dict(HEADERS)
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers=headers, method="POST")
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
languages = {}

for repo in owned[:40]:
    try:
        data = get(repo["languages_url"])
        for lang, count in data.items():
            languages[lang] = languages.get(lang, 0) + int(count)
    except Exception:
        pass

top = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
lang_total = sum(v for _, v in top) or 1

query = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""
calendar = {"totalContributions": 0, "weeks": []}
try:
    result = graphql(query, {"login": USER})
    calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
except Exception as e:
    print("GraphQL contribution query failed:", e)

days = []
for week in calendar.get("weeks", []):
    for d in week.get("contributionDays", []):
        days.append((d["date"], int(d["contributionCount"])))
days.sort()

longest = 0
run = 0
for _, count in days:
    if count > 0:
        run += 1
        longest = max(longest, run)
    else:
        run = 0

today = date.today().isoformat()
past = [(d, c) for d, c in days if d <= today]
current = 0
i = len(past) - 1
if i >= 0 and past[i][1] == 0:
    i -= 1
while i >= 0 and past[i][1] > 0:
    current += 1
    i -= 1

palette = ["#00E5FF", "#8B5CF6", "#35F2B1", "#F7C948", "#FF6B9A"]
bars = []
for i, (lang, value) in enumerate(top):
    pct = value / lang_total * 100
    y = 286 + i * 26
    width = max(8, round(pct * 3.9, 1))
    safe = html.escape(lang)
    bars.append(f"""
      <text x="34" y="{y+12}" class="small" fill="#C9D1D9">{safe}</text>
      <rect x="150" y="{y}" width="390" height="12" rx="6" fill="#0B2233"/>
      <rect x="150" y="{y}" width="0" height="12" rx="6" fill="{palette[i]}">
        <animate attributeName="width" from="0" to="{width}" dur="{1.0+i*0.18}s" fill="freeze"/>
      </rect>
      <text x="530" y="{y+11}" text-anchor="end" class="tiny" fill="#8198A8">{pct:.1f}%</text>
    """)

heat = []
weeks = calendar.get("weeks", [])[-53:]
max_count = max([d.get("contributionCount", 0) for w in weeks for d in w.get("contributionDays", [])] or [1])
for wi, week in enumerate(weeks):
    week_days = week.get("contributionDays", [])
    for di, d in enumerate(week_days):
        count = int(d.get("contributionCount", 0))
        if count == 0:
            color = "#0B2233"
        else:
            ratio = count / max_count
            color = "#0D6675" if ratio < .25 else "#00A0B6" if ratio < .5 else "#00C9DF" if ratio < .75 else "#00E5FF"
        x = 608 + wi * 10.5
        y = 286 + di * 17
        delay = (wi * 7 + di) * 0.002
        heat.append(f'<rect x="{x:.1f}" y="{y}" width="8" height="8" rx="2" fill="{color}" opacity=".25"><animate attributeName="opacity" from=".25" to="1" dur=".5s" begin="{delay:.3f}s" fill="freeze"/></rect>')

sync = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
total_contrib = int(calendar.get("totalContributions", 0))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="455" viewBox="0 0 1200 455">
<defs>
  <linearGradient id="bg" x1="0" x2="1"><stop stop-color="#02070D"/><stop offset=".52" stop-color="#071522"/><stop offset="1" stop-color="#02070D"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.head{{font-weight:800;font-size:22px}} .num{{font-weight:800;font-size:32px}}
.label{{font-size:13px}} .small{{font-size:14px}} .tiny{{font-size:11px}}
.pulse{{animation:p 2.4s ease-in-out infinite}} .scan{{animation:s 4s linear infinite}}
@keyframes p{{50%{{opacity:.35}}}} @keyframes s{{from{{transform:translateX(-180px)}}to{{transform:translateX(1380px)}}}}
</style>
<rect width="1200" height="455" rx="24" fill="url(#bg)" stroke="#00E5FF" stroke-opacity=".34"/>
<text x="34" y="48" class="head" fill="#EAFBFF">LIVE_GITHUB // TELEMETRY</text>
<circle cx="376" cy="41" r="6" fill="#00E5FF" class="pulse"/>
<text x="393" y="47" class="label" fill="#62EFFF">AUTO-SYNC ONLINE</text>
<text x="1165" y="47" text-anchor="end" class="tiny" fill="#667D8D">{sync}</text>

<g transform="translate(34 78)">
  <rect width="260" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">PUBLIC REPOS</text>
  <text x="20" y="82" class="num" fill="#00E5FF" filter="url(#glow)">{user.get("public_repos", len(owned))}</text>
</g>
<g transform="translate(310 78)">
  <rect width="260" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">FOLLOWERS</text>
  <text x="20" y="82" class="num" fill="#8B5CF6" filter="url(#glow)">{user.get("followers", 0)}</text>
</g>
<g transform="translate(586 78)">
  <rect width="280" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">YEAR CONTRIBUTIONS</text>
  <text x="20" y="82" class="num" fill="#35F2B1" filter="url(#glow)">{total_contrib}</text>
</g>
<g transform="translate(882 78)">
  <rect width="284" height="112" rx="18" fill="#06131E" stroke="#12384C"/>
  <text x="20" y="34" class="label" fill="#8198A8">CURRENT STREAK</text>
  <text x="20" y="82" class="num" fill="#F7C948" filter="url(#glow)">{current} DAYS</text>
</g>

<text x="34" y="235" class="label" fill="#62EFFF">LANGUAGE SIGNAL</text>
<text x="420" y="235" class="tiny" fill="#667D8D">STARS {stars}  •  LONGEST STREAK {longest} DAYS</text>
{''.join(bars) if bars else '<text x="34" y="300" class="small" fill="#8198A8">Language data will appear after the next sync.</text>'}

<text x="608" y="235" class="label" fill="#62EFFF">CONTRIBUTION HEATMAP</text>
<text x="1165" y="235" text-anchor="end" class="tiny" fill="#667D8D">REAL GITHUB ACTIVITY</text>
{''.join(heat)}
<text x="608" y="429" class="tiny" fill="#667D8D">Less</text>
<rect x="646" y="421" width="9" height="9" rx="2" fill="#0B2233"/>
<rect x="660" y="421" width="9" height="9" rx="2" fill="#0D6675"/>
<rect x="674" y="421" width="9" height="9" rx="2" fill="#00A0B6"/>
<rect x="688" y="421" width="9" height="9" rx="2" fill="#00C9DF"/>
<rect x="702" y="421" width="9" height="9" rx="2" fill="#00E5FF"/>
<text x="718" y="429" class="tiny" fill="#667D8D">More</text>

<rect width="150" height="455" fill="#00E5FF" opacity=".025" class="scan"/>
</svg>'''

os.makedirs("assets", exist_ok=True)
with open("assets/live-stats.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("generated assets/live-stats.svg")
