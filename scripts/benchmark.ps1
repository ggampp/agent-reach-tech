#Requires -Version 5.1
$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "Agent Reach Tech — Benchmark (probe latency)" -ForegroundColor Cyan
Write-Host ""

$channels = @(
    @{ name = "hackernews"; cmd = "agent-reach-tech hn front-page --limit 1" },
    @{ name = "github"; cmd = "agent-reach-tech github repo Gentleman-Programming/engram" },
    @{ name = "web"; cmd = "agent-reach-tech web https://example.com --raw" },
    @{ name = "rss"; cmd = "agent-reach-tech rss read https://hnrss.org/frontpage --limit 1" },
    @{ name = "cve"; cmd = "agent-reach-tech cve CVE-2024-3094" },
    @{ name = "catalog"; cmd = "agent-reach-tech catalog search engram --limit 1" }
)

foreach ($ch in $channels) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-Expression $ch.cmd | Out-Null
    $sw.Stop()
    $ms = $sw.ElapsedMilliseconds
    Write-Host ("  {0,-12} {1,6} ms" -f $ch.name, $ms)
}

Write-Host ""