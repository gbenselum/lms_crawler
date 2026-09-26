<#
.SYNOPSIS
    Cross-platform LMS Crawler launcher for Windows (PowerShell).
.EXAMPLE
    .\run_crawler.ps1 -Url "https://inaconfirmantes.milaulas.com/course/view.php?id=5" -Username "alenieto" -Password "Lte_2026" -OutputDir ".\output"
#>
param (
    [Parameter(Mandatory=$true)]
    [string]$Url,

    [Parameter(Mandatory=$true)]
    [string]$Username,

    [Parameter(Mandatory=$true)]
    [string]$Password,

    [Parameter(Mandatory=$false)]
    [string]$OutputDir = ".\lms_output",

    [Parameter(Mandatory=$false)]
    [int]$Port = 9222
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$crawlerScript = Join-Path $scriptDir "crawl_lms.mjs"

# Verify Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js (v18+) is required to run this script. Please install it from https://nodejs.org/"
    exit 1
}

Write-Host "Starting LMS Crawler with Node.js on Windows..." -ForegroundColor Cyan
Write-Host "Target: $Url" -ForegroundColor Yellow
Write-Host "User:   $Username" -ForegroundColor Yellow
Write-Host "Output: $OutputDir" -ForegroundColor Yellow

node "$crawlerScript" --url "$Url" --user "$Username" --pass "$Password" --out "$OutputDir" --port $Port
