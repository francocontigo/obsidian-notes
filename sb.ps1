<#
.SYNOPSIS
  Second Brain automation for Windows (PowerShell). Mirror of the Makefile.
  Thin wrappers around the Claude Code CLI in headless mode.

.DESCRIPTION
  Requires the `claude` CLI on PATH (https://docs.claude.com/claude-code).
  --permission-mode acceptEdits lets Claude write wiki files without prompting.

.EXAMPLE
  ./sb.ps1 ingest "1 Books&Courses/Descomplicando SQL.md"
  ./sb.ps1 ingest "https://example.com/article"
  ./sb.ps1 process-inbox
  ./sb.ps1 query "what do my notes say about big-o for linked lists?"
  ./sb.ps1 lint
  ./sb.ps1 capture "a fleeting thought"
  ./sb.ps1 ui
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('ingest', 'process-inbox', 'query', 'lint', 'capture', 'study', 'explain', 'gaps', 'ui', 'help')]
    [string]$Command,

    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = 'Stop'
$Claude = if ($env:CLAUDE) { $env:CLAUDE } else { 'claude' }
$Perm   = @('--permission-mode', 'acceptEdits')
$Arg    = ($Rest -join ' ')
# Run from the vault root (this script's folder) so vault-relative paths resolve.
Set-Location -Path $PSScriptRoot

switch ($Command) {
    'ingest' {
        if (-not $Arg) { throw 'Usage: ./sb.ps1 ingest "path-or-URL"' }
        & $Claude -p "/ingest $Arg" @Perm
    }
    'process-inbox' { & $Claude -p '/process-inbox' @Perm }
    'query' {
        if (-not $Arg) { throw 'Usage: ./sb.ps1 query "your question"' }
        & $Claude -p "/query $Arg" @Perm
    }
    'lint' { & $Claude -p '/lint' @Perm }
    'capture' {
        if (-not $Arg) { throw 'Usage: ./sb.ps1 capture "a thought"' }
        $inbox = Join-Path $PSScriptRoot 'raw/inbox.md'
        $old = Get-Content -Path $inbox -Raw
        Set-Content -Path $inbox -Value ("$Arg`n$old") -NoNewline
        Write-Host 'Captured to raw/inbox.md'
    }
    # Interactive: open a live Claude session so it can ask you questions.
    'study'   { & $Claude "/study $Arg" @Perm }
    'explain' {
        if (-not $Arg) { throw 'Usage: ./sb.ps1 explain "a concept"' }
        & $Claude "/explain $Arg" @Perm
    }
    'gaps'    { & $Claude -p '/gaps' @Perm }
    'ui'   { streamlit run app/app.py }
    'help' {
        Write-Host 'Second Brain commands:'
        Write-Host '  ./sb.ps1 ingest "path-or-URL"   Ingest one source into the wiki'
        Write-Host '  ./sb.ps1 process-inbox          Triage raw/inbox.md into the wiki'
        Write-Host '  ./sb.ps1 query "question"       Ask the wiki; answer saved to output/'
        Write-Host '  ./sb.ps1 lint                   Health-check the wiki'
        Write-Host '  ./sb.ps1 capture "a thought"    Append a line to raw/inbox.md (no LLM)'
        Write-Host '  -- learning --'
        Write-Host '  ./sb.ps1 study [N]              Spaced-repetition session (interactive)'
        Write-Host '  ./sb.ps1 explain "a concept"    Feynman mode (interactive)'
        Write-Host '  ./sb.ps1 gaps                   Learning health check -> output/study-plan.md'
        Write-Host '  ./sb.ps1 ui                     Launch the Streamlit interface'
    }
}
