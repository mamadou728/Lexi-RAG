# Run from backend/ so "src" is on Python path. Use from project root: .\backend\run.ps1
# Or: cd backend; .\run.ps1
Set-Location $PSScriptRoot
uvicorn src.main:app --reload
