"""
Canvas Medical Setup Verification Script
Run this after filling in ~/.canvas/credentials.ini to confirm everything works.

Usage: python3 setup/verify_setup.py
"""

import configparser
import sys
import os
import urllib.request
import urllib.parse
import urllib.error
import json

CREDENTIALS_PATH = os.path.expanduser("~/.canvas/credentials.ini")

def check_step(label, success, detail=""):
    status = "✓" if success else "✗"
    print(f"  {status}  {label}")
    if detail:
        print(f"     {detail}")
    return success


def read_credentials():
    print("\n── Step 1: Reading credentials ─────────────────────────────")
    if not os.path.exists(CREDENTIALS_PATH):
        check_step("credentials.ini found", False,
                   f"File not found at {CREDENTIALS_PATH}\n"
                   "     Fix: Copy setup/credentials.ini.template to ~/.canvas/credentials.ini\n"
                   "     and fill in your client_id, client_secret, and sandbox name.")
        return None, None, None

    check_step("credentials.ini found", True, CREDENTIALS_PATH)

    config = configparser.ConfigParser()
    config.read(CREDENTIALS_PATH)

    # Find the default section (is_default = true) or use the first section
    default_section = None
    for section in config.sections():
        if config.get(section, "is_default", fallback="false").lower() == "true":
            default_section = section
            break
    if not default_section and config.sections():
        default_section = config.sections()[0]

    if not default_section:
        check_step("Sandbox section found", False,
                   "credentials.ini has no sections.\n"
                   "     Fix: Add [YOUR-SANDBOX-NAME] as a section header (replace with your actual subdomain).")
        return None, None, None

    check_step("Sandbox section found", True, f"Using section: [{default_section}]")

    client_id = config.get(default_section, "client_id", fallback=None)
    client_secret = config.get(default_section, "client_secret", fallback=None)

    if not client_id or client_id.startswith("PASTE_"):
        check_step("client_id is set", False,
                   "client_id still has the placeholder value.\n"
                   "     Fix: Replace PASTE_YOUR_CLIENT_ID_HERE with your real client_id from Canvas.")
        return None, None, None
    check_step("client_id is set", True, f"{client_id[:8]}{'*' * max(0, len(client_id)-8)}")

    if not client_secret or client_secret.startswith("PASTE_"):
        check_step("client_secret is set", False,
                   "client_secret still has the placeholder value.\n"
                   "     Fix: Replace PASTE_YOUR_CLIENT_SECRET_HERE with your real client_secret from Canvas.")
        return None, None, None
    check_step("client_secret is set", True, "(hidden for security)")

    host = f"https://{default_section}.canvasmedical.com"
    check_step("Canvas URL constructed", True, host)

    return host, client_id, client_secret


def get_oauth_token(host, client_id, client_secret):
    print("\n── Step 2: Getting OAuth token ──────────────────────────────")
    token_url = f"{host}/auth/token/"
    payload = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(token_url, data=payload, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            token = body.get("access_token")
            if not token:
                check_step("OAuth token received", False,
                           f"Response had no access_token. Body: {body}")
                return None
            check_step("OAuth token received", True, "Token obtained (not shown for security)")
            return token
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        check_step("OAuth token received", False,
                   f"HTTP {e.code} from {token_url}\n"
                   f"     Body: {body[:300]}\n"
                   "     Fix: Double-check your client_id and client_secret in credentials.ini.\n"
                   "          Make sure the section name [sandbox-name] matches your Canvas subdomain.")
        return None
    except urllib.error.URLError as e:
        check_step("OAuth token received", False,
                   f"Could not reach {token_url}: {e.reason}\n"
                   "     Fix: Check your internet connection. Confirm your Canvas instance name is correct.")
        return None


def check_patient_api(host, token):
    print("\n── Step 3: Testing FHIR Patient API ─────────────────────────")
    patient_url = f"{host}/api/Patient?_count=1"
    try:
        req = urllib.request.Request(patient_url)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/fhir+json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            total = body.get("total", "unknown")
            check_step("FHIR Patient endpoint accessible", True,
                       f"Found {total} patient(s) in your sandbox")
            return True
    except urllib.error.HTTPError as e:
        check_step("FHIR Patient endpoint accessible", False,
                   f"HTTP {e.code}. Your token works but FHIR access may be restricted.\n"
                   "     This is expected on some Canvas plans — the plugin itself will still work.\n"
                   "     Contact your Canvas rep if you need full FHIR API access.")
        return False
    except urllib.error.URLError as e:
        check_step("FHIR Patient endpoint accessible", False, str(e.reason))
        return False


def main():
    print("=" * 60)
    print("  Canvas Medical Setup Verification")
    print("  Suvida Healthcare — HEDIS Care Gap Plugin")
    print("=" * 60)

    host, client_id, client_secret = read_credentials()
    if not all([host, client_id, client_secret]):
        print("\n✗  Setup incomplete. Fix the issues above and run this script again.")
        sys.exit(1)

    token = get_oauth_token(host, client_id, client_secret)
    if not token:
        print("\n✗  Could not authenticate. Fix the issues above and run this script again.")
        sys.exit(1)

    fhir_ok = check_patient_api(host, token)

    print("\n" + "=" * 60)
    if fhir_ok:
        print("  ✓  All checks passed! Your Canvas sandbox is ready.")
        print(f"     Instance: {host}")
        print("     Next step: Tell Claude to deploy the HEDIS plugin.")
    else:
        print("  ✓  Authentication works. FHIR access may be limited.")
        print(f"     Instance: {host}")
        print("     Your plugin will still work for note/chart events.")
        print("     Contact Canvas if you need full FHIR read access.")
    print("=" * 60)


if __name__ == "__main__":
    main()
