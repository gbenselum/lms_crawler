# LMS Crawler & Screenshot Automation for Google Antigravity

[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Skill-blue.svg)](https://github.com/gbenselum/lms_crawler)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green.svg)](https://github.com/gbenselum/lms_crawler)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0%20(Native%20Node.js)-brightgreen.svg)](https://github.com/gbenselum/lms_crawler)
[![Browser](https://img.shields.io/badge/Browser-Microsoft%20Edge%20%7C%20Google%20Chrome-orange.svg)](https://github.com/gbenselum/lms_crawler)

An **Antigravity Skill** and cross-platform automation tool designed to authenticate into Learning Management Systems (LMS) like **Moodle**, explore course syllabi, extract activities and participants, and capture high-resolution viewport and full-page screenshots on **Microsoft Windows**, **macOS**, and **Linux**.

> [!TIP]
> 🚀 **¿Buscás el backup descargado y cómo explorarlo?**
> - 🌐 **Demo en vivo (GitHub Pages):** [**https://gbenselum.github.io/lms_crawler/**](https://gbenselum.github.io/lms_crawler/)
> - 📘 **Guía paso a paso:** [**empiece_aqui.md**](./empiece_aqui.md)
> - 💻 **Visor local offline:** Abrí con doble clic [**visor_backup.html**](./visor_backup.html) o [`backup_chamilo/index.html`](./backup_chamilo/index.html)


---

## 🌟 Key Highlights

- 🪟 **Built for Windows First:** Automatically detects **Microsoft Edge** (pre-installed on all Windows 10 & 11 PCs) or **Google Chrome**. No need to download extra browser binaries.
- ⚡ **Zero External Dependencies:** Built entirely on native Node.js (`fetch`, `WebSocket`, `child_process`). No `npm install`, avoiding proxy issues, 403 Forbidden registry blocks, or sandbox restrictions.
- 🤖 **Antigravity Skill Integration:** Enables Antigravity to automatically handle prompts with LMS URLs and credentials, generating formatted visual reports in artifacts.
- 📸 **Comprehensive Captures:** Captures login screens, hero viewports, stitched full-page course outlines, interactive forum/assignment views, participant rosters, gradebooks, and user dashboards.

---

## 🚀 The Prompt: How to Use in Antigravity on Windows

Once installed, simply send a prompt like this to **Antigravity** on your Windows machine:

> *"Could you check this LMS and get me some screenshots? Here are the credentials https://inaconfirmantes.milaulas.com/course/view.php?id=5 usuario: alenieto password: Lte_2026"*

Antigravity will:
1. Detect the LMS inspection task and activate the `lms-crawler` skill.
2. Launch the headless crawler using Edge or Chrome on Windows.
3. Automatically authenticate and navigate the course.
4. Extract syllabus sections, forums, tasks, and participant tables.
5. Capture full-page and viewport screenshots.
6. Present a rich markdown report (`lms_report.md`) with embedded screenshots directly in the IDE.

---

## 📦 How to Install the Skill on Windows

### Option 1: Global Skill (Recommended)
Make the skill accessible from **any** project or workspace on your Windows machine:

1. Clone or copy this repository:
   ```powershell
   git clone https://github.com/gbenselum/lms_crawler.git
   ```

2. Copy the skill folder into your Antigravity global configuration:
   ```powershell
   $target = "$env:USERPROFILE\.gemini\config\skills\lms-crawler"
   New-Item -ItemType Directory -Force -Path $target
   Copy-Item -Recurse -Force ".\lms_crawler\skills\lms-crawler\*" $target
   ```

### Option 2: Workspace Skill (Project Specific)
Add the skill to your current repository:
```text
C:\Users\YourUser\MyProject\
└── .agents\
    └── skills\
        └── lms-crawler\
            ├── SKILL.md
            ├── scripts\
            │   ├── crawl_lms.mjs
            │   ├── run_crawler.ps1
            │   └── run_crawler.cmd
            └── references\
```

---

## 🛠️ Tools Used & Technical Architecture

### 1. Chromium Headless Engine (Microsoft Edge & Google Chrome)
Instead of forcing the user to download a 200MB Chromium bundle (like standard Puppeteer or Playwright installs), this tool leverages the browser already installed on the operating system:
- **On Windows:** Pre-installed **Microsoft Edge** (`msedge.exe`) or **Google Chrome** (`chrome.exe`).
- **Headless mode:** Uses `--headless=new` for pixel-accurate rendering.
- **Data isolation:** Spawns with an ephemeral `--user-data-dir` so active browser sessions are never interrupted.

### 2. Chrome DevTools Protocol (CDP) via Native WebSocket
- Connects directly to Chromium's remote debugging endpoint (`http://127.0.0.1:9222/json/list`).
- Speaks the **Chrome DevTools Protocol (CDP)** over bidirectional WebSockets using Node's built-in `WebSocket` class.
- Uses the `Page`, `Runtime`, and `DOM` domains:
  - `Page.navigate` & `Page.captureScreenshot` (with `captureBeyondViewport: true` for full-page stitching).
  - `Runtime.evaluate` to auto-fill credentials, submit forms, and extract JSON metadata.

### 3. Node.js (v18+) Standard Library
- No external `npm` packages required.
- Uses `node:child_process` for process spawning.
- Native Windows process management via `taskkill /pid ... /T /F` to prevent orphan background processes.

---

## 💻 Standalone CLI Usage (Without Antigravity)

You can also run the crawler directly from PowerShell, Command Prompt, or Bash:

### Windows PowerShell:
```powershell
node .\skills\lms-crawler\scripts\crawl_lms.mjs `
  --url "https://inaconfirmantes.milaulas.com/course/view.php?id=5" `
  --user "alenieto" `
  --pass "Lte_2026" `
  --out ".\output"
```
Or use the PowerShell helper:
```powershell
.\skills\lms-crawler\scripts\run_crawler.ps1 `
  -Url "https://inaconfirmantes.milaulas.com/course/view.php?id=5" `
  -Username "alenieto" `
  -Password "Lte_2026"
```

### Windows Command Prompt (CMD):
```cmd
skills\lms-crawler\scripts\run_crawler.cmd "https://inaconfirmantes.milaulas.com/course/view.php?id=5" "alenieto" "Lte_2026" ".\output"
```

### macOS / Linux:
```bash
node skills/lms-crawler/scripts/crawl_lms.mjs \
  --url "https://inaconfirmantes.milaulas.com/course/view.php?id=5" \
  --user "alenieto" \
  --pass "Lte_2026" \
  --out "./output"
```

---

## 📁 Repository Structure

```text
lms_crawler/
├── README.md                          # Project documentation and guide
├── package.json                       # Project metadata
├── .gitignore                         # Ignored temporary folders
├── skills/
│   └── lms-crawler/
│       ├── SKILL.md                   # Antigravity skill definition & runbook
│       ├── scripts/
│       │   ├── crawl_lms.mjs          # Cross-platform zero-dependency crawler
│       │   ├── run_crawler.ps1        # Windows PowerShell launcher
│       │   └── run_crawler.cmd        # Windows CMD batch launcher
│       ├── references/
│       │   ├── windows_guide.md       # In-depth Windows guide & troubleshooting
│       │   └── tools_used.md          # CDP architecture & technical details
│       └── examples/
│           ├── sample_report.md       # Real report generated from the test run
│           └── screenshots/           # Real high-res screenshots from test run
```

---

## 📄 Output Artifacts

Running the crawler generates:
1. **`screenshots/`**: High-resolution `.png` files of the course header, full syllabus, forum discussions, participant roster, grades, and user dashboard.
2. **`course_data.json`**: Structured JSON containing course title, breadcrumbs, sections, and activity links.
3. **`lms_report.md`**: Markdown report ready to be embedded or viewed in Antigravity or GitHub.

---

## 🤝 Contributing & License

MIT License. Created by [Gabriel Benselum](https://github.com/gbenselum).
