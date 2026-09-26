#!/usr/bin/env python3
"""
Full Automated Backup Script for Chamilo LMS
Captures:
- Full-page and viewport screenshots for every screen
- Complete HTML source snapshots
- Iframe lesson documents and content
- Structured metadata manifest JSON
- Markdown summary report with embedded gallery
"""

import asyncio
import json
import os
import sys
import re
from datetime import datetime
from playwright.async_api import async_playwright

LMS_URL = "https://chamilo.educa.website/"
USERNAME = "PauGonzalez"
PASSWORD = "Paula01!"

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "backup_chamilo"))
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")
HTML_DIR = os.path.join(OUTPUT_DIR, "html")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

manifest = []

async def save_page_snapshot(page, key, label, category, custom_url=None):
    current_url = custom_url or page.url
    page_title = await page.title()
    print(f"[{category}] Saving snapshot: {label} ({key})...")

    # Full page screenshot
    screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{key}.png")
    try:
        await page.screenshot(path=screenshot_path, full_page=True)
    except Exception as e:
        print(f"  [Warning] Full page screenshot failed, falling back to viewport: {e}")
        await page.screenshot(path=screenshot_path, full_page=False)

    # HTML snapshot
    html_content = await page.content()
    html_path = os.path.join(HTML_DIR, f"{key}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    item_record = {
        "key": key,
        "label": label,
        "category": category,
        "url": current_url,
        "title": page_title,
        "screenshot": f"screenshots/{key}.png",
        "html": f"html/{key}.html",
        "html_size_bytes": len(html_content.encode("utf-8")),
        "timestamp": datetime.now().isoformat()
    }

    # If an iframe is present (e.g., in lessons), check for iframe document content
    try:
        iframe_elem = await page.query_selector("iframe[name='content_name'], iframe#content_id, iframe")
        if iframe_elem:
            src = await iframe_elem.get_attribute("src")
            frame = page.frame(name="content_name") or page.frames[1] if len(page.frames) > 1 else None
            if frame:
                try:
                    frame_html = await frame.content()
                    if frame_html and len(frame_html) > 50:
                        frame_html_path = os.path.join(HTML_DIR, f"{key}_doc_iframe.html")
                        with open(frame_html_path, "w", encoding="utf-8") as ff:
                            ff.write(frame_html)
                        item_record["iframe_doc_url"] = src
                        item_record["iframe_html"] = f"html/{key}_doc_iframe.html"
                        item_record["iframe_size_bytes"] = len(frame_html.encode("utf-8"))
                        print(f"  -> Captured embedded document ({len(frame_html)} bytes)")
                except Exception as fe:
                    print(f"  [Notice] Frame content extraction: {fe}")
    except Exception as ie:
        pass

    manifest.append(item_record)
    return item_record


async def main():
    print(f"=== Starting Comprehensive LMS Backup ===")
    print(f"Target: {LMS_URL}")
    print(f"User: {USERNAME}")
    print(f"Output directory: {OUTPUT_DIR}")

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome_path):
        chrome_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=chrome_path,
            headless=True
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5
        )
        page = await context.new_page()

        # ---------------------------------------------------------
        # 1. Login Page
        # ---------------------------------------------------------
        print("\n--- 1. Login Screen ---")
        await page.goto(LMS_URL, wait_until="networkidle")
        await asyncio.sleep(2)
        await save_page_snapshot(page, "01_login_page", "Pantalla de Inicio de Sesión", "Portal General")

        # Perform Login
        print("[Auth] Submitting login credentials...")
        await page.fill("#login", USERNAME)
        await page.fill("#password", PASSWORD)
        await page.click("button[type='submit'], input[type='submit'], #submit-login")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        # ---------------------------------------------------------
        # 2. Portal General & Student Dashboard Views
        # ---------------------------------------------------------
        print("\n--- 2. Portal General & Perfil de Estudiante ---")
        portal_pages = [
            ("02_dashboard_home", "Página Principal (Home)", "https://chamilo.educa.website/home"),
            ("03_my_courses", "Mis Cursos Registrados", "https://chamilo.educa.website/courses"),
            ("04_course_catalog", "Catálogo de Cursos", "https://chamilo.educa.website/catalogue/courses"),
            ("05_global_agenda", "Agenda / Calendario General", "https://chamilo.educa.website/resources/ccalendarevent"),
            ("06_global_progress", "Informes y Progreso Académico", "https://chamilo.educa.website/main/auth/my_progress.php"),
            ("07_social_network", "Red Social del Campus", "https://chamilo.educa.website/social"),
            ("08_messages_inbox", "Bandeja de Mensajes Privados", "https://chamilo.educa.website/resources/messages"),
            ("09_friends", "Contactos y Amigos", "https://chamilo.educa.website/resources/friends"),
            ("10_groups", "Grupos de Usuarios", "https://chamilo.educa.website/resources/usergroups"),
            ("11_personal_files", "Mis Archivos Personales", "https://chamilo.educa.website/resources/personal_files/82/"),
            ("12_personal_data", "Datos Personales y Perfil", "https://chamilo.educa.website/resources/users/personal_data")
        ]

        for key, label, url in portal_pages:
            try:
                await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(2.5)
                await save_page_snapshot(page, key, label, "Portal General")
            except Exception as e:
                print(f"[Error] Failed to load {url}: {e}")

        # ---------------------------------------------------------
        # 3. Course Core Tools (Enseñar en la era Digital, cid=1)
        # ---------------------------------------------------------
        print("\n--- 3. Herramientas del Curso: Enseñar en la era Digital ---")
        course_tools = [
            ("13_course_home", "Portada y Menú Principal del Curso", "https://chamilo.educa.website/course/1/home?sid=0"),
            ("14_course_description", "Descripción y Objetivos del Curso", "https://chamilo.educa.website/main/course_description/index.php?cid=1&gid=0"),
            ("15_course_announcements", "Tablón de Anuncios del Curso", "https://chamilo.educa.website/main/announcements/announcements.php?cid=1&gid=0"),
            ("16_course_users_roster", "Listado de Participantes y Docentes", "https://chamilo.educa.website/main/user/user.php?cid=1&gid=0"),
            ("17_course_assignments_list", "Listado de Tareas Asignadas", "https://chamilo.educa.website/resources/assignment/5?cid=1&gid=0"),
            ("18_course_assignment_detail", "Detalle y Entrega: Tarea El Gran Rediseño", "https://chamilo.educa.website/resources/assignment/5/submission/1?cid=1"),
            ("19_course_exercises", "Evaluaciones y Ejercicios", "https://chamilo.educa.website/main/exercise/exercise.php?cid=1&gid=0"),
            ("20_course_gradebook", "Cuaderno de Calificaciones", "https://chamilo.educa.website/main/gradebook/index.php?cid=1&gid=0"),
            ("21_course_links", "Enlaces y Recursos Web del Curso", "https://chamilo.educa.website/main/link/link.php?cid=1&gid=0"),
            ("22_course_agenda", "Agenda y Calendario del Curso", "https://chamilo.educa.website/main/calendar/agenda.php?cid=1&gid=0"),
            ("23_course_lessons_catalog", "Catálogo Central de Lecciones", "https://chamilo.educa.website/resources/lp/5/?cid=1&gid=0")
        ]

        for key, label, url in course_tools:
            try:
                await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(2.5)
                await save_page_snapshot(page, key, label, "Herramientas de Curso")
            except Exception as e:
                print(f"[Error] Failed to load {url}: {e}")

        # ---------------------------------------------------------
        # 4. Forums & Discussions
        # ---------------------------------------------------------
        print("\n--- 4. Foros y Debates del Curso ---")
        forum_pages = [
            ("24_forums_index", "Índice Principal de Foros", "https://chamilo.educa.website/main/forum/index.php?cid=1&gid=0"),
            ("25_forum_1_nos_conocemos", "Foro: Nos conocemos", "https://chamilo.educa.website/main/forum/viewforum.php?cid=1&sid=0&gid=0&gradebook=0&origin=&gid=0&forum=1"),
            ("26_forum_2_consultas", "Foro: ¡Bienvenidos/as al espacio de Consultas!", "https://chamilo.educa.website/main/forum/viewforum.php?cid=1&sid=0&gid=0&gradebook=0&origin=&gid=0&forum=2"),
            ("27_forum_3_desafios_asincronia", "Foro: Desafíos de la asincronía: experiencias compartidas", "https://chamilo.educa.website/main/forum/viewforum.php?cid=1&sid=0&gid=0&gradebook=0&origin=&gid=0&forum=3"),
            ("28_forum_4_zona_exploracion", "Foro: 🔥 Zona de Exploración — Reflexión colectiva", "https://chamilo.educa.website/main/forum/viewforum.php?cid=1&sid=0&gid=0&gradebook=0&origin=&gid=0&forum=4"),
            ("29_forum_4_thread_iniciamos_conversacion", "Debate en Foro 4: Iniciamos la conversación aquí", "https://chamilo.educa.website/main/forum/viewthread.php?cid=1&sid=0&gid=0&gradebook=0&origin=&forum=4&thread=1&search="),
            ("30_forum_5_consultas_modulo_2", "Foro de Consultas Módulo 2: El Gran Rediseño", "https://chamilo.educa.website/main/forum/viewforum.php?cid=1&sid=0&gid=0&gradebook=0&origin=&gid=0&forum=5")
        ]

        for key, label, url in forum_pages:
            try:
                await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(2)
                await save_page_snapshot(page, key, label, "Foros de Debate")
            except Exception as e:
                print(f"[Error] Failed to load {url}: {e}")

        # ---------------------------------------------------------
        # 5. Learning Paths (Lecciones) & Every Single Internal Step
        # ---------------------------------------------------------
        print("\n--- 5. Lecciones y Rutas de Aprendizaje Detalladas ---")
        learning_paths = [
            {
                "lp_id": 2,
                "title": "Módulo 0: Primeros pasos: navegación y organización en la virtualidad",
                "prefix": "lp2_mod0",
                "steps": [
                    ("10", "Tutorial Chamilo"),
                    ("11", "Guía para organizar tu recorrido")
                ]
            },
            {
                "lp_id": 1,
                "title": "Módulo 1: Desafiando la sincronía",
                "prefix": "lp1_mod1",
                "steps": [
                    ("2", "Desafiando la sincronía"),
                    ("8", "Microcápsula en formato de texto"),
                    ("3", "Semáforo")
                ]
            },
            {
                "lp_id": 3,
                "title": "Módulo 2: Expedición didáctica",
                "prefix": "lp3_mod2",
                "steps": [
                    ("29", "🗺️📍 La expedición didáctica: Hoja de ruta"),
                    ("35", "Rúbrica evaluativa del módulo"),
                    ("37", "Bitácora del recorrido"),
                    ("15", "Guía de expedición"),
                    ("28", "Equipamiento"),
                    ("26", "¡Es momento de poner a prueba tus ideas! Respondé el Kahoot"),
                    ("25", "Sala de escape"),
                    ("34", "🔥 Zona de Exploración — Reflexión colectiva"),
                    ("31", "🏆 Tarea: El Gran Rediseño")
                ]
            },
            {
                "lp_id": 4,
                "title": "Módulo 6: Fin del recorrido, inicio de nuevos desafíos",
                "prefix": "lp4_mod6",
                "steps": [
                    ("43", "🗺️📍 Hoja de Ruta: El tramo final"),
                    ("39", "⭐ Bienvenidos al cierre"),
                    ("40", "🧩 Revisamos lo aprendido"),
                    ("41", "🛣 Recorremos el camino transitado"),
                    ("42", "🎯 ¡Es tu turno de decidir!")
                ]
            }
        ]

        for lp in learning_paths:
            lp_id = lp["lp_id"]
            lp_title = lp["title"]
            lp_prefix = lp["prefix"]
            print(f"\n>> Procesando {lp_title} (LP ID: {lp_id})...")

            # Main LP View
            lp_url = f"https://chamilo.educa.website/main/lp/lp_controller.php?action=view&cid=1&sid=0&isStudentView=true&lp_id={lp_id}"
            await page.goto(lp_url, wait_until="networkidle")
            await asyncio.sleep(3)
            await save_page_snapshot(page, f"31_{lp_prefix}_main_view", f"{lp_title} (Vista General)", f"Lecciones: LP {lp_id}")

            # Each step inside the LP
            for step_id, step_name in lp["steps"]:
                safe_name = re.sub(r'[^a-zA-Z0-9]', '_', step_name)[:30].strip('_').lower()
                step_key = f"32_{lp_prefix}_step{step_id}_{safe_name}"
                print(f"  -> Cargando paso {step_id}: {step_name}...")

                # Click item in the TOC or execute switch_item
                try:
                    clicked = await page.evaluate(f"""() => {{
                        if (typeof switch_item === 'function') {{
                            const curr = (typeof olms !== 'undefined' && olms.item_id) ? olms.item_id : '0';
                            switch_item(curr, '{step_id}');
                            return true;
                        }}
                        const link = document.querySelector('[onclick*=\"\\'{step_id}\\'\"]');
                        if (link) {{
                            link.click();
                            return true;
                        }}
                        return false;
                    }}""")
                    await asyncio.sleep(3)
                except Exception as ce:
                    print(f"  [Notice] Switch item exception: {ce}")

                await save_page_snapshot(page, step_key, f"{lp_title} - Paso {step_id}: {step_name}", f"Lecciones: LP {lp_id}")

            # LP Statistics Report
            stats_url = f"https://chamilo.educa.website/main/lp/lp_controller.php?action=stats&origin=learnpath&cid=1&sid=0&gid=0&gradebook=0&origin=&lp_id={lp_id}"
            try:
                await page.goto(stats_url, wait_until="networkidle")
                await asyncio.sleep(2)
                await save_page_snapshot(page, f"33_{lp_prefix}_stats", f"{lp_title} - Estadísticas e Informes", f"Lecciones: LP {lp_id}")
            except Exception as se:
                print(f"  [Error] Failed to load stats for LP {lp_id}: {se}")

        await browser.close()

    # ---------------------------------------------------------
    # 6. Save Manifest JSON
    # ---------------------------------------------------------
    manifest_path = os.path.join(DATA_DIR, "lms_backup_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n[Manifest] Saved {len(manifest)} snapshot records to: {manifest_path}")

    # ---------------------------------------------------------
    # 7. Generate Full Markdown Backup Report
    # ---------------------------------------------------------
    report_path = os.path.join(OUTPUT_DIR, "lms_backup_report.md")
    lines = [
        "# Resumen Ejecutivo del Backup Completo de Chamilo LMS",
        "",
        f"- **Fecha y Hora de Extracción:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **LMS URL:** [{LMS_URL}]({LMS_URL})",
        f"- **Usuario Autenticado:** `{USERNAME}`",
        f"- **Total de Pantallas y Recursos Respaldados:** {len(manifest)}",
        f"- **Directorio Local de Almacenamiento:** `{OUTPUT_DIR}`",
        "",
        "---",
        "",
        "## 📑 Índice de Categorías Respaldadas",
        "",
        "1. [Portal General & Perfil de Usuario](#1-portal-general--perfil-de-usuario)",
        "2. [Herramientas Principales del Curso](#2-herramientas-principales-del-curso)",
        "3. [Foros y Debates de Discusión](#3-foros-y-debates-de-discusión)",
        "4. [Rutas de Aprendizaje y Lecciones Detalladas](#4-rutas-de-aprendizaje-y-lecciones-detalladas)",
        "",
        "---",
        ""
    ]

    # Group by category
    categories = {}
    for item in manifest:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    for cat_name, items in categories.items():
        lines.append(f"## 📂 {cat_name}")
        lines.append("")
        lines.append("| Pantalla / Recurso | Enlace Original | Captura PNG | Snapshot HTML | Documento Embebido |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for it in items:
            ss_link = f"[{it['key']}.png](./screenshots/{it['key']}.png)"
            html_link = f"[{it['key']}.html](./html/{it['key']}.html)"
            iframe_link = f"[{it['key']}_doc_iframe.html](./html/{it['key']}_doc_iframe.html)" if "iframe_html" in it else "—"
            lines.append(f"| **{it['label']}** | [URL]({it['url']}) | {ss_link} | {html_link} | {iframe_link} |")
        lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Report] Generated comprehensive report at: {report_path}")
    print(f"=== Backup Completed Successfully! ===")

if __name__ == "__main__":
    asyncio.run(main())
