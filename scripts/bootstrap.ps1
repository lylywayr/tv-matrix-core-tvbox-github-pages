param(
  [Parameter(Mandatory=$true)][string]$RemoteUrl,
  [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is required. Install Git for Windows and ensure git is on PATH."
}

if (-not (Test-Path ".git")) {
  git init
}

git branch -M $Branch

$existing = git remote 2>$null
if ($existing -notcontains "origin") {
  git remote add origin $RemoteUrl
}

git add .
git commit -m "chore: initialize tv matrix core" 2>$null
git push -u origin $Branch

if (Get-Command gh -ErrorAction SilentlyContinue) {
  gh repo edit --enable-pages --source "public"
  Write-Host "GitHub Pages enable command submitted."
} else {
  Write-Host "Install GitHub CLI and run: gh repo edit --enable-pages --source public"
}
