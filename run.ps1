param(
    [string]$Env = "default.yaml",
    [string]$Suite = "testcases/bstackdemo_e2e.robot",
    [string]$OutputDir = "results"
)

Write-Host "Running Robot Framework with Environment Config: $Env" -ForegroundColor Cyan
Write-Host "Target Suite: $Suite" -ForegroundColor Cyan

& ".\.venv\Scripts\python.exe" -m robot --outputdir $OutputDir --prerunmodifier "resources/keywords/custom-libs/DataLoader.py:$Env" $Suite
