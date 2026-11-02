# ---------------------------------------------------------------------------
# Publish the Pakistan Evidence Catalogue to GitHub. (Windows / PowerShell)
#
# Safe to run repeatedly: the first run creates the repository and pushes,
# every later run just commits and pushes whatever changed.
#
#   .\publish.ps1                     # commit with an automatic message
#   .\publish.ps1 "Fix P35 dates"     # commit with your own message
#
# If PowerShell refuses to run this, allow local scripts once:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# ---------------------------------------------------------------------------
param([string]$Message)

$ErrorActionPreference = 'Stop'

$GithubUser = if ($env:GITHUB_USER) { $env:GITHUB_USER } else { 'itssaqib' }
$RepoName   = if ($env:REPO_NAME)   { $env:REPO_NAME }   else { 'pakistan-evidence-catalogue' }
$Branch     = if ($env:BRANCH)      { $env:BRANCH }      else { 'main' }

Set-Location $PSScriptRoot

function Say  ($m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Warn ($m) { Write-Host "!   $m" -ForegroundColor Yellow }
function Die  ($m) { Write-Host "x   $m" -ForegroundColor Red; exit 1 }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Die "git is not installed. Install it from https://git-scm.com"
}

# --- sanity check: are we in the right folder? ------------------------------
if (-not (Test-Path 'index.html')) {
  Die "index.html is not in this folder. Run this from the folder that contains index.html, not its parent."
}

# --- identity ---------------------------------------------------------------
if (-not (git config --global user.email)) {
  Warn "git has no global user.email set."
  $email = Read-Host "    Email for commits"
  $name  = Read-Host "    Name for commits"
  git config --global user.email $email
  git config --global user.name  $name
}

# --- repo ---------------------------------------------------------------------
if (-not (Test-Path '.git')) {
  Say "Initialising a new repository on branch '$Branch'"
  git init -b $Branch | Out-Null
} else {
  Say "Repository already initialised"
}

# --- stage and commit ----------------------------------------------------------
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
  Say "No changes to commit"
} else {
  if (-not $Message) { $Message = "Update catalogue - $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
  Say "Committing: $Message"
  git commit -q -m $Message
}

# --- remote --------------------------------------------------------------------
git remote get-url origin 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  $ghReady = $false
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh auth status 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $ghReady = $true }
  }
  if ($ghReady) {
    Say "Creating the repository on GitHub with the gh CLI"
    $desc = "Staggered district-level programmes in Pakistan for causal impact evaluation"
    gh repo create $RepoName --public --source=. --remote=origin --description $desc
  } else {
    Warn "No 'origin' remote yet."
    Warn "Create an EMPTY repository named '$RepoName' at https://github.com/new"
    Warn "(no README, no .gitignore, no licence - this folder already has them)"
    Read-Host "    Press Enter once it exists, or Ctrl-C to stop"
    git remote add origin "https://github.com/$GithubUser/$RepoName.git"
    Say "Remote set to https://github.com/$GithubUser/$RepoName.git"
  }
}

# --- push ------------------------------------------------------------------------
Say "Pushing to origin/$Branch"
git push -u origin $Branch

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
Write-Host "  Repository   https://github.com/$GithubUser/$RepoName"
Write-Host "  Live site    https://$GithubUser.github.io/$RepoName/"
Write-Host ""
Write-Host "If this was the first push, switch Pages on once:"
Write-Host "  Settings -> Pages -> Source: ""Deploy from a branch"""
Write-Host "                    -> Branch: $Branch / (root) -> Save"
Write-Host ""
Write-Host "The site appears about a minute later."
