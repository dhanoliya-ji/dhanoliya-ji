<!-- ═══════════════════════════════════════════════════════════════════════ -->
<!--  Gajendra Dhanoliya · profile README                                    -->
<!--                                                                         -->
<!--  Generated pieces — edit the generator, not the output:                 -->
<!--   · assets/neon-*.svg ........ scripts/gen_neon_assets.py               -->
<!--   · assets/*-3d-*.svg ........ scripts/gen_3d_assets.py                 -->
<!--   · RECENTLY PUSHED block .... scripts/update_readme.py (daily)         -->
<!--   · assets/snake-*.svg ....... .github/workflows/visuals.yml            -->
<!--   · profile-3d-contrib/ ...... .github/workflows/visuals.yml            -->
<!-- ═══════════════════════════════════════════════════════════════════════ -->

<!-- ░░ HERO ░░ the wordmark, filled by a gradient that never stops moving ░░ -->
<p align="center">
  <img width="100%" src="assets/neon-hero-dark.svg#gh-dark-mode-only" alt="Gajendra Dhanoliya — backend, systems, applied AI"/>
  <img width="100%" src="assets/neon-hero-light.svg#gh-light-mode-only" alt="Gajendra Dhanoliya — backend, systems, applied AI"/>
</p>

<!-- ░░ CONTACT, right at the top ░░ -->
<p align="center">
  <a href="https://dhanoliya-ji.github.io"><img src="https://img.shields.io/badge/PORTFOLIO-22d3ee?style=for-the-badge&logo=firefoxbrowser&logoColor=0d1117" alt="Portfolio"/></a>
  <a href="mailto:gajendradhanoliya01@gmail.com"><img src="https://img.shields.io/badge/EMAIL-f472b6?style=for-the-badge&logo=gmail&logoColor=0d1117" alt="Email"/></a>
  <a href="tel:+919109485566"><img src="https://img.shields.io/badge/+91_9109485566-c3f53c?style=for-the-badge&logo=whatsapp&logoColor=0d1117" alt="Phone"/></a>
  <a href="https://www.linkedin.com/in/gajendra-dhanoliya-813345359/"><img src="https://img.shields.io/badge/LINKEDIN-8b5cf6?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
</p>

<p align="center">
  <a href="https://github.com/dhanoliya-ji"><img src="https://img.shields.io/badge/GitHub-0d1117?style=flat-square&logo=github&logoColor=white" alt="GitHub"/></a>
  <a href="https://codeforces.com/profile/G.Dhanoliya"><img src="https://img.shields.io/badge/Codeforces_·_Specialist-0d1117?style=flat-square&logo=codeforces&logoColor=22d3ee" alt="Codeforces"/></a>
  <a href="https://www.codechef.com/users/gajenx7"><img src="https://img.shields.io/badge/CodeChef_·_4★-0d1117?style=flat-square&logo=codechef&logoColor=c3f53c" alt="CodeChef"/></a>
  <a href="https://leetcode.com/u/dhanoliya/"><img src="https://img.shields.io/badge/LeetCode-0d1117?style=flat-square&logo=leetcode&logoColor=f472b6" alt="LeetCode"/></a>
</p>

<p align="center">
  <a href="https://dhanoliya-ji.github.io"><b>dhanoliya-ji.github.io</b></a>
</p>

<!-- ░░ the one line that changes ░░ -->
<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=19&duration=2600&pause=700&color=22D3EE&center=true&vCenter=true&width=680&lines=2026+IIT+Delhi+graduate%2C+B.Tech+Electrical+Engineering;I+build+full-stack+apps+and+applied+AI+systems;Route+optimizers.+RAG+pipelines.+Code+sandboxes.;Open+to+SDE+and+AI%2FML+roles" alt="What I do"/>
</p>

<img src="assets/neon-rule-dark.svg#gh-dark-mode-only" width="100%" alt=""/>
<img src="assets/neon-rule-light.svg#gh-light-mode-only" width="100%" alt=""/>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<h2 align="center">◈ &nbsp; W H A T &nbsp; I &nbsp; B U I L D &nbsp; ◈</h2>

<p align="center">
  <i>I like problems where correctness is measurable rather than a matter of taste.<br/>
  A solver either beats the baseline or it doesn't. A sandbox either contains untrusted<br/>
  code or it doesn't. A retrieval pipeline either cites the right page or it made something up.</i>
</p>

<br/>

<!-- ░░ 01 ░░ -->
<h3>
  <img src="https://img.shields.io/badge/01-22d3ee?style=flat-square&label=&labelColor=22d3ee" alt=""/>
  &nbsp;RouteOS &nbsp;<sub><i>fleet route optimization</i></sub>
</h3>

<table>
<tr><td width="62%" valign="top">

Multi-vehicle logistics optimizer solving the **capacitated VRP with time windows**
in Google OR-Tools. Time windows, service durations and per-vehicle distance caps
are modelled as constraint dimensions with priority-scaled drop penalties.

Live vehicle simulation streams over **WebSockets** with traffic injection, and a
**rolling-horizon re-optimizer** re-solves undelivered stops from a vehicle's current
position. PostGIS proximity queries and Redis-cached analytics sit behind the dashboard.

Runs on AWS EC2 in a VPC public subnet, every service in Docker Compose behind an
auto-renewing TLS reverse proxy, hardened to 3 inbound ports.

</td><td width="38%" valign="top">

**Cut fleet distance**
### `20–35%`
against a greedy nearest-neighbour baseline on identical order sets

`375 km` vs `576 km` on 100 orders, 12 vehicles
<br/>`100%` order assignment on 50–250 order benchmarks

</td></tr>
</table>

<p>
  <a href="https://routeos-frontend.onrender.com"><img src="https://img.shields.io/badge/▶_LIVE_DEMO-22d3ee?style=for-the-badge&logoColor=0d1117" alt="Live demo"/></a>
  <a href="https://github.com/dhanoliya-ji/RouteOS"><img src="https://img.shields.io/badge/SOURCE-0d1117?style=for-the-badge&logo=github" alt="Source"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-1a1f28?style=flat-square&logo=python&logoColor=22d3ee"/>
  <img src="https://img.shields.io/badge/OR--Tools-1a1f28?style=flat-square&logo=google&logoColor=22d3ee"/>
  <img src="https://img.shields.io/badge/FastAPI-1a1f28?style=flat-square&logo=fastapi&logoColor=22d3ee"/>
  <img src="https://img.shields.io/badge/PostGIS-1a1f28?style=flat-square&logo=postgresql&logoColor=22d3ee"/>
  <img src="https://img.shields.io/badge/Redis-1a1f28?style=flat-square&logo=redis&logoColor=22d3ee"/>
  <img src="https://img.shields.io/badge/AWS-1a1f28?style=flat-square&logo=amazonwebservices&logoColor=22d3ee"/>
</p>

<br/>

<!-- ░░ 02 ░░ -->
<h3>
  <img src="https://img.shields.io/badge/02-8b5cf6?style=flat-square&label=&labelColor=8b5cf6" alt=""/>
  &nbsp;DocMinds &nbsp;<sub><i>document intelligence &amp; semantic search</i></sub>
</h3>

<table>
<tr><td width="62%" valign="top">

Multi-tenant **RAG platform** for enterprise documents. The upload service reads
**19 file extensions** through PyMuPDF, python-docx, python-pptx, openpyxl and
BeautifulSoup, opens ZIP archives and reads what is inside them, and routes scanned
PDFs to **Tesseract OCR** when a page has under 100 characters.

Each chunk becomes a **384-dimensional** vector from `all-MiniLM-L6-v2` running on
the server, stored with its page number in PostgreSQL behind a **pgvector HNSW**
index so search stays fast as the corpus grows.

The question is embedded the same way, nearest chunks are found by cosine distance
and dropped below a score floor, then **Llama 3.3 70B on Groq** answers only from
those chunks and shows the page it used.

</td><td width="38%" valign="top">

**Grounded, not guessed**
### `page-level`
citations on every answer

`19` file extensions ingested
<br/>`384-d` local embeddings
<br/>`HNSW` cosine index in pgvector
<br/>Celery workers so uploads never block

</td></tr>
</table>

<p>
  <a href="https://github.com/dhanoliya-ji/DocMinds"><img src="https://img.shields.io/badge/SOURCE-0d1117?style=for-the-badge&logo=github" alt="Source"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-1a1f28?style=flat-square&logo=python&logoColor=8b5cf6"/>
  <img src="https://img.shields.io/badge/FastAPI-1a1f28?style=flat-square&logo=fastapi&logoColor=8b5cf6"/>
  <img src="https://img.shields.io/badge/pgvector-1a1f28?style=flat-square&logo=postgresql&logoColor=8b5cf6"/>
  <img src="https://img.shields.io/badge/Celery-1a1f28?style=flat-square&logo=celery&logoColor=8b5cf6"/>
  <img src="https://img.shields.io/badge/Next.js-1a1f28?style=flat-square&logo=nextdotjs&logoColor=8b5cf6"/>
  <img src="https://img.shields.io/badge/Groq-1a1f28?style=flat-square&logo=lightning&logoColor=8b5cf6"/>
</p>

<br/>

<!-- ░░ 03 ░░ -->
<h3>
  <img src="https://img.shields.io/badge/03-c3f53c?style=flat-square&label=&labelColor=c3f53c" alt=""/>
  &nbsp;Online Coding Judge &nbsp;<sub><i>Crucible</i></sub>
</h3>

<table>
<tr><td width="62%" valign="top">

A full-stack competitive-programming judge. A user writes **Python, C++ or Java** in
a React editor and submits to a FastAPI backend that verifies a **JWT**, loads the
problem limits from PostgreSQL, and queues the code to run.

Untrusted code executes inside a **fresh Docker container** with no network, a
read-only filesystem, a non-root user, **128 MB** memory, **50% CPU** and a **2s**
timeout. Each submission is replayed over sample and hidden tests and comes back as
Accepted, Wrong Answer, Runtime Error or TLE, with the time and memory it used.

**37 REST endpoints** across 7 areas cover auth, problems, test cases, submissions,
contests and dashboards, so an admin can ship a problem with hidden tests while a
user registers for a contest and watches a score-ranked leaderboard update live.

</td><td width="38%" valign="top">

**Contains untrusted code**
### `no network`
read-only FS · non-root · hard CPU, memory and wall-clock caps

`37` REST endpoints
<br/>`3` languages judged
<br/>`88` tests passing in CI

</td></tr>
</table>

<p>
  <a href="https://crucible-web.onrender.com"><img src="https://img.shields.io/badge/▶_LIVE_DEMO-c3f53c?style=for-the-badge&logoColor=0d1117" alt="Live demo"/></a>
  <a href="https://github.com/dhanoliya-ji/ONLINE-CODING-JUDGE"><img src="https://img.shields.io/badge/SOURCE-0d1117?style=for-the-badge&logo=github" alt="Source"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-1a1f28?style=flat-square&logo=python&logoColor=c3f53c"/>
  <img src="https://img.shields.io/badge/FastAPI-1a1f28?style=flat-square&logo=fastapi&logoColor=c3f53c"/>
  <img src="https://img.shields.io/badge/PostgreSQL-1a1f28?style=flat-square&logo=postgresql&logoColor=c3f53c"/>
  <img src="https://img.shields.io/badge/React-1a1f28?style=flat-square&logo=react&logoColor=c3f53c"/>
  <img src="https://img.shields.io/badge/Docker-1a1f28?style=flat-square&logo=docker&logoColor=c3f53c"/>
  <img src="https://img.shields.io/badge/TypeScript-1a1f28?style=flat-square&logo=typescript&logoColor=c3f53c"/>
</p>

<br/>

<!-- ░░ 04 ░░ -->
<h3>
  <img src="https://img.shields.io/badge/04-f472b6?style=flat-square&label=&labelColor=f472b6" alt=""/>
  &nbsp;SentinelGraph &nbsp;<sub><i>graph-based fraud detection</i></sub>
</h3>

<table>
<tr><td width="62%" valign="top">

Fraud is rarely visible in a single row. One account receiving $4,000 is
unremarkable. Ten accounts each sending $4,000 into one account that immediately
wires 95% of it offshore is a mule funnel. None of these are properties of a record.
They are **properties of a shape in the network**, and that is what SentinelGraph
looks for.

Built on **CognoDB** with openCypher over Bolt. The whole application rests on one
question: does money leaving this account eventually come back to it? That has no
fixed answer length, so the ring detector is variable-depth Cypher
(`[:TRANSFERRED*3..5]`) instead of a recursive CTE.

</td><td width="38%" valign="top">

**Shapes, not rows**
### `*3..5`
one line of Cypher replaces a recursive CTE

Mule funnels · laundering rings · fraud farms
<br/>Risk scoring over graph structure

</td></tr>
</table>

<p>
  <a href="https://sentinelgraph.vercel.app"><img src="https://img.shields.io/badge/▶_LIVE_DEMO-f472b6?style=for-the-badge&logoColor=0d1117" alt="Live demo"/></a>
  <a href="https://github.com/dhanoliya-ji/sentinelgraph"><img src="https://img.shields.io/badge/SOURCE-0d1117?style=for-the-badge&logo=github" alt="Source"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-1a1f28?style=flat-square&logo=python&logoColor=f472b6"/>
  <img src="https://img.shields.io/badge/openCypher-1a1f28?style=flat-square&logo=neo4j&logoColor=f472b6"/>
  <img src="https://img.shields.io/badge/CognoDB-1a1f28?style=flat-square&logo=databricks&logoColor=f472b6"/>
  <img src="https://img.shields.io/badge/Vercel-1a1f28?style=flat-square&logo=vercel&logoColor=f472b6"/>
</p>

<br/>

<!-- ░░ 05 ░░ -->
<h3>
  <img src="https://img.shields.io/badge/05-64748b?style=flat-square&label=&labelColor=64748b" alt=""/>
  &nbsp;HR Cold Email Automation &nbsp;<sub><i>outreach that doesn't look automated</i></sub>
</h3>

Reads recruiter contacts from Excel, analyses the job role to match the right skills
and projects, personalises greeting and location, attaches the résumé, and sends over
Gmail SMTP with anti-spam pacing. Ships a dry-run mode, a self-test mode and an
interactive HTML analytics dashboard.

<p>
  <a href="https://github.com/dhanoliya-ji/hr-cold-email-automation"><img src="https://img.shields.io/badge/SOURCE-0d1117?style=for-the-badge&logo=github" alt="Source"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-1a1f28?style=flat-square&logo=python&logoColor=94a3b8"/>
  <img src="https://img.shields.io/badge/pandas-1a1f28?style=flat-square&logo=pandas&logoColor=94a3b8"/>
  <img src="https://img.shields.io/badge/SMTP-1a1f28?style=flat-square&logo=gmail&logoColor=94a3b8"/>
</p>

<br/>

<!-- ░░ 06 ░░ -->
<h3>
  <img src="https://img.shields.io/badge/06-64748b?style=flat-square&label=&labelColor=64748b" alt=""/>
  &nbsp;Portfolio &nbsp;<sub><i>the site this all links to</i></sub>
</h3>

An interactive 3D portfolio in React 19, Vite and Tailwind, with a react-three-fiber
hero that tracks the cursor, Framer Motion scroll reveals and Lenis inertial
scrolling. Deployed free on GitHub Pages.

<p>
  <a href="https://dhanoliya-ji.github.io"><img src="https://img.shields.io/badge/▶_VISIT-8b5cf6?style=for-the-badge&logoColor=0d1117" alt="Visit"/></a>
  <a href="https://github.com/dhanoliya-ji/dhanoliya-ji.github.io"><img src="https://img.shields.io/badge/SOURCE-0d1117?style=for-the-badge&logo=github" alt="Source"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/React-1a1f28?style=flat-square&logo=react&logoColor=94a3b8"/>
  <img src="https://img.shields.io/badge/Three.js-1a1f28?style=flat-square&logo=threedotjs&logoColor=94a3b8"/>
  <img src="https://img.shields.io/badge/Tailwind-1a1f28?style=flat-square&logo=tailwindcss&logoColor=94a3b8"/>
</p>

<br/>

<img src="assets/neon-rule-dark.svg#gh-dark-mode-only" width="100%" alt=""/>
<img src="assets/neon-rule-light.svg#gh-light-mode-only" width="100%" alt=""/>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<h2 align="center">◈ &nbsp; T H E &nbsp; S T A C K &nbsp; ◈</h2>

<p align="center"><i>Roughly the path a request takes through the things I build.</i></p>

<p align="center">
  <img width="96%" src="assets/neon-pipeline-dark.svg#gh-dark-mode-only" alt="Ingest, embed, index, solve, serve"/>
  <img width="96%" src="assets/neon-pipeline-light.svg#gh-light-mode-only" alt="Ingest, embed, index, solve, serve"/>
</p>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,cpp,typescript,fastapi,react,nextjs,tailwind&theme=dark" alt="Languages and frameworks"/>
  <br/>
  <img src="https://skillicons.dev/icons?i=postgres,redis,docker,aws,linux,git,github,vercel&theme=dark" alt="Data and infrastructure"/>
</p>

<p align="center">
  <sub>
    <b>Backend</b> REST design · WebSockets · async I/O · Celery · auth &amp; multi-tenant access control &nbsp;·&nbsp;
    <b>Data</b> PostgreSQL · PostGIS · pgvector · Redis · GiST &amp; HNSW indexing<br/>
    <b>AI/ML</b> OR-Tools · RAG · sentence-transformers · vector search · Llama 3.3 on Groq · Tesseract OCR · OpenCV &amp; dlib &nbsp;·&nbsp;
    <b>Infra</b> Docker · container sandboxing · EC2 · Nginx &amp; TLS · GitHub Actions
  </sub>
</p>

<br/>

<img src="assets/neon-rule-dark.svg#gh-dark-mode-only" width="100%" alt=""/>
<img src="assets/neon-rule-light.svg#gh-light-mode-only" width="100%" alt=""/>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<h2 align="center">◈ &nbsp; T H E &nbsp; A R E N A &nbsp; ◈</h2>

<p align="center">
  <i>Competitive programming is where the instinct for complexity and edge cases comes from.</i>
</p>

<p align="center">
  <a href="https://codeforces.com/profile/G.Dhanoliya"><img src="https://img.shields.io/badge/Codeforces-Specialist_·_1500%2B-22d3ee?style=for-the-badge&logo=codeforces&logoColor=0d1117" alt="Codeforces"/></a>
  <a href="https://www.codechef.com/users/gajenx7"><img src="https://img.shields.io/badge/CodeChef-4★_·_1800%2B-c3f53c?style=for-the-badge&logo=codechef&logoColor=0d1117" alt="CodeChef"/></a>
  <a href="https://leetcode.com/u/dhanoliya/"><img src="https://img.shields.io/badge/LeetCode-dhanoliya-f472b6?style=for-the-badge&logo=leetcode&logoColor=0d1117" alt="LeetCode"/></a>
  <br/>
  <img src="https://img.shields.io/badge/1000%2B_problems_solved_across_platforms-8b5cf6?style=for-the-badge" alt="1000+ solved"/>
</p>

<p align="center">
  <img height="150" src="https://leetcard.jacoblin.cool/dhanoliya?theme=dark&font=JetBrains%20Mono&ext=heatmap" alt="LeetCode stats"/>
</p>

<br/>

<img src="assets/neon-rule-dark.svg#gh-dark-mode-only" width="100%" alt=""/>
<img src="assets/neon-rule-light.svg#gh-light-mode-only" width="100%" alt=""/>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<h2 align="center">◈ &nbsp; T H E &nbsp; N U M B E R S &nbsp; ◈</h2>

<!-- github-readme-stats.vercel.app is used everywhere but its shared instance
     sits at 503 for long stretches, which leaves four broken images on the
     page. profile-summary-cards and streak-stats.demolab.com both answer. -->
<p align="center">
  <img width="94%" src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=dhanoliya-ji&theme=github_dark#gh-dark-mode-only" alt="Profile summary"/>
  <img width="94%" src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=dhanoliya-ji&theme=github#gh-light-mode-only" alt="Profile summary"/>
</p>

<p align="center">
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=dhanoliya-ji&theme=github_dark#gh-dark-mode-only" alt="Repos per language"/>
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=dhanoliya-ji&theme=github_dark#gh-dark-mode-only" alt="Most committed language"/>
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=dhanoliya-ji&theme=github#gh-light-mode-only" alt="Repos per language"/>
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=dhanoliya-ji&theme=github#gh-light-mode-only" alt="Most committed language"/>
</p>

<p align="center">
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=dhanoliya-ji&theme=github_dark#gh-dark-mode-only" alt="Stats"/>
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=dhanoliya-ji&theme=github_dark&utcOffset=5.5#gh-dark-mode-only" alt="Productive time"/>
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=dhanoliya-ji&theme=github#gh-light-mode-only" alt="Stats"/>
  <img height="175" src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=dhanoliya-ji&theme=github&utcOffset=5.5#gh-light-mode-only" alt="Productive time"/>
</p>

<p align="center">
  <img height="150" src="https://streak-stats.demolab.com?user=dhanoliya-ji&hide_border=true&background=00000000&ring=22d3ee&fire=f472b6&currStreakLabel=22d3ee&sideLabels=94a3b8&dates=64748b#gh-dark-mode-only" alt="Streak"/>
  <img height="150" src="https://streak-stats.demolab.com?user=dhanoliya-ji&hide_border=true&background=00000000&ring=0891b2&fire=db2777&currStreakLabel=0891b2&sideLabels=475569&dates=94a3b8#gh-light-mode-only" alt="Streak"/>
</p>

<!-- ░░ a year of commits, chewed through by a snake ░░ -->
<p align="center">
  <img width="94%" src="assets/snake-dark.svg#gh-dark-mode-only" alt="Snake eating my contribution graph"/>
  <img width="94%" src="assets/snake-light.svg#gh-light-mode-only" alt="Snake eating my contribution graph"/>
</p>

<!-- ░░ and the same year, as an isometric city ░░ -->
<p align="center">
  <img width="92%" src="profile-3d-contrib/profile-night-rainbow.svg#gh-dark-mode-only" alt="3D contribution calendar"/>
  <img width="92%" src="profile-3d-contrib/profile-green-animate.svg#gh-light-mode-only" alt="3D contribution calendar"/>
</p>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<h3 align="center">◈ &nbsp; R E C E N T L Y &nbsp; P U S H E D &nbsp; ◈</h3>

<!-- RECENT-PROJECTS:START -->
<!-- This block is generated. Do not edit by hand. -->
<table align="center">
<tr><th align="left">Project</th><th align="left">What it is</th><th align="left">Stack</th><th align="left">Updated</th></tr>
<tr><td><a href="https://github.com/dhanoliya-ji/dhanoliya-ji.github.io"><b>Dhanoliya Ji.github.io</b></a></td><td>—</td><td><img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logoColor=white" alt="TypeScript"/></td><td><sub>2026-08-30</sub></td></tr>
<tr><td><a href="https://github.com/dhanoliya-ji/DocMinds"><b>Docminds</b></a></td><td>Multi-tenant RAG platform for enterprise documents: ingests 19 file extensions with aut…</td><td><img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logoColor=white" alt="Python"/></td><td><sub>2026-08-30</sub></td></tr>
<tr><td><a href="https://github.com/dhanoliya-ji/RouteOS"><b>RouteOS</b></a> · <a href="https://routeos-frontend.onrender.com">live</a></td><td>Intelligent logistics & fleet optimization platform for multi vehicle route optimizatio…</td><td><img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logoColor=white" alt="Python"/></td><td><sub>2026-08-29</sub></td></tr>
<tr><td><a href="https://github.com/dhanoliya-ji/hr-cold-email-automation"><b>Cold Email Automation</b></a></td><td>Recruiter outreach that personalises per role, sends on a schedule and tracks replies</td><td><img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logoColor=white" alt="Python"/></td><td><sub>2026-08-18</sub></td></tr>
<tr><td><a href="https://github.com/dhanoliya-ji/ONLINE-CODING-JUDGE"><b>Online Coding Judge</b></a> · <a href="https://crucible-web.onrender.com">live</a></td><td>Submit, sandbox, evaluate against test cases, run contests, rank a leaderboard</td><td><img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logoColor=white" alt="Python"/></td><td><sub>2026-08-12</sub></td></tr>
<tr><td><a href="https://github.com/dhanoliya-ji/sentinelgraph"><b>SentinelGraph</b></a> · <a href="https://sentinelgraph.vercel.app">live</a></td><td>Graph-based fraud detection with clickable evidence for every flag</td><td><img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logoColor=white" alt="Python"/></td><td><sub>2026-08-08</sub></td></tr>
</table>
<!-- RECENT-PROJECTS:END -->

<br/>

<details align="center">
<summary><b>↕︎ How this page builds itself</b></summary>
<br/>
<p align="left">

Nothing here is pasted in twice.

| Piece | Where it comes from |
|---|---|
| **Hero, rules and pipeline** | [`scripts/gen_neon_assets.py`](scripts/gen_neon_assets.py). Pure SMIL, no dependencies. GitHub strips `<script>` from markdown and ignores CSS `:hover` in an image, so nothing on a README can react to your cursor. What it *can* do is never stop moving: gradient stop-colours rotate through four accents, a highlight sweeps the letterforms, packets travel down the wire. Both themes are emitted from one definition. |
| **The 3D pieces** | [`scripts/gen_3d_assets.py`](scripts/gen_3d_assets.py) projects real geometry at 25–37 keyframes and bakes the frames into SMIL, so the browser interpolates between projected frames. |
| **RECENTLY PUSHED** | [`scripts/update_readme.py`](scripts/update_readme.py) reads the GitHub API and rewrites only the text between two markers, so the hand-written parts are never touched. Runs daily. |
| **Commit calendar and snake** | [`github-profile-3d-contrib`](https://github.com/yoshi389111/github-profile-3d-contrib) and [`Platane/snk`](https://github.com/Platane/snk), regenerated nightly. |
| **Theme awareness** | Two images per slot, one tagged `#gh-light-mode-only` and one `#gh-dark-mode-only`. GitHub hides whichever doesn't match your theme. |

```bash
python scripts/gen_neon_assets.py   # 6 files: hero, rule, pipeline x light/dark
python scripts/gen_3d_assets.py     # 12 files: 6 pieces x light/dark
```

</p>
</details>

<br/>

<img src="assets/neon-rule-dark.svg#gh-dark-mode-only" width="100%" alt=""/>
<img src="assets/neon-rule-light.svg#gh-light-mode-only" width="100%" alt=""/>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<h2 align="center">◈ &nbsp; L E T ' S &nbsp; T A L K &nbsp; ◈</h2>

<p align="center">
  <i>Open to SDE and AI/ML roles, full-time or internship, in India or internationally,<br/>
  remote or onsite. If you're building something in backend, distributed systems<br/>
  or applied AI, I'd like to hear about it.</i>
</p>

<p align="center">
  <a href="https://dhanoliya-ji.github.io"><img src="https://img.shields.io/badge/PORTFOLIO-22d3ee?style=for-the-badge&logo=firefoxbrowser&logoColor=0d1117" alt="Portfolio"/></a>
  <a href="mailto:gajendradhanoliya01@gmail.com"><img src="https://img.shields.io/badge/EMAIL-f472b6?style=for-the-badge&logo=gmail&logoColor=0d1117" alt="Email"/></a>
  <a href="tel:+919109485566"><img src="https://img.shields.io/badge/+91_9109485566-c3f53c?style=for-the-badge&logo=whatsapp&logoColor=0d1117" alt="Phone"/></a>
  <a href="https://www.linkedin.com/in/gajendra-dhanoliya-813345359/"><img src="https://img.shields.io/badge/LINKEDIN-8b5cf6?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
</p>

<p align="center">
  <sub>
    <a href="https://dhanoliya-ji.github.io">dhanoliya-ji.github.io</a> &nbsp;·&nbsp;
    gajendradhanoliya01@gmail.com &nbsp;·&nbsp;
    +91 9109485566
  </sub>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=dhanoliya-ji&style=flat-square&color=8b5cf6&label=PROFILE+VIEWS" alt="Profile views"/>
</p>
