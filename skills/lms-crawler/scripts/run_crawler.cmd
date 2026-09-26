@echo off
REM Windows CMD Launcher for LMS Crawler
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set CRAWLER_MJS=%SCRIPT_DIR%crawl_lms.mjs

if "%~1"=="" (
    echo Usage: run_crawler.cmd ^<url^> ^<username^> ^<password^> [output_dir]
    echo Example: run_crawler.cmd "https://inaconfirmantes.milaulas.com/course/view.php?id=5" "alenieto" "Lte_2026" ".\output"
    exit /b 1
)

set URL=%~1
set USERNAME=%~2
set PASSWORD=%~3
set OUTPUT_DIR=%~4
if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=.\lms_output

node "%CRAWLER_MJS%" --url "%URL%" --user "%USERNAME%" --pass "%PASSWORD%" --out "%OUTPUT_DIR%"
