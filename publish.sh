#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Publish the Pakistan Evidence Catalogue to GitHub.
#
# Safe to run repeatedly: the first run creates the repository and pushes,
# every later run just commits and pushes whatever changed.
#
#   ./publish.sh                      # commit with an automatic message
#   ./publish.sh "Fix P35 dates"      # commit with your own message
#
# Set these once, or export them in your shell instead.
# ---------------------------------------------------------------------------
set -euo pipefail

GITHUB_USER="${GITHUB_USER:-itssaqib}"
REPO_NAME="${REPO_NAME:-pakistan-evidence-catalogue}"
BRANCH="${BRANCH:-main}"

cd "$(dirname "$0")"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m!  \033[0m %s\n' "$1"; }
die()  { printf '\033[1;31mx  \033[0m %s\n' "$1" >&2; exit 1; }

command -v git >/dev/null 2>&1 || die "git is not installed. Install it from https://git-scm.com"

# --- sanity check: are we in the right folder? ------------------------------
[ -f index.html ] || die "index.html is not in this folder. Run this from the folder that contains index.html, not its parent."

# --- identity ---------------------------------------------------------------
if [ -z "$(git config --global user.email || true)" ]; then
  warn "git has no global user.email set."
  read -rp "    Email for commits: " GIT_EMAIL
  read -rp "    Name for commits:  " GIT_NAME
  git config --global user.email "$GIT_EMAIL"
  git config --global user.name  "$GIT_NAME"
fi

# --- repo ---------------------------------------------------------------------
if [ ! -d .git ]; then
  say "Initialising a new repository on branch '$BRANCH'"
  git init -b "$BRANCH" >/dev/null
else
  say "Repository already initialised"
  git symbolic-ref -q HEAD >/dev/null || git checkout -b "$BRANCH" >/dev/null 2>&1 || true
fi

# --- stage and commit ----------------------------------------------------------
git add -A
if git diff --cached --quiet; then
  say "No changes to commit"
else
  MSG="${1:-Update catalogue — $(date '+%Y-%m-%d %H:%M')}"
  say "Committing: $MSG"
  git commit -q -m "$MSG"
fi

# --- remote --------------------------------------------------------------------
if ! git remote get-url origin >/dev/null 2>&1; then
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    say "Creating the repository on GitHub with the gh CLI"
    gh repo create "$REPO_NAME" --public --source=. --remote=origin \
      --description "Staggered district-level programmes in Pakistan for causal impact evaluation"
  else
    warn "No 'origin' remote yet."
    warn "Create an EMPTY repository named '$REPO_NAME' at https://github.com/new"
    warn "(no README, no .gitignore, no licence — this folder already has them)"
    read -rp "    Press Enter once it exists, or Ctrl-C to stop... " _
    git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
    say "Remote set to https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
  fi
fi

# --- push ------------------------------------------------------------------------
say "Pushing to origin/$BRANCH"
git push -u origin "$BRANCH"

cat <<EOF

Done.

  Repository   https://github.com/${GITHUB_USER}/${REPO_NAME}
  Live site    https://${GITHUB_USER}.github.io/${REPO_NAME}/

If this was the first push, switch Pages on once:
  Settings -> Pages -> Source: "Deploy from a branch"
                    -> Branch: ${BRANCH} / (root) -> Save

The site appears about a minute later.
EOF
