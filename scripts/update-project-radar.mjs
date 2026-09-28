import fs from "node:fs";

const username = process.env.GITHUB_REPOSITORY_OWNER || "Suryakanta-Creator";
const token = process.env.GITHUB_TOKEN || "";
const profileRepo = username.toLowerCase();

const headers = {
  Accept: "application/vnd.github+json",
  "User-Agent": `${username}-profile-radar`,
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
};

const response = await fetch(
  `https://api.github.com/users/${username}/repos?per_page=100&sort=pushed&type=owner`,
  { headers }
);

if (!response.ok) {
  throw new Error(`GitHub API failed: ${response.status} ${await response.text()}`);
}

const allRepos = await response.json();
const repos = allRepos
  .filter(
    (repo) =>
      !repo.fork &&
      !repo.archived &&
      repo.name.toLowerCase() !== profileRepo
  )
  .sort((a, b) => new Date(b.pushed_at) - new Date(a.pushed_at));

const visible = repos.slice(0, 6);

const escapeXml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");

const shortName = (name, max = 22) =>
  name.length > max ? `${name.slice(0, max - 1)}…` : name;

const points = [
  [425, 88],
  [338, 204],
  [455, 270],
  [690, 82],
  [792, 205],
  [695, 272],
];

const colors = ["#00E5FF", "#8B5CF6", "#35F2B1", "#FF3CAC", "#38BDF8", "#F59E0B"];

const pointMarkup = visible
  .map((repo, index) => {
    const [x, y] = points[index];
    const color = colors[index % colors.length];
    const cls = `p${(index % 3) + 1}`;
    const language = repo.language ? ` • ${escapeXml(repo.language)}` : "";
    return `
<g class="${cls}" style="transform-origin:${x}px ${y}px">
  <circle cx="${x}" cy="${y}" r="17" fill="${color}" opacity=".18"/>
  <circle cx="${x}" cy="${y}" r="6" fill="${color}" filter="url(#gl)"/>
  <text x="${x + 20}" y="${y + 4}" fill="#E6FBFF" font-size="13" font-weight="700">${escapeXml(shortName(repo.name))}</text>
  <text x="${x + 20}" y="${y + 22}" fill="#8198A8" font-size="10">${language ? language.slice(3) : "Repository"}</text>
</g>`;
  })
  .join("");

const polygon =
  visible.length > 1
    ? `<path d="${visible
        .map((_, i) => `${i === 0 ? "M" : "L"}${points[i][0]} ${points[i][1]}`)
        .join(" ")} Z" fill="none" stroke="#00E5FF" stroke-opacity=".24" class="dash"/>`
    : "";

const latest = visible[0];
const latestName = latest ? shortName(latest.name, 20) : "NO PROJECTS";
const latestLang = latest?.language || "—";
const syncDate = new Date().toISOString().slice(0, 16).replace("T", " ");

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="340" viewBox="0 0 1200 340">
<defs>
  <radialGradient id="bg"><stop stop-color="#0A1D2A"/><stop offset="1" stop-color="#02070D"/></radialGradient>
  <filter id="gl"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.sweep{animation:r 5s linear infinite;transform-origin:600px 170px}
.p1{animation:p 2s ease-in-out infinite}.p2{animation:p 2.6s ease-in-out infinite}.p3{animation:p 3.1s ease-in-out infinite}
.dash{stroke-dasharray:8 10;animation:d 14s linear infinite}
.live{animation:blink 1.8s ease-in-out infinite}
@keyframes r{to{transform:rotate(360deg)}}@keyframes p{50%{opacity:.35;transform:scale(.95)}}@keyframes d{to{stroke-dashoffset:-300}}@keyframes blink{50%{opacity:.35}}
</style>

<rect width="1200" height="340" rx="24" fill="url(#bg)" stroke="#00E5FF" stroke-opacity=".28"/>
<text x="34" y="42" fill="#62EFFF" font-size="16" font-weight="700">PROJECT_RADAR // AUTO</text>
<circle cx="220" cy="36" r="5" fill="#35F2B1" class="live"/>
<text x="234" y="42" fill="#35F2B1" font-size="11">LIVE FROM GITHUB</text>

<g opacity=".35">
  <circle cx="600" cy="170" r="55" fill="none" stroke="#17445A"/>
  <circle cx="600" cy="170" r="105" fill="none" stroke="#17445A"/>
  <circle cx="600" cy="170" r="150" fill="none" stroke="#17445A"/>
  <line x1="450" y1="170" x2="750" y2="170" stroke="#17445A"/>
  <line x1="600" y1="20" x2="600" y2="320" stroke="#17445A"/>
</g>

<g class="sweep">
  <path d="M600 170 L600 20 A150 150 0 0 1 706 64 Z" fill="#00E5FF" opacity=".09"/>
  <line x1="600" y1="170" x2="600" y2="20" stroke="#00E5FF" stroke-width="3" opacity=".7" filter="url(#gl)"/>
</g>

${polygon}
${pointMarkup}

<g>
  <text x="900" y="82" fill="#8198A8" font-size="12">LATEST PUSH</text>
  <text x="900" y="108" fill="#35F2B1" font-size="17" font-weight="700">${escapeXml(latestName)}</text>

  <text x="900" y="142" fill="#8198A8" font-size="12">PRIMARY LANGUAGE</text>
  <text x="900" y="168" fill="#00E5FF" font-size="16">${escapeXml(latestLang)}</text>

  <text x="900" y="202" fill="#8198A8" font-size="12">PROJECTS TRACKED</text>
  <text x="900" y="228" fill="#8B5CF6" font-size="16">${repos.length}</text>

  <text x="900" y="262" fill="#8198A8" font-size="12">AUTO REFRESH</text>
  <text x="900" y="288" fill="#FF3CAC" font-size="16">EVERY 30 MIN</text>

  <text x="900" y="316" fill="#5F7482" font-size="10">SYNC ${escapeXml(syncDate)} UTC</text>
</g>
</svg>`;

fs.mkdirSync("assets", { recursive: true });
fs.writeFileSync("assets/project-radar.svg", svg);
console.log(`Project radar generated from ${repos.length} repositories; showing ${visible.length}.`);
