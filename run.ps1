param(
    [string]$Env = "default.yaml",
    [string]$Suite = "testcases/bstackdemo_e2e.robot",
    [string]$OutputDir = "results",
    [switch]$DryRun
)

$dryRunArgs = @()
if ($DryRun) {
    Write-Host "[DRY-RUN] Executing sandbox syntax validation (no browser launched)..." -ForegroundColor Yellow
    $dryRunArgs = @("--dryrun")
}

Write-Host "Running Robot Framework with Environment Config: $Env" -ForegroundColor Cyan
Write-Host "Target Suite: $Suite" -ForegroundColor Cyan

& ".\.venv\Scripts\python.exe" -m robot @dryRunArgs --outputdir $OutputDir --prerunmodifier "resources/keywords/custom-libs/DataLoader.py:$Env" $Suite
