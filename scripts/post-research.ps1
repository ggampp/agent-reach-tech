#Requires -Version 5.1
param(
    [Parameter(Mandatory = $true)][string]$Topic,
    [Parameter(Mandatory = $true)][ValidateSet("adotar", "observar", "evitar")][string]$Verdict,
    [string]$Summary = "",
    [string]$Reason = "",
    [string]$EvidenceFile = ""
)

$payload = @{
    topic    = $Topic
    summary  = $Summary
    verdict  = $Verdict
    reason   = $Reason
    evidence = @()
}

if ($EvidenceFile -and (Test-Path $EvidenceFile)) {
    $raw = Get-Content $EvidenceFile -Raw | ConvertFrom-Json
    if ($raw.evidence) { $payload.evidence = $raw.evidence }
}

$tmp = [System.IO.Path]::GetTempFileName()
try {
    $payload | ConvertTo-Json -Depth 6 | Set-Content -Path $tmp -Encoding utf8
    agent-reach-tech format --file $tmp
}
finally {
    if (Test-Path $tmp) { Remove-Item $tmp -Force }
}