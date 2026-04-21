#!/usr/bin/env bash
# Deploys the hedis_care_gaps plugin to a Canvas Medical sandbox.
# Usage:
#   ./setup/deploy.sh                          (interactive prompts)
#   ./setup/deploy.sh INSTANCE CLIENT_ID SECRET (non-interactive)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CREDS_DIR="$HOME/.canvas"
CREDS_FILE="$CREDS_DIR/credentials.ini"

# ── 1. Collect credentials ─────────────────────────────────────────────────

if [[ $# -ge 3 ]]; then
  INSTANCE_NAME="$1"
  CLIENT_ID="$2"
  CLIENT_SECRET="$3"
else
  echo ""
  echo "=== Canvas Sandbox Deployment ==="
  echo ""
  read -rp "Instance name (subdomain, e.g. suvida-dev): " INSTANCE_NAME
  read -rp "Client ID: " CLIENT_ID
  read -rsp "Client Secret (hidden): " CLIENT_SECRET
  echo ""
fi

if [[ -z "$INSTANCE_NAME" || -z "$CLIENT_ID" || -z "$CLIENT_SECRET" ]]; then
  echo "ERROR: instance name, client_id, and client_secret are all required." >&2
  exit 1
fi

# ── 2. Write ~/.canvas/credentials.ini ────────────────────────────────────

mkdir -p "$CREDS_DIR"
chmod 700 "$CREDS_DIR"

cat > "$CREDS_FILE" <<EOF
[$INSTANCE_NAME]
client_id = $CLIENT_ID
client_secret = $CLIENT_SECRET
is_default = true
EOF

chmod 600 "$CREDS_FILE"
echo "✓ Credentials written to $CREDS_FILE"

# ── 3. Verify connectivity ─────────────────────────────────────────────────

echo ""
echo "--- Verifying Canvas connection ---"
cd "$REPO_ROOT"
python3 setup/verify_setup.py

# ── 4. Run tests ───────────────────────────────────────────────────────────

echo ""
echo "--- Running plugin tests ---"
python3 -m pytest tests/ -q

# ── 5. Deploy plugin ───────────────────────────────────────────────────────

echo ""
echo "--- Deploying plugin to $INSTANCE_NAME ---"
canvas install --host "$INSTANCE_NAME" "$REPO_ROOT/plugins/hedis_care_gaps"

echo ""
echo "✓ Deployment complete!"
echo "  Open https://$INSTANCE_NAME.canvasmedical.com, find a patient with"
echo "  diabetes or hypertension, check them in — the HEDIS banner should appear."
