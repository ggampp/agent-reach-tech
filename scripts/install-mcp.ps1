#Requires -Version 5.1
param(
    [string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent | Split-Path -Parent),
    [switch]$DryRun
)

$args = @("-m", "agent_reach_tech.core.mcp_install", "--project", $ProjectRoot)
if ($DryRun) { $args += "--dry-run" }

Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    python @args
    if (-not $DryRun) {
        Write-Host ""
        Write-Host "Validate MCP server:"
        python -c @"
import asyncio, json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command='agent-reach-tech', args=['mcp'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print('OK:', len(tools.tools), 'tools')

asyncio.run(main())
"@
        Write-Host ""
        Write-Host "Restart Cursor / Claude / Grok / Codex to load MCP."
    }
}
finally {
    Pop-Location
}