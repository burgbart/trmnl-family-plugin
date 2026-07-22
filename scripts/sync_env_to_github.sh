#!/usr/bin/env bash
# Push local .env values to the GitHub repo's Actions secrets/variables so
# .github/workflows/generate-dashboard.yml has what it needs to run.
#
# Only pushes the keys that workflow actually consumes (see the `env:`
# blocks in generate-dashboard.yml), split the same way the workflow reads
# them: non-sensitive config as Actions Variables, credentials as Secrets.
#
# Usage:
#   scripts/sync_env_to_github.sh              # push everything found in .env
#   scripts/sync_env_to_github.sh --dry-run    # show what would be set, no writes
#   scripts/sync_env_to_github.sh path/to/.env # use a different env file
#
# Requires: gh CLI, authenticated (`gh auth status`) with access to this repo.

set -euo pipefail

DRY_RUN=false
ENV_FILE=".env"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    *) ENV_FILE="$arg" ;;
  esac
done

if [ ! -f "$ENV_FILE" ]; then
  echo "Env file not found: $ENV_FILE" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found on PATH." >&2
  exit 1
fi

# Keys generate-dashboard.yml reads as ${{ vars.NAME }}.
VAR_KEYS="
WEATHER_LATITUDE
WEATHER_LONGITUDE
CITY
TIMEZONE
GOOGLE_CALENDAR_IDS
CALENDAR_ATTENDEE_EMAILS
CALENDAR_MAIN_CALENDAR_ID
TICKTICK_LIST_ID
CLOUDFLARE_R2_BUCKET_NAME
CLOUDFLARE_R2_PUBLIC_URL
"

# Keys generate-dashboard.yml reads as ${{ secrets.NAME }}.
SECRET_KEYS="
GOOGLE_SERVICE_ACCOUNT_JSON
TICKTICK_ACCESS_TOKEN
CLOUDFLARE_R2_ENDPOINT
CLOUDFLARE_R2_ACCESS_KEY_ID
CLOUDFLARE_R2_SECRET_ACCESS_KEY
"

# Keys src/config.py defaults if unset — fall back explicitly rather than
# pushing an empty Actions variable, which would override the Python default
# with an empty string (unset vars.NAME renders as "" too, but an empty
# TIMEZONE breaks ZoneInfo, so we'd rather push a real value).
default_for() {
  case "$1" in
    WEATHER_LATITUDE) echo "52.3676" ;;
    WEATHER_LONGITUDE) echo "4.9041" ;;
    CITY) echo "Amsterdam" ;;
    TIMEZONE) echo "Europe/Amsterdam" ;;
    *) echo "" ;;
  esac
}

# Look up KEY's value in ENV_FILE. Handles `KEY=value`, `KEY="value"`, and
# `KEY='value'` on a single line (sufficient for this project's .env, which
# has no multi-line values). Strips one matching layer of surrounding quotes.
lookup() {
  local key="$1" line value
  line=$(grep -E "^${key}=" "$ENV_FILE" | tail -n1 || true)
  [ -z "$line" ] && return 0
  value="${line#${key}=}"
  if [[ "$value" == \"*\" && "$value" == *\" ]]; then
    value="${value#\"}"; value="${value%\"}"
  elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
    value="${value#\'}"; value="${value%\'}"
  fi
  printf '%s' "$value"
}

set_one() {
  local kind="$1" key="$2" value="$3"
  if [ -z "$value" ]; then
    value=$(default_for "$key")
    if [ -z "$value" ]; then
      echo "skip   $key (empty in $ENV_FILE, no default)"
      return
    fi
    echo "note   $key not set in $ENV_FILE — using default '$value'"
  fi

  if [ "$DRY_RUN" = true ]; then
    echo "would set $kind $key (${#value} chars)"
    return
  fi

  if [ "$kind" = "secret" ]; then
    gh secret set "$key" --body "$value" >/dev/null
  else
    gh variable set "$key" --body "$value" >/dev/null
  fi
  echo "set    $kind $key"
}

echo "Syncing from $ENV_FILE to GitHub repo $(gh repo view --json nameWithOwner -q .nameWithOwner)..."
$DRY_RUN && echo "(dry run — no changes will be made)"
echo

for key in $VAR_KEYS; do
  set_one "variable" "$key" "$(lookup "$key")"
done

for key in $SECRET_KEYS; do
  set_one "secret" "$key" "$(lookup "$key")"
done

echo
echo "Done. Verify with: gh secret list && gh variable list"
