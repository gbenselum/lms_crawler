#!/usr/bin/env python3
"""
Generates the interactive, standalone navigable HTML viewers for the Chamilo LMS backup:
1. backup_chamilo/index.html (self-contained inside backup folder)
2. visor_backup.html (convenient launcher at repository root)
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(BASE_DIR, "backup_chamilo", "data", "lms_backup_manifest.json")

with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Loaded {len(items)} items from manifest.")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>InnovaEduca — Chamilo LMS Backup Explorer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #090d16;
      --bg-surface: #111827;
      --bg-card: #1a2234;
      --bg-card-hover: #222d44;
      --border: #2a364f;
      --border-subtle: #1e293b;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --accent-glow: rgba(59, 130, 246, 0.25);
      --badge-bg: rgba(59, 130, 246, 0.15);
      --badge-text: #60a5fa;
      --sidebar-width: 380px;
      --header-height: 68px;
    }

    html.light {
      --bg-base: #f8fafc;
      --bg-surface: #ffffff;
      --bg-card: #f1f5f9;
      --bg-card-hover: #e2e8f0;
      --border: #cbd5e1;
      --border-subtle: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-dim: #94a3b8;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-glow: rgba(37, 99, 235, 0.15);
      --badge-bg: rgba(37, 99, 235, 0.1);
      --badge-text: #1d4ed8;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-base);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Header */
    header {
      height: var(--header-height);
      background-color: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      z-index: 50;
      flex-shrink: 0;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-icon {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      box-shadow: 0 4px 12px var(--accent-glow);
    }

    .brand-text h1 {
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text-main);
    }

    .brand-text p {
      font-size: 11px;
      color: var(--text-muted);
      font-weight: 500;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .stats-pill {
      background: var(--badge-bg);
      color: var(--badge-text);
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      border: 1px solid rgba(59, 130, 246, 0.2);
    }

    .search-box {
      position: relative;
      width: 280px;
    }

    .search-box input {
      width: 100%;
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 8px 14px 8px 36px;
      border-radius: 8px;
      font-size: 13px;
      font-family: inherit;
      outline: none;
      transition: all 0.2s;
    }

    .search-box input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }

    .search-icon {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 14px;
      color: var(--text-dim);
      pointer-events: none;
    }

    .theme-toggle-btn {
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 16px;
      transition: all 0.2s;
    }

    .theme-toggle-btn:hover {
      background: var(--bg-card-hover);
      border-color: var(--accent);
    }

    /* Main Container */
    .app-body {
      display: flex;
      flex: 1;
      height: calc(100vh - var(--header-height));
      overflow: hidden;
    }

    /* Sidebar */
    .sidebar {
      width: var(--sidebar-width);
      background: var(--bg-surface);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      height: 100%;
    }

    .sidebar-filter-bar {
      padding: 12px 14px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      gap: 6px;
      overflow-x: auto;
      flex-shrink: 0;
    }

    .filter-chip {
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
    }

    .filter-chip.active, .filter-chip:hover {
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }

    .screen-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .category-divider {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 12px 8px 4px 8px;
    }

    .screen-card {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 10px 12px;
      border-radius: 8px;
      cursor: pointer;
      background: transparent;
      border: 1px solid transparent;
      transition: all 0.15s;
    }

    .screen-card:hover {
      background: var(--bg-card-hover);
      border-color: var(--border);
    }

    .screen-card.active {
      background: var(--bg-card);
      border-color: var(--accent);
      box-shadow: 0 2px 8px var(--accent-glow);
    }

    .card-idx {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 600;
      color: var(--text-dim);
      background: rgba(255, 255, 255, 0.05);
      padding: 2px 6px;
      border-radius: 4px;
      margin-top: 1px;
      flex-shrink: 0;
    }

    .card-info {
      flex: 1;
      min-width: 0;
    }

    .card-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.3;
    }

    .card-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 4px;
      font-size: 11px;
      color: var(--text-muted);
    }

    .card-badge {
      background: rgba(255, 255, 255, 0.08);
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 10px;
    }

    .badge-iframe {
      background: rgba(168, 85, 247, 0.15);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.3);
    }

    /* Content Area */
    .content-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      background: var(--bg-base);
      overflow: hidden;
    }

    .content-toolbar {
      padding: 12px 20px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
      gap: 16px;
    }

    .active-header {
      min-width: 0;
    }

    .active-header h2 {
      font-size: 16px;
      font-weight: 700;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--text-main);
    }

    .active-header .url-tag {
      font-size: 11px;
      color: var(--text-dim);
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 2px;
      text-decoration: none;
    }

    .active-header .url-tag:hover {
      color: var(--accent);
    }

    .view-tabs {
      display: flex;
      background: var(--bg-card);
      padding: 3px;
      border-radius: 8px;
      border: 1px solid var(--border);
      flex-shrink: 0;
    }

    .view-tab {
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      border: none;
      background: transparent;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .view-tab.active {
      background: var(--accent);
      color: #ffffff;
      box-shadow: 0 2px 6px var(--accent-glow);
    }

    .action-links {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .btn-secondary {
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }

    .btn-secondary:hover {
      background: var(--bg-card-hover);
      border-color: var(--accent);
    }

    /* Viewer Container */
    .viewer-viewport {
      flex: 1;
      overflow: auto;
      padding: 16px;
      display: flex;
      justify-content: center;
      position: relative;
    }

    /* Screenshot View */
    .screenshot-container {
      width: 100%;
      max-width: 1440px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .screenshot-img {
      width: 100%;
      height: auto;
      border-radius: 8px;
      border: 1px solid var(--border);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
      background: #ffffff;
    }

    /* Frame View */
    .frame-container {
      width: 100%;
      height: 100%;
      border-radius: 8px;
      border: 1px solid var(--border);
      overflow: hidden;
      background: #ffffff;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }

    .frame-view {
      width: 100%;
      height: 100%;
      border: none;
      background: #ffffff;
    }

    /* Metadata View */
    .meta-container {
      width: 100%;
      max-width: 800px;
      margin: 20px auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .meta-card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .meta-card h3 {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 12px;
      color: var(--badge-text);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .meta-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid var(--border-subtle);
      font-size: 13px;
    }

    .meta-row:last-child {
      border-bottom: none;
    }

    .meta-label {
      color: var(--text-muted);
      font-weight: 500;
    }

    .meta-val {
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-main);
      font-weight: 600;
      max-width: 450px;
      word-break: break-all;
      text-align: right;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .sidebar {
        width: 300px;
      }
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <div class="brand">
      <div class="brand-icon">🎓</div>
      <div class="brand-text">
        <h1>InnovaEduca — Chamilo LMS Explorer</h1>
        <p>Backup Completo Offline (Screenshots + Rendered HTML)</p>
      </div>
    </div>

    <div class="header-actions">
      <div class="stats-pill">
        <span>⚡</span>
        <span id="screen-count">57 Pantallas</span>
      </div>

      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="search-input" placeholder="Buscar pantalla o módulo... (Presione /)">
      </div>

      <button class="theme-toggle-btn" id="theme-btn" title="Alternar Modo Oscuro / Claro">🌓</button>
    </div>
  </header>

  <!-- App Body -->
  <div class="app-body">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-filter-bar" id="category-filters">
        <button class="filter-chip active" data-cat="all">Todos (57)</button>
        <button class="filter-chip" data-cat="Portal General">Portal (12)</button>
        <button class="filter-chip" data-cat="Herramientas de Curso">Curso (11)</button>
        <button class="filter-chip" data-cat="Foros de Debate">Foros (7)</button>
        <button class="filter-chip" data-cat="LP 2">Módulo 0</button>
        <button class="filter-chip" data-cat="LP 1">Módulo 1</button>
        <button class="filter-chip" data-cat="LP 3">Módulo 2</button>
        <button class="filter-chip" data-cat="LP 4">Módulo 6</button>
      </div>

      <div class="screen-list" id="screen-list">
        <!-- Rendered dynamically -->
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="content-area">
      <!-- Toolbar -->
      <div class="content-toolbar">
        <div class="active-header">
          <h2 id="active-title">Seleccione una pantalla</h2>
          <a href="#" target="_blank" id="active-url" class="url-tag">
            <span>🔗</span>
            <span id="active-url-text">https://chamilo.educa.website</span>
          </a>
        </div>

        <div class="view-tabs">
          <button class="view-tab active" data-tab="screenshot">
            <span>📸</span> Captura PNG
          </button>
          <button class="view-tab" data-tab="html">
            <span>🌐</span> Snapshot HTML
          </button>
          <button class="view-tab" data-tab="iframe" id="tab-iframe" style="display: none;">
            <span>📄</span> Documento Embebido
          </button>
          <button class="view-tab" data-tab="meta">
            <span>ℹ️</span> Metadatos
          </button>
        </div>

        <div class="action-links">
          <a href="#" target="_blank" id="btn-open-tab" class="btn-secondary">
            <span>↗️</span> Abrir archivo
          </a>
        </div>
      </div>

      <!-- Viewport -->
      <div class="viewer-viewport">
        <!-- Screenshot Tab -->
        <div id="view-screenshot" class="screenshot-container">
          <img id="main-screenshot" class="screenshot-img" src="" alt="Captura de pantalla">
        </div>

        <!-- HTML View Tab -->
        <div id="view-html" class="frame-container" style="display: none;">
          <iframe id="main-frame" class="frame-view" sandbox="allow-scripts allow-same-origin"></iframe>
        </div>

        <!-- Iframe Doc Tab -->
        <div id="view-iframe" class="frame-container" style="display: none;">
          <iframe id="sub-frame" class="frame-view" sandbox="allow-scripts allow-same-origin"></iframe>
        </div>

        <!-- Metadata Tab -->
        <div id="view-meta" class="meta-container" style="display: none;">
          <div class="meta-card">
            <h3>📑 Ficha Técnica del Recurso</h3>
            <div class="meta-row">
              <span class="meta-label">Clave / Identificador:</span>
              <span class="meta-val" id="meta-key">-</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Título Registrado:</span>
              <span class="meta-val" id="meta-title">-</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Categoría:</span>
              <span class="meta-val" id="meta-category">-</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Dirección URL Original:</span>
              <span class="meta-val" id="meta-url">-</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Peso HTML:</span>
              <span class="meta-val" id="meta-size">-</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Captura PNG:</span>
              <span class="meta-val" id="meta-ss-path">-</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Snapshot HTML:</span>
              <span class="meta-val" id="meta-html-path">-</span>
            </div>
            <div class="meta-row" id="meta-iframe-row" style="display: none;">
              <span class="meta-label">Documento Embebido (Iframe):</span>
              <span class="meta-val" id="meta-iframe-path">-</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Fecha y Hora de Extracción:</span>
              <span class="meta-val" id="meta-timestamp">-</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <script>
    const PATH_PREFIX = "__PATH_PREFIX__";
    const ITEMS = __ITEMS_JSON__;

    let currentIndex = 0;
    let currentTab = 'screenshot';
    let currentFilter = 'all';

    const screenListEl = document.getElementById('screen-list');
    const searchInput = document.getElementById('search-input');
    const themeBtn = document.getElementById('theme-btn');

    const activeTitle = document.getElementById('active-title');
    const activeUrl = document.getElementById('active-url');
    const activeUrlText = document.getElementById('active-url-text');
    const btnOpenTab = document.getElementById('btn-open-tab');

    const mainScreenshot = document.getElementById('main-screenshot');
    const mainFrame = document.getElementById('main-frame');
    const subFrame = document.getElementById('sub-frame');
    const tabIframe = document.getElementById('tab-iframe');

    const viewScreenshot = document.getElementById('view-screenshot');
    const viewHtml = document.getElementById('view-html');
    const viewIframe = document.getElementById('view-iframe');
    const viewMeta = document.getElementById('view-meta');

    // Theme toggle
    themeBtn.addEventListener('click', () => {
      document.documentElement.classList.toggle('dark');
      document.documentElement.classList.toggle('light');
    });

    // Render screen list
    function renderList() {
      const query = searchInput.value.toLowerCase();
      screenListEl.innerHTML = '';

      let lastCategory = '';

      ITEMS.forEach((item, idx) => {
        // Filter by category
        if (currentFilter !== 'all') {
          if (!item.category.includes(currentFilter)) return;
        }

        // Filter by search query
        if (query) {
          const matchLabel = item.label.toLowerCase().includes(query);
          const matchKey = item.key.toLowerCase().includes(query);
          const matchCat = item.category.toLowerCase().includes(query);
          if (!matchLabel && !matchKey && !matchCat) return;
        }

        // Category header divider
        if (item.category !== lastCategory) {
          lastCategory = item.category;
          const div = document.createElement('div');
          div.className = 'category-divider';
          div.textContent = item.category;
          screenListEl.appendChild(div);
        }

        const card = document.createElement('div');
        card.className = `screen-card ${idx === currentIndex ? 'active' : ''}`;
        card.innerHTML = `
          <div class="card-idx">${String(idx + 1).padStart(2, '0')}</div>
          <div class="card-info">
            <div class="card-title">${item.label}</div>
            <div class="card-meta">
              <span>${(item.html_size_bytes / 1024).toFixed(0)} KB</span>
              ${item.iframe_html ? '<span class="card-badge badge-iframe">Embebido</span>' : ''}
            </div>
          </div>
        `;

        card.addEventListener('click', () => selectItem(idx));
        screenListEl.appendChild(card);
      });
    }

    function selectItem(idx) {
      currentIndex = idx;
      const item = ITEMS[idx];
      if (!item) return;

      // Update card active states
      document.querySelectorAll('.screen-card').forEach((c, i) => {
        c.classList.toggle('active', i === idx);
      });

      // Update Header Info
      activeTitle.textContent = item.label;
      activeUrl.href = item.url;
      activeUrlText.textContent = item.url;

      // Paths
      const ssPath = PATH_PREFIX + item.screenshot;
      const htmlPath = PATH_PREFIX + item.html;
      const iframePath = item.iframe_html ? PATH_PREFIX + item.iframe_html : null;

      mainScreenshot.src = ssPath;
      mainFrame.src = htmlPath;

      if (iframePath) {
        subFrame.src = iframePath;
        tabIframe.style.display = 'flex';
      } else {
        tabIframe.style.display = 'none';
        if (currentTab === 'iframe') {
          switchTab('screenshot');
        }
      }

      // Update Metadata Card
      document.getElementById('meta-key').textContent = item.key;
      document.getElementById('meta-title').textContent = item.title;
      document.getElementById('meta-category').textContent = item.category;
      document.getElementById('meta-url').textContent = item.url;
      document.getElementById('meta-size').textContent = (item.html_size_bytes / 1024).toFixed(1) + ' KB';
      document.getElementById('meta-ss-path').textContent = ssPath;
      document.getElementById('meta-html-path').textContent = htmlPath;
      document.getElementById('meta-timestamp').textContent = item.timestamp;

      if (iframePath) {
        document.getElementById('meta-iframe-row').style.display = 'flex';
        document.getElementById('meta-iframe-path').textContent = iframePath;
      } else {
        document.getElementById('meta-iframe-row').style.display = 'none';
      }

      // Update action button
      if (currentTab === 'screenshot') {
        btnOpenTab.href = ssPath;
      } else if (currentTab === 'html') {
        btnOpenTab.href = htmlPath;
      } else if (currentTab === 'iframe' && iframePath) {
        btnOpenTab.href = iframePath;
      } else {
        btnOpenTab.href = htmlPath;
      }
    }

    function switchTab(tab) {
      currentTab = tab;
      document.querySelectorAll('.view-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-tab') === tab);
      });

      viewScreenshot.style.display = tab === 'screenshot' ? 'flex' : 'none';
      viewHtml.style.display = tab === 'html' ? 'block' : 'none';
      viewIframe.style.display = tab === 'iframe' ? 'block' : 'none';
      viewMeta.style.display = tab === 'meta' ? 'flex' : 'none';

      const item = ITEMS[currentIndex];
      if (tab === 'screenshot') {
        btnOpenTab.href = PATH_PREFIX + item.screenshot;
      } else if (tab === 'html') {
        btnOpenTab.href = PATH_PREFIX + item.html;
      } else if (tab === 'iframe' && item.iframe_html) {
        btnOpenTab.href = PATH_PREFIX + item.iframe_html;
      }
    }

    // View tab handlers
    document.querySelectorAll('.view-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        switchTab(btn.getAttribute('data-tab'));
      });
    });

    // Category filter chips
    document.querySelectorAll('.filter-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentFilter = chip.getAttribute('data-cat');
        renderList();
      });
    });

    // Search input
    searchInput.addEventListener('input', () => renderList());

    // Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.target === searchInput) {
        if (e.key === 'Escape') searchInput.blur();
        return;
      }

      if (e.key === '/') {
        e.preventDefault();
        searchInput.focus();
      } else if (e.key === 'ArrowDown' || e.key === 'j') {
        if (currentIndex < ITEMS.length - 1) selectItem(currentIndex + 1);
      } else if (e.key === 'ArrowUp' || e.key === 'k') {
        if (currentIndex > 0) selectItem(currentIndex - 1);
      } else if (e.key === '1') {
        switchTab('screenshot');
      } else if (e.key === '2') {
        switchTab('html');
      } else if (e.key === '3' && ITEMS[currentIndex]?.iframe_html) {
        switchTab('iframe');
      } else if (e.key === '4') {
        switchTab('meta');
      }
    });

    // Init
    renderList();
    selectItem(0);
  </script>
</body>
</html>
"""

# 1. Generate backup_chamilo/index.html
chamilo_index_path = os.path.join(BASE_DIR, "backup_chamilo", "index.html")
chamilo_html = HTML_TEMPLATE.replace("__PATH_PREFIX__", "").replace("__ITEMS_JSON__", json.dumps(items))
with open(chamilo_index_path, "w", encoding="utf-8") as f:
    f.write(chamilo_html)
print(f"Generated: {chamilo_index_path}")

# 2. Generate visor_backup.html (Root Launcher)
root_visor_path = os.path.join(BASE_DIR, "visor_backup.html")
root_html = HTML_TEMPLATE.replace("__PATH_PREFIX__", "backup_chamilo/").replace("__ITEMS_JSON__", json.dumps(items))
with open(root_visor_path, "w", encoding="utf-8") as f:
    f.write(root_html)
print(f"Generated: {root_visor_path}")

print("Both interactive viewers created successfully!")
