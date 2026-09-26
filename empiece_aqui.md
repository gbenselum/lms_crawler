# 🚀 Empiece Aquí — Guía Integral del Repositorio y Backup de Chamilo LMS

Bienvenido al repositorio de automatización y respaldo offline de **Chamilo LMS** (*InnovaEduca*).

Este proyecto contiene tanto las herramientas de crawling y extracción basadas en navegador headless (Playwright / Chrome DevTools Protocol) como el **backup completo (HTML + Screenshots + Datos estructurados)** de todo el campus virtual y del curso *«Enseñar en la era Digital: Propuestas con recursos digitales para el aula»*.

> [!TIP]
> 🌐 **Visor en línea disponible en GitHub Pages:** [**https://gbenselum.github.io/lms_crawler/**](https://gbenselum.github.io/lms_crawler/)  
> También podés acceder directamente a [`visor_backup.html`](https://gbenselum.github.io/lms_crawler/visor_backup.html) o abrirlo de manera 100% offline en tu computadora.

---


## 🗂️ Estructura General de Carpetas

A continuación se detalla la organización de archivos de la raíz y de cada subcarpeta:

```text
lms_crawler/
├── empiece_aqui.md                <-- [ESTE ARCHIVO] Manual de organización, navegación y uso
├── README.md                      <-- Documentación técnica de la Skill de Antigravity
├── run_full_backup.py             <-- Script en Python (Playwright) que generó el backup completo
├── visor_backup.html              <-- Acceso directo al visor interactivo offline
│
├── backup_chamilo/                <-- 📦 CONTENEDOR DEL BACKUP COMPLETO
│   ├── index.html                 <-- Aplicación web interactiva para explorar todo el backup
│   ├── lms_backup_report.md       <-- Reporte técnico en Markdown con tablas de todas las pantallas
│   │
│   ├── html/                      <-- 🌐 86 Archivos HTML (Renderizados completos + Documentos)
│   ├── screenshots/               <-- 📸 57 Capturas Full-Page en alta resolución (PNG)
│   └── data/                      <-- 📊 Metadatos en formato estructurado (JSON)
│       └── lms_backup_manifest.json
│
├── skills/                        <-- Antigravity Skill para automatización en Windows/macOS/Linux
│   └── lms-crawler/
│       ├── SKILL.md
│       ├── scripts/               <-- Script Node.js nativo con cero dependencias externas
│       │   └── crawl_lms.mjs
│       └── references/            <-- Guías de arquitectura CDP y configuración en Windows
│
└── examples/                      <-- Ejemplos y plantillas de reportes previos
```

---

## 📦 Detalle de la Carpeta `backup_chamilo/`

La carpeta [`backup_chamilo/`](./backup_chamilo/) es el núcleo del respaldo descargado. Está estructurada en 3 subdirectorios especializados:

### 1. `backup_chamilo/screenshots/` (57 imágenes PNG, ~15 MB)
Contiene las capturas de pantalla completa (*full-page*) de cada sección, con una resolución base de 1440x900 a escala de alta densidad (1.5x):
- **Prefijo `01_` a `12_`:** Portal general (Login, Dashboard Home, Mis Cursos, Catálogo, Agenda global, Progreso, Red Social, Mensajería, Amigos, Grupos, Archivos personales y Datos de perfil).
- **Prefijo `13_` a `23_`:** Herramientas del curso (Portada, Descripción, Anuncios, Roster de participantes, Tareas, Detalle de entrega de tarea, Evaluaciones/Ejercicios, Cuaderno de calificaciones, Enlaces web, Agenda del curso y Catálogo de lecciones).
- **Prefijo `24_` a `30_`:** Foros de debate (Índice de foros, hilos individuales temáticos y debate abierto *«Iniciamos la conversación aquí»*).
- **Prefijo `31_`, `32_`, `33_`:** Lecciones interactivas organizadas por módulos:
  - `lp2_mod0`: Módulo 0 (Tutorial Chamilo, Guía de recorrido, Estadísticas).
  - `lp1_mod1`: Módulo 1 (Desafiando la sincronía, Microcápsula de texto, Semáforo, Estadísticas).
  - `lp3_mod2`: Módulo 2 (Hoja de ruta, Rúbrica, Bitácora, Guía, Equipamiento, Kahoot, Sala de escape, Reflexión, Tarea, Estadísticas).
  - `lp4_mod6`: Módulo 6 (Hoja de ruta final, Bienvenidos al cierre, Revisamos lo aprendido, Recorremos el camino, Turno de decidir, Estadísticas).

### 2. `backup_chamilo/html/` (86 archivos HTML, ~7.4 MB)
Contiene los snapshots del código fuente y del árbol DOM completamente renderizado en el navegador:
- **Snapshots de Pantallas Principales (`[clave].html`):** Contiene el HTML completo con estilos, clases Vue/Tailwind/PrimeVue y componentes cargados.
- **Documentos Embebidos (`[clave]_doc_iframe.html`):** Chamilo carga muchos materiales didácticos (como hojas de ruta interactivas, juegos de escape, actividades de Kahoot, rúbricas y microcápsulas) dentro de etiquetas `<iframe>`. Este backup extrajo de manera individual el HTML interno de cada uno de esos documentos para que no se pierda ningún texto ni interactividad didáctica.

### 3. `backup_chamilo/data/` (Metadatos JSON)
- **`lms_backup_manifest.json`:** Contiene el catálogo completo en formato JSON con las 57 pantallas registradas. Cada entrada especifica:
  - `key`: Identificador único del archivo.
  - `label`: Título legible de la pantalla.
  - `category`: Categoría funcional (Portal General, Herramientas, Foros, Lecciones).
  - `url`: Dirección web original en el LMS en vivo.
  - `screenshot`: Ruta relativa a la captura de pantalla.
  - `html`: Ruta relativa al snapshot HTML.
  - `iframe_html`: Ruta al documento embebido si correspondía.
  - `html_size_bytes`: Peso exacto del documento.
  - `timestamp`: Fecha y hora de captura.

---

## 🖥️ Cómo Explorar el Backup de Forma Navegable

Tienes dos formas sumamente cómodas de navegar todo el contenido sin necesidad de conexión a Internet ni servidores externos:

### Opción A: A través del Visor Web Interactivo (`visor_backup.html` o `backup_chamilo/index.html`)
1. Haz doble clic en el archivo [`visor_backup.html`](./visor_backup.html) o ábrelo en tu navegador favorito (Chrome, Edge, Safari, Firefox, Brave).
2. **Características del Visor:**
   - **Buscador en tiempo real:** Filtra instantáneamente entre las 57 pantallas por nombre o palabra clave.
   - **Filtro por Categorías:** Explora por Portal, Herramientas del Curso, Foros o por cada Módulo específico (0, 1, 2, 6).
   - **Vista Dual (Screenshot / HTML Renderizado):** Alterna entre ver la captura visual exacta o renderizar el archivo HTML respaldado.
   - **Documentos Embebidos:** Botón directo para visualizar los documentos interactivos que estaban dentro de iframes.
   - **Atajos de teclado:** Usa las flechas `Arriba` / `Abajo` para navegar entre pantallas y los números `1` / `2` / `3` para cambiar de pestaña.
   - **Modo Oscuro / Claro:** Selector de tema integrado.

### Opción B: A través de los Reportes en Markdown
- Puedes abrir el reporte técnico [`backup_chamilo/lms_backup_report.md`](./backup_chamilo/lms_backup_report.md) directamente en VS Code, Antigravity IDE o GitHub para acceder a las tablas comparativas y enlaces de cada archivo.

---

## 🔄 Cómo Volver a Ejecutar o Actualizar el Backup

Si en el futuro el curso agrega nuevas secciones o deseas actualizar las capturas:

```bash
# Ejecutar con uv (recomendado, maneja dependencias de Playwright automáticamente):
uv run --with playwright python run_full_backup.py
```

El script volverá a conectarse, autenticarse, refrescar las 57 pantallas y actualizar los reportes automáticamente.
