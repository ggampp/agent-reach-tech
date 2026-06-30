#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

Write-Host ""
Write-Host "Agent Reach Tech v1.0 — Instalacao" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] agent-reach-tech install --env=auto" -ForegroundColor Yellow
agent-reach-tech install --env=auto
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
Write-Host "[2/2] Diagnostico" -ForegroundColor Yellow
agent-reach-tech doctor

Write-Host ""
Write-Host "Pronto. Diga ao agent:" -ForegroundColor Green
Write-Host "  Use o skill Agent Reach Tech para pesquisar [topico]"
Write-Host ""