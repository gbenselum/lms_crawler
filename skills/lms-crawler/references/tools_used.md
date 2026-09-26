# Tools Used & Technical Architecture

This document details the tools, protocols, and architectural decisions used to build the LMS Crawler skill.

---

## 1. Architectural Design Choices

Traditional scraping solutions (Puppeteer, Playwright, Selenium) often face multiple hurdles in modern developer environments:
- They require downloading massive binaries (Chromium ~200MB).
- NPM package installation often fails behind corporate firewalls, VPNs, or strict security sandboxes (e.g. `HTTP 403 Forbidden` on `registry.npmjs.org`).
- Heavy dependencies introduce version mismatch bugs.

### Our Solution: Zero-Dependency Native CDP
We built a lightweight, native Chrome DevTools Protocol client using **standard Node.js libraries**:
- **`node:child_process`**: Launches the local Chrome or Edge browser binary.
- **Native `fetch()`** (Node 18+): Queries `http://127.0.0.1:9222/json/list` to discover open page targets.
- **Native `WebSocket`** (Node 21+): Establishes a direct bidirectional connection with the browser's DevTools engine.

---

## 2. Tools Breakdown

### A. Browser Engine: Chromium (Google Chrome & Microsoft Edge)
- **Engine:** Chromium 120+
- **Command Line Flags:**
  - `--headless=new`: Modern Chrome headless mode with full rendering parity to visible browser.
  - `--remote-debugging-port=9222`: Exposes DevTools HTTP and WebSocket endpoints.
  - `--user-data-dir=<temp>`: Isolates user data and prevents interfering with existing browser windows.
  - `--window-size=1440,1080`: Ensures clean, high-resolution desktop rendering.

### B. Chrome DevTools Protocol (CDP) Domains
The crawler interacts directly with the Chromium engine using these CDP domains:

| Domain | Methods Used | Purpose |
| :--- | :--- | :--- |
| `Page` | `Page.enable`, `Page.navigate`, `Page.captureScreenshot` | Navigates URLs and captures PNG buffers with `captureBeyondViewport: true` for full-page stitching. |
| `Runtime` | `Runtime.enable`, `Runtime.evaluate` | Injects JavaScript into the DOM to fill forms, click buttons, and extract metadata. |
| `DOM` | `DOM.enable` | Ensures DOM tree updates are synced during dynamic page transitions. |

### C. Node.js Runtime
- Utilizes native asynchronous primitives (`async/await`, `Promise`, `Map`).
- Native buffer conversion: `Buffer.from(base64Data, 'base64')` writes PNGs directly to disk.
- Cross-platform process management: Uses `taskkill /pid ... /T /F` on Windows and `SIGTERM` on Unix.

### D. Antigravity Agent Customization System
- **`SKILL.md` Specification**: Exposes the workflow to Antigravity's progressive disclosure mechanism.
- **Artifact Integration**: Allows Antigravity to render interactive carousels, embedded PNGs, and markdown reports.
