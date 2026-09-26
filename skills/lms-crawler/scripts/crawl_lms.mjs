#!/usr/bin/env node
/**
 * Cross-platform LMS Crawler & Screenshot Utility
 * Works on Windows, macOS, and Linux with ZERO npm dependencies.
 * Uses native Node.js (v18+) fetch and WebSocket APIs to control
 * Google Chrome or Microsoft Edge via Chrome DevTools Protocol (CDP).
 */

import { spawn, execSync } from 'node:child_process';
import { existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';

// ---------------------------------------------------------------------------
// 1. Parse Command Line Arguments
// ---------------------------------------------------------------------------
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    url: '',
    username: '',
    password: '',
    outputDir: path.join(process.cwd(), 'lms_output'),
    port: 9222,
    headless: true
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--url' || arg === '-u') {
      options.url = args[++i];
    } else if (arg.startsWith('--url=')) {
      options.url = arg.split('=')[1];
    } else if (arg === '--user' || arg === '--username') {
      options.username = args[++i];
    } else if (arg.startsWith('--user=')) {
      options.username = arg.split('=')[1];
    } else if (arg === '--pass' || arg === '--password' || arg === '-p') {
      options.password = args[++i];
    } else if (arg.startsWith('--pass=')) {
      options.password = arg.split('=')[1];
    } else if (arg === '--out' || arg === '--output' || arg === '-o') {
      options.outputDir = path.resolve(args[++i]);
    } else if (arg.startsWith('--out=')) {
      options.outputDir = path.resolve(arg.split('=')[1]);
    } else if (arg === '--port') {
      options.port = parseInt(args[++i], 10);
    } else if (arg === '--no-headless') {
      options.headless = false;
    }
  }

  return options;
}

// ---------------------------------------------------------------------------
// 2. Cross-Platform Browser Discovery (Windows, macOS, Linux)
// ---------------------------------------------------------------------------
function findBrowserExecutable() {
  if (process.env.CHROME_PATH && existsSync(process.env.CHROME_PATH)) {
    return process.env.CHROME_PATH;
  }
  if (process.env.BROWSER_PATH && existsSync(process.env.BROWSER_PATH)) {
    return process.env.BROWSER_PATH;
  }
  if (process.env.EDGE_PATH && existsSync(process.env.EDGE_PATH)) {
    return process.env.EDGE_PATH;
  }

  const platform = process.platform;

  if (platform === 'win32') {
    const localAppData = process.env.LOCALAPPDATA || '';
    const programFiles = process.env['ProgramFiles'] || 'C:\\Program Files';
    const programFilesX86 = process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)';

    const candidates = [
      // Google Chrome
      path.join(programFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(programFilesX86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(localAppData, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      // Microsoft Edge (Pre-installed on all modern Windows 10/11)
      path.join(programFilesX86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      path.join(programFiles, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      path.join(localAppData, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      // Brave
      path.join(programFiles, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
      path.join(localAppData, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe')
    ];

    for (const p of candidates) {
      if (p && existsSync(p)) return p;
    }
  } else if (platform === 'darwin') {
    const candidates = [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
      '/Applications/Chromium.app/Contents/MacOS/Chromium'
    ];
    for (const p of candidates) {
      if (existsSync(p)) return p;
    }
  } else {
    // Linux
    const candidates = [
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium-browser',
      '/usr/bin/chromium',
      '/usr/bin/microsoft-edge',
      '/usr/bin/microsoft-edge-stable'
    ];
    for (const p of candidates) {
      if (existsSync(p)) return p;
    }
  }

  throw new Error(
    `No supported browser (Google Chrome or Microsoft Edge) was found on your system (${platform}). ` +
    `Please install Chrome or Edge, or set the CHROME_PATH environment variable.`
  );
}

// ---------------------------------------------------------------------------
// 3. Chrome DevTools Protocol (CDP) WebSocket Client
// ---------------------------------------------------------------------------
class CDPClient {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.msgId = 0;
    this.pending = new Map();

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.id !== undefined && this.pending.has(data.id)) {
          const { resolve, reject } = this.pending.get(data.id);
          this.pending.delete(data.id);
          if (data.error) {
            reject(new Error(`CDP Error: ${JSON.stringify(data.error)}`));
          } else {
            resolve(data.result);
          }
        }
      } catch (err) {
        console.error('WebSocket parse error:', err);
      }
    };
  }

  async ready() {
    if (this.ws.readyState === WebSocket.OPEN) return;
    return new Promise((resolve, reject) => {
      this.ws.onopen = () => resolve();
      this.ws.onerror = (err) => reject(err);
    });
  }

  send(method, params = {}) {
    const id = ++this.msgId;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true
    });
    if (res.exceptionDetails) {
      console.warn('Evaluation warning:', res.exceptionDetails.text);
    }
    return res.result?.value;
  }

  async captureScreenshot(outputPath, fullPage = false) {
    const params = { format: 'png' };
    if (fullPage) {
      params.captureBeyondViewport = true;
    }
    const res = await this.send('Page.captureScreenshot', params);
    const buf = Buffer.from(res.data, 'base64');
    writeFileSync(outputPath, buf);
    const kb = (buf.length / 1024).toFixed(1);
    console.log(`[Screenshot] Saved: ${path.basename(outputPath)} (${kb} KB)`);
    return outputPath;
  }

  async wait(ms) {
    return new Promise(r => setTimeout(r, ms));
  }
}

// ---------------------------------------------------------------------------
// 4. Main Crawling Routine
// ---------------------------------------------------------------------------
async function main() {
  const options = parseArgs();

  if (!options.url) {
    console.error('Error: LMS URL is required. Example:');
    console.error('  node crawl_lms.mjs --url "https://inaconfirmantes.milaulas.com/course/view.php?id=5" --user "alenieto" --pass "Lte_2026"');
    process.exit(1);
  }

  mkdirSync(options.outputDir, { recursive: true });
  const screenshotsDir = path.join(options.outputDir, 'screenshots');
  mkdirSync(screenshotsDir, { recursive: true });

  const browserPath = findBrowserExecutable();
  console.log(`[Browser] Found executable: ${browserPath}`);

  // Create isolated temp profile directory
  const tempProfile = path.join(os.tmpdir(), `lms-crawler-profile-${Date.now()}`);
  mkdirSync(tempProfile, { recursive: true });

  const browserArgs = [
    options.headless ? '--headless=new' : '',
    `--remote-debugging-port=${options.port}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-networking',
    '--window-size=1440,1080',
    `--user-data-dir=${tempProfile}`,
    'about:blank'
  ].filter(Boolean);

  console.log(`[Browser] Launching on port ${options.port}...`);
  const browserProc = spawn(browserPath, browserArgs, {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false
  });

  let isExiting = false;
  function cleanup() {
    if (isExiting) return;
    isExiting = true;
    console.log('[Browser] Cleaning up processes and temp profile...');
    try {
      if (process.platform === 'win32') {
        execSync(`taskkill /pid ${browserProc.pid} /T /F`, { stdio: 'ignore' });
      } else {
        browserProc.kill('SIGTERM');
      }
    } catch (e) {}

    try {
      rmSync(tempProfile, { recursive: true, force: true });
    } catch (e) {}
  }

  process.on('exit', cleanup);
  process.on('SIGINT', () => { cleanup(); process.exit(0); });
  process.on('SIGTERM', () => { cleanup(); process.exit(0); });

  // Wait for browser devtools endpoint
  let pageWsUrl = null;
  const endpointUrl = `http://127.0.0.1:${options.port}/json/list`;
  for (let attempt = 0; attempt < 40; attempt++) {
    try {
      const res = await fetch(endpointUrl);
      if (res.ok) {
        const list = await res.json();
        const pageTarget = list.find(t => t.type === 'page');
        if (pageTarget && pageTarget.webSocketDebuggerUrl) {
          pageWsUrl = pageTarget.webSocketDebuggerUrl;
          break;
        }
      }
    } catch (e) {}
    await new Promise(r => setTimeout(r, 250));
  }

  if (!pageWsUrl) {
    cleanup();
    throw new Error(`Failed to connect to browser DevTools on port ${options.port}`);
  }

  console.log(`[CDP] Connected to target WebSocket: ${pageWsUrl}`);
  const client = new CDPClient(pageWsUrl);
  await client.ready();

  await client.send('Page.enable');
  await client.send('Runtime.enable');
  await client.send('DOM.enable');

  // Step 1: Navigate to Target LMS URL
  console.log(`[Navigation] Navigating to: ${options.url}`);
  await client.send('Page.navigate', { url: options.url });
  await client.wait(4000);

  // Capture initial screen
  await client.captureScreenshot(path.join(screenshotsDir, '01_initial_landing.png'));

  // Step 2: Handle Authentication if prompted
  if (options.username && options.password) {
    const hasLoginForm = await client.eval(`
      !!(document.querySelector('input[type="password"]') || document.querySelector('#password') || document.querySelector('#username'))
    `);

    if (hasLoginForm) {
      console.log(`[Auth] Login form detected. Submitting credentials for: ${options.username}...`);
      await client.eval(`
        (() => {
          const userField = document.querySelector('#username') || document.querySelector('input[name="username"]') || document.querySelector('input[type="text"]');
          const passField = document.querySelector('#password') || document.querySelector('input[name="password"]') || document.querySelector('input[type="password"]');
          if (userField) userField.value = ${JSON.stringify(options.username)};
          if (passField) passField.value = ${JSON.stringify(options.password)};

          const loginBtn = document.querySelector('#loginbtn') || document.querySelector('button[type="submit"]') || document.querySelector('input[type="submit"]');
          if (loginBtn) {
            loginBtn.click();
          } else {
            const form = document.querySelector('form#login') || document.querySelector('form');
            if (form) form.submit();
          }
        })()
      `);

      await client.wait(4500);
      console.log('[Auth] Authenticated. Validating destination...');
    }
  }

  // Step 3: Capture Course Main View (Viewport & Full Page)
  const currentUrl = await client.eval('window.location.href');
  const pageTitle = await client.eval('document.title');
  console.log(`[Course] Active URL: ${currentUrl}`);
  console.log(`[Course] Title: ${pageTitle}`);

  await client.captureScreenshot(path.join(screenshotsDir, '02_course_main_viewport.png'), false);
  await client.captureScreenshot(path.join(screenshotsDir, '03_course_main_fullpage.png'), true);

  // Step 4: Extract Course Structure & Interactive Activities
  console.log('[Analysis] Extracting sections, activities, and navigation elements...');
  const courseData = await client.eval(`(() => {
    const headerTitle = document.querySelector('.page-header-headings h1, h1')?.innerText?.trim() || document.title;
    const breadcrumbs = Array.from(document.querySelectorAll('.breadcrumb-item')).map(el => el.innerText.trim());

    // Extract all sections and their contents
    const sections = Array.from(document.querySelectorAll('.course-section, .section')).map((sec, idx) => {
      const sectionName = sec.querySelector('.sectionname, .section-title, h3, h4')?.innerText?.trim() || ('Sección ' + (idx + 1));
      const activities = Array.from(sec.querySelectorAll('.activity, .activityinstance')).map(act => {
        const linkElem = act.querySelector('a');
        const name = act.querySelector('.instancename, .activityname')?.innerText?.trim() || act.innerText?.trim();
        return {
          name: name ? name.split('\\n')[0] : '',
          link: linkElem ? linkElem.href : null
        };
      }).filter(a => a.name);

      return { title: sectionName, activities };
    }).filter(s => s.activities.length > 0 || s.title);

    // Extract sidebar navigation courses
    const sidebarCourses = Array.from(document.querySelectorAll('a'))
      .filter(a => a.href && a.href.includes('/course/view.php?id='))
      .map(a => ({ title: a.innerText.trim(), href: a.href }));

    return { headerTitle, breadcrumbs, sections, sidebarCourses };
  })()`);

  writeFileSync(path.join(options.outputDir, 'course_data.json'), JSON.stringify(courseData, null, 2));

  // Step 5: Capture Specific Moodle Views (Activities, Participants, Grades, Dashboard)
  const urlObj = new URL(currentUrl);
  const courseIdMatch = currentUrl.match(/[?&]id=(\\d+)/);
  const courseId = courseIdMatch ? courseIdMatch[1] : null;

  const extraViews = [];

  // Activities (first 2 forums/assignments found in the course)
  if (courseData && courseData.sections) {
    let actIndex = 1;
    for (const sec of courseData.sections) {
      for (const act of sec.activities) {
        if (act.link && !act.link.includes('#') && act.link !== currentUrl && extraViews.length < 3) {
          extraViews.push({
            name: `activity_${actIndex}_${act.name.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase()}`,
            url: act.link,
            label: `Actividad: ${act.name}`
          });
          actIndex++;
        }
      }
    }
  }

  if (courseId) {
    extraViews.push({
      name: 'participants_fullpage',
      url: `${urlObj.origin}/user/index.php?id=${courseId}`,
      label: 'Lista de Participantes'
    });
    extraViews.push({
      name: 'grades_fullpage',
      url: `${urlObj.origin}/grade/report/user/index.php?id=${courseId}`,
      label: 'Calificaciones del Estudiante'
    });
  }

  extraViews.push({
    name: 'dashboard_my_fullpage',
    url: `${urlObj.origin}/my/`,
    label: 'Área Personal / Mis Cursos'
  });

  for (const view of extraViews) {
    console.log(`[View] Capturing: ${view.label} (${view.url})...`);
    try {
      await client.send('Page.navigate', { url: view.url });
      await client.wait(3500);
      await client.captureScreenshot(path.join(screenshotsDir, `${view.name}.png`), true);
    } catch (err) {
      console.warn(`Could not capture view ${view.name}:`, err.message);
    }
  }

  // Step 6: Generate Markdown Report
  console.log('[Report] Compiling summary markdown report...');
  const reportLines = [
    `# LMS Crawl Report: ${courseData.headerTitle || pageTitle}`,
    '',
    `- **URL:** ${options.url}`,
    `- **Usuario:** ${options.username}`,
    `- **Fecha de Relevamiento:** ${new Date().toISOString()}`,
    '',
    '## 📸 Galería de Capturas',
    '',
    '| Archivo | Descripción |',
    '| :--- | :--- |',
    '| `01_initial_landing.png` | Pantalla de inicio de sesión o bienvenida |',
    '| `02_course_main_viewport.png` | Portada y cabecera del curso |',
    '| `03_course_main_fullpage.png` | Vista completa de todas las secciones del curso |'
  ];

  for (const view of extraViews) {
    reportLines.push(`| \`${view.name}.png\` | ${view.label} |`);
  }

  reportLines.push('', '## 📚 Estructura de Secciones');
  if (courseData.sections && courseData.sections.length > 0) {
    for (const sec of courseData.sections) {
      reportLines.push(`\n### ${sec.title}`);
      if (sec.activities.length === 0) {
        reportLines.push('- *Sin actividades en esta sección.*');
      } else {
        for (const act of sec.activities) {
          reportLines.push(`- **${act.name}**${act.link ? ` ([Enlace](${act.link}))` : ''}`);
        }
      }
    }
  }

  const reportPath = path.join(options.outputDir, 'lms_report.md');
  writeFileSync(reportPath, reportLines.join('\n'));
  console.log(`[Done] Report generated at: ${reportPath}`);

  cleanup();
  console.log('[Complete] Crawl finished successfully!');
}

main().catch(err => {
  console.error('[Fatal Error]:', err);
  process.exit(1);
});
