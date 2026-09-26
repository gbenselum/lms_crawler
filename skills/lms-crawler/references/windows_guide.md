# Complete Windows Guide: Antigravity LMS Crawler

This guide walks you through setting up and running the LMS Crawler skill on **Microsoft Windows 10 & 11**.

---

## 1. Prerequisites on Windows

### A. Web Browser (Already Installed)
- **Microsoft Edge** is installed by default on Windows 10 and 11.
- Edge is built on the Chromium engine and has native support for the **Chrome DevTools Protocol (CDP)**.
- Alternatively, **Google Chrome** or **Brave** can also be used.
- The crawler will automatically scan:
  - `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
  - `C:\Program Files\Microsoft\Edge\Application\msedge.exe`
  - `C:\Program Files\Google\Chrome\Application\chrome.exe`

### B. Node.js (v18 or higher)
To verify if Node.js is installed, open PowerShell and run:
```powershell
node --version
```
If not installed, install it in seconds using `winget` (Windows Package Manager):
```powershell
winget install OpenJS.NodeJS.LTS
```
*(Restart your terminal or Antigravity after installing).*

---

## 2. Installing the Skill into Antigravity on Windows

Antigravity supports two discovery locations on Windows:

### Option A: Global Skill (Available in all Windows projects)
Copy the `skills\lms-crawler` folder to your user's global Gemini directory:
```powershell
# In PowerShell:
$target = "$env:USERPROFILE\.gemini\config\skills\lms-crawler"
New-Item -ItemType Directory -Force -Path $target
Copy-Item -Recurse -Force ".\skills\lms-crawler\*" $target
```

### Option B: Workspace Skill (Project-specific)
If you have an active workspace project in Antigravity:
```text
C:\Users\YourUser\MyProject\
├── .agents\
│   └── skills\
│       └── lms-crawler\
│           ├── SKILL.md
│           ├── scripts\
│           └── references\
```
Antigravity automatically indexes any skill inside `.agents\skills\` upon starting.

---

## 3. Running the Prompt in Antigravity on Windows

Once installed, you can simply type your request into Antigravity on Windows:

> *"Could you check this LMS and get me some screenshots? Here are the credentials https://inaconfirmantes.milaulas.com/course/view.php?id=5 usuario: alenieto password: Lte_2026"*

### What happens behind the scenes:
1. Antigravity activates the `lms-crawler` skill based on the intent (LMS URL + credentials + screenshots request).
2. It launches `crawl_lms.mjs` via `run_command` in headless mode.
3. Edge/Chrome launches in the background using an isolated temporary user data profile.
4. The script logs in, traverses the course syllabus, captures high-resolution screenshots, and saves everything to disk.
5. Antigravity displays the final report and embedded images directly in your chat or artifact viewer.

---

## 4. Running Standalone via Terminal on Windows

You can also run the crawler directly in Windows PowerShell or Command Prompt outside Antigravity:

### Using PowerShell:
```powershell
node .\skills\lms-crawler\scripts\crawl_lms.mjs `
  --url "https://inaconfirmantes.milaulas.com/course/view.php?id=5" `
  --user "alenieto" `
  --pass "Lte_2026" `
  --out ".\output"
```
Or using the PowerShell launcher:
```powershell
.\skills\lms-crawler\scripts\run_crawler.ps1 `
  -Url "https://inaconfirmantes.milaulas.com/course/view.php?id=5" `
  -Username "alenieto" `
  -Password "Lte_2026" `
  -OutputDir ".\output"
```

### Using Command Prompt (CMD):
```cmd
skills\lms-crawler\scripts\run_crawler.cmd "https://inaconfirmantes.milaulas.com/course/view.php?id=5" "alenieto" "Lte_2026" ".\output"
```

---

## 5. Troubleshooting on Windows

### Issue 1: PowerShell Script Execution Policy
If PowerShell blocks `.ps1` scripts, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Issue 2: Custom Browser Path
If your browser is installed in a non-standard directory, specify it before running:
```powershell
$env:CHROME_PATH = "D:\CustomApps\Chrome\chrome.exe"
```

### Issue 3: Port Conflict (9222 in use)
If port 9222 is used by another service, pass a custom port:
```powershell
node .\skills\lms-crawler\scripts\crawl_lms.mjs --url "..." --user "..." --pass "..." --port 9230
```
