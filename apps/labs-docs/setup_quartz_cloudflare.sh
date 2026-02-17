#!/usr/bin/env bash
set -euo pipefail

# ====== EDIT ======
export GH_USER="${GH_USER:-wilfried-lafaye}"
export REPO="${REPO:-llm-devops-aws}"
export PROJ="${PROJ:-llm-devops-aws-pages}"
export DOMAIN="${DOMAIN:-CHANGE_ME_DOMAIN}"                 # optional custom domain
export EMAIL_DOMAIN="${EMAIL_DOMAIN:-esiee.fr,edu.esiee.fr}" # comma-separated
export ACCESS_APP_NAME="${ACCESS_APP_NAME:-llm-devops-website}"
export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-CHANGE_ME_CF_ACCOUNT_ID}"
export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-REPLACE_WITH_API_TOKEN}" # set or export before run
export CF_ACCOUNT_ID="${CF_ACCOUNT_ID:-$CLOUDFLARE_ACCOUNT_ID}"
export CF_API_TOKEN="${CF_API_TOKEN:-$CLOUDFLARE_API_TOKEN}"

# ====== PATHS ======
export SITE_DIR="${SITE_DIR:-$PWD}"
export ROOT="${ROOT:-$PWD}"
export DEVOPS_CONTENT_DIR="$ROOT/devops/devops-content"  # markdown/static content for devops track
export UPM_CONTENT_DIR="$ROOT/devops/upm-content"        # markdown/static content for upm track

# Optional: load Cloudflare/GitHub secrets from .env-style files (kept out of git)
for env_file in "$HOME/.devops-website.env" "$ROOT/.env" "$ROOT/.env.cloudflare"; do
  if [ -f "$env_file" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$env_file"
    set +a
  fi
done

if [ "$CLOUDFLARE_API_TOKEN" = "REPLACE_WITH_API_TOKEN" ]; then
  echo "Set CLOUDFLARE_API_TOKEN before running." >&2; exit 1
fi

CF_API_BASE="https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID"
ACCESS_HOST="$PROJ.pages.dev"
[[ -n "$DOMAIN" && "$DOMAIN" != CHANGE_ME_DOMAIN ]] && ACCESS_HOST="$DOMAIN"

has(){ command -v "$1" >/dev/null 2>&1; }
log_step(){ printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$1"; }

quartz_degit_clone(){
  tmpdir=$(mktemp -d)
  echo " - Fallback: cloning Quartz template" >&2
  if git clone --depth 1 --branch v4 https://github.com/jackyzha0/quartz.git "$tmpdir/quartz" >/dev/null 2>&1; then
    rm -rf "$tmpdir/quartz/.git"; cp -a "$tmpdir/quartz"/. .; rm -rf "$tmpdir"; return 0
  fi
  rm -rf "$tmpdir"; return 1
}

write_index_from_readme(){
  local tmp=$(mktemp)
  # If README.md exists, wrap it with Quartz frontmatter for the home page.
  if [ -f "$ROOT/README.md" ]; then
    cat "$ROOT/README.md" > "$tmp"
  else
    printf '# Welcome\n' > "$tmp"
  fi
  {
    printf '%s\n' '---'
    printf '%s\n' 'title: Home'
    printf '%s\n' 'publish: true'
    printf '%s\n' '---'
    cat "$tmp"
  } > content/index.md
  rm -f "$tmp"
}

# ====== ENSURE Assets() EMITTER IS ENABLED IN quartz.config.ts ======
ensure_assets_emitter() {
  local cfg="$SITE_DIR/quartz.config.ts"
  [ -f "$cfg" ] || return 0

  # already present? bail
  grep -q 'Assets[[:space:]]*(' "$cfg" && return 0

  cp "$cfg" "$cfg.bak.assets"

  # 1) add import if missing
  grep -q 'plugins/emitters/assets' "$cfg" || \
    sed -i '1i import { Assets } from "./quartz/plugins/emitters/assets"' "$cfg"

  # 2) register Assets() as first entry in **emitters** array
  awk '
    BEGIN{inEmit=0; injected=0}
    /emitters:[[:space:]]*\[/ && !injected { print; print "    Assets(),"; injected=1; next }
    { print }
  ' "$cfg" > "$cfg.tmp" && mv "$cfg.tmp" "$cfg"

  echo "Patched Assets() into quartz.config.ts"
}

# Copy a content directory into the Quartz content tree under a given prefix.
sync_content_dir() {
  local src="$1" prefix="$2"
  [ -d "$src" ] || return 0
  find "$src" -type f -print0 | while IFS= read -r -d '' f; do
    rel="${f#"$src/"}"
    dest="$SITE_DIR/content/$prefix/$rel"
    mkdir -p "$(dirname "$dest")"
    cp -f "$f" "$dest"
  done
}

# -----------------------------------------------------------------------

# ====== 0) BASE TOOLS ======
log_step "0) Checking base tools"; for t in git curl jq; do has "$t" || { echo "Missing $t"; exit 1; }; done

# ====== 1) NODE 22 + NPM via NVM ======
log_step "1) Ensuring Node.js 22 via nvm"
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  # shellcheck disable=SC1090
  . "$NVM_DIR/nvm.sh"
  nvm use default >/dev/null || true
  nvm install 22
  nvm alias default 22
  nvm use 22
else
  if command -v node >/dev/null; then
    echo "Using system node $(node -v)"
  else
    echo "nvm missing at $NVM_DIR; install nvm first." >&2
    exit 1
  fi
fi
node -v; npm -v

# ====== 2) GH CLI, WRANGLER, NBCONVERT ======
log_step "2) Installing GitHub CLI and Wrangler"
if ! has gh; then
  if has apt-get; then sudo apt-get update && sudo apt-get install -y gh jq; else echo "Install gh"; exit 1; fi
fi
npm i -g wrangler@latest
if ! has python3; then
  if has apt-get; then sudo apt-get install -y python3 python3-pip; else echo "Install python3"; exit 1; fi
fi

# ====== 3) AUTH ======
log_step "3) Authenticating with GitHub and Cloudflare"
gh auth status || gh auth login
wrangler whoami || wrangler login

# ====== 4) QUARTZ SCAFFOLD ======
log_step "4) Creating or refreshing the Quartz scaffold"
mkdir -p "$SITE_DIR"; cd "$SITE_DIR"
quartz_create(){ [ -d content ] && return 0; quartz_degit_clone; }
quartz_create
npm install

# ensure non-MD assets under content/ are emitted
ensure_assets_emitter

# ====== 5) SITE SKELETON ======
log_step "5) Creating base content structure"
# hard-clean stale output and any prior content
# rm -rf "$SITE_DIR/public" "$SITE_DIR/quartz/static/nb" "$SITE_DIR/content/devops" "$SITE_DIR/content/upm" "$SITE_DIR/content/DE1" "$SITE_DIR/content/nb"
mkdir -p "$SITE_DIR/content" "$SITE_DIR/quartz/static/img"
# Copy images to quartz/static/img (Static plugin serves static/ at /static/)
[ -d "$ROOT/static/img" ] && cp -a "$ROOT/static/img/." "$SITE_DIR/quartz/static/img/" || true
# write_index_from_readme
sync_all_content(){
  # sync_content_dir "$DEVOPS_CONTENT_DIR" "devops"
  # sync_content_dir "$UPM_CONTENT_DIR" "upm"
  :
}
sync_all_content

# Keep Assets emitter enabled (for any non-MD assets placed in content/)
ensure_assets_emitter

# ====== 6) BUILD SITE LOCALLY ======
log_step "6) Building Quartz site locally"
npx quartz build

# ====== 7) GITHUB (PRIVATE) ======
log_step "7) Initialising Git and pushing to GitHub"
git init -b main >/dev/null 2>&1 || true
git add .; git commit -m "Quartz init + static content" || true
if ! git remote | grep -q '^origin$'; then
  gh repo create "$GH_USER/$REPO" --private --source=. --remote=origin --push || true
else
  git push -u origin main || true
fi

# ====== 8) CLOUDFLARE PAGES DEPLOY ======
log_step "8) Deploying to Cloudflare Pages"
project_tmp=$(mktemp)
project_status=$(curl -s -o "$project_tmp" -w "%{http_code}" "$CF_API_BASE/pages/projects/$PROJ" -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json")
case "$project_status" in
  200) echo "Project $PROJ already exists, skipping create" >&2;;
  404) wrangler pages project create "$PROJ" --production-branch main || echo "Warn: wrangler create failed" >&2;;
  *) echo "Warn: verify project (HTTP $project_status): $(cat "$project_tmp")" >&2; wrangler pages project create "$PROJ" --production-branch main || true;;
esac
rm -f "$project_tmp"
wrangler pages deploy ./public --project-name "$PROJ"

# ====== 9) CUSTOM DOMAIN + ACCESS (reusable policy, sane session) ======
log_step "9) Configuring Cloudflare custom domain and reusable Access policy"

# 11.0 Pick the host we will protect
ACCESS_HOST="$PROJ.pages.dev"
if [[ -n "$DOMAIN" && "$DOMAIN" != CHANGE_ME_DOMAIN ]]; then
  ACCESS_HOST="$DOMAIN"
fi
echo "Access host ⇒ $ACCESS_HOST"

# 11.1 Optional: link a custom domain only when you actually set one
if [[ "$ACCESS_HOST" != "$PROJ.pages.dev" ]]; then
  domain_payload=$(jq -n --arg domain "$ACCESS_HOST" '{domain:$domain}')
  tmp=$(mktemp)
  http=$(curl -s -o "$tmp" -w "%{http_code}" -X POST \
    "$CF_API_BASE/pages/projects/$PROJ/domains" \
    -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
    --data "$domain_payload")
  case "$http" in
    200|201) : ;;
    409) echo "Domain $ACCESS_HOST already linked to $PROJ" >&2 ;;
    *)  echo "Warning: domain link failed ($http): $(cat "$tmp")" >&2 ;;
  esac
  rm -f "$tmp"
else
  echo "Skipping domain linking (using default Pages host)."
fi

# 11.2 Build include rules from EMAIL_DOMAIN (comma separated)
include_rules=$(
  jq -n --arg s "$EMAIL_DOMAIN" '
    [ $s
      | split(",")
      | map(gsub("^\\s+|\\s+$";""))
      | map(select(length>0))[]
      | {email_domain:{domain:.}}
    ]'
)

# 11.3 Upsert a reusable policy (account-scoped)
POLICY_NAME="${POLICY_NAME:-course-website-access-policy}"
policy_payload=$(jq -n \
  --arg name "$POLICY_NAME" \
  --arg sd "720h" \
  --argjson include "$include_rules" \
  '{name:$name, decision:"allow", include:$include, session_duration:$sd}')

pol_list=$(mktemp)
curl -s "$CF_API_BASE/access/policies?per_page=100" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" > "$pol_list"

POLICY_ID=$(jq -r --arg name "$POLICY_NAME" '
  ( .result // [] )
  | map(select(type=="object" and (.name // "")==$name))
  | (.[0] | .id) // empty
' "$pol_list")
rm -f "$pol_list"

if [[ -n "$POLICY_ID" ]]; then
  curl -s -X PUT "$CF_API_BASE/access/policies/$POLICY_ID" \
    -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
    --data "$policy_payload" >/dev/null
else
  POLICY_ID=$(
    curl -s -X POST "$CF_API_BASE/access/policies" \
      -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
      --data "$policy_payload" | jq -r '.result.id'
  )
fi
echo "Reusable policy ⇒ $POLICY_ID"

# 11.4 Access application upsert
access_payload=$(jq -n \
  --arg host "$ACCESS_HOST" \
  --arg name "$ACCESS_APP_NAME" \
  --arg sd "720h" \
'{
  name:$name, domain:$host, type:"self_hosted",
  session_duration:$sd, auto_redirect_to_identity:false,
  skip_interstitial:false, http_only_cookie_attribute:true, path_cookie_attribute:true,
  same_site_cookie_attribute:"lax", service_auth_401_redirect:false, options_preflight_bypass:false
}')

app_get=$(mktemp)
curl -s "$CF_API_BASE/access/apps?per_page=100" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" > "$app_get"

# Robust jq: only look at objects; guard missing fields; never index arrays like .domain on non-objects
APP_ID=$(jq -r --arg host "$ACCESS_HOST" --arg name "$ACCESS_APP_NAME" '
  ( .result // [] )
  | map(select(type=="object"))
  | map(select(
      ((.self_hosted_domains // []) | index($host))
      or ((.domain // "") == $host)
      or ((.name   // "") == $name)
    ))
  | (.[0] | .id) // empty
' "$app_get")
rm -f "$app_get"

if [[ -z "$APP_ID" ]]; then
  APP_ID=$(
    curl -s -X POST "$CF_API_BASE/access/apps" \
      -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
      --data "$access_payload" | jq -r '.result.id'
  )
else
  curl -s -X PUT "$CF_API_BASE/access/apps/$APP_ID" \
    -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
    --data "$access_payload" >/dev/null
fi

# 11.5 Remove any legacy app-scoped policies to avoid precedence conflicts
curl -s "$CF_API_BASE/access/apps/$APP_ID/policies?per_page=100" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" |
jq -r '(.result // []) | .[].id' | while read -r PID; do
  [[ -n "$PID" ]] && curl -s -X DELETE "$CF_API_BASE/access/apps/$APP_ID/policies/$PID" \
    -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" >/dev/null
done

# 11.6 Attach exactly one reusable policy with precedence 1
update_payload=$(jq -n --argjson base "$access_payload" --arg pid "$POLICY_ID" '
  $base + {policies:[{id:$pid, precedence:1}]}
')
resp=$(curl -s -o /tmp/appupd -w "%{http_code}" -X PUT \
  "$CF_API_BASE/access/apps/$APP_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
  --data "$update_payload")

if [[ "$resp" != "200" && "$resp" != "201" ]]; then
  echo "Warning: failed to attach reusable policy ($resp): $(cat /tmp/appupd)" >&2
fi
rm -f /tmp/appupd


# ====== 10) FINAL DEPLOY ======
log_step "10) Rebuilding site and publishing final deploy"
# Safety: ensure there are no files >25 MiB under site content.
large_count=$(find "$SITE_DIR/content" -type f -size +25M | wc -l || true)
if [ "${large_count:-0}" -gt 0 ]; then
  log_step "Found $large_count file(s) >25MiB under $SITE_DIR/content — refusing to deploy."
  find "$SITE_DIR/content" -type f -size +25M -exec ls -lh {} \; || true
  echo
  if [ "${FORCE_DEPLOY:-0}" != "1" ]; then
    echo "Aborting deploy. To force deploy anyway (script will remove offending files), set FORCE_DEPLOY=1 and re-run." >&2
    exit 1
  else
    log_step "FORCE_DEPLOY=1 set — removing files >25MiB under $SITE_DIR/content before deploy"
    find "$SITE_DIR/content" -type f -size +25M -print0 | xargs -0 rm -f || true
  fi
else
  log_step "No files >25MiB found under $SITE_DIR/content after pruning — continuing deploy."
fi

npx quartz build
wrangler pages deploy ./public --project-name "$PROJ"

echo "Deployment done at $(date '+%Y-%m-%d %H:%M:%S')  |  Site root: https://$ACCESS_HOST"
