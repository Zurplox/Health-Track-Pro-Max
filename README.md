# Health Track Pro Max

A public-safe Garmin health dashboard template. The repository contains a
passwordless synthetic demo; it does not contain a person's Garmin credentials,
health data, GitHub token, or vault passphrase.

## Demo

Serve the project root and open `index.html`:

```bash
python -m http.server 8971 --bind 127.0.0.1
```

The page loads `data/demo.json`, labels it **Synthetic demo**, and renders the
same charts, scoring, coaching, and provenance surfaces used by a private live
deployment. Demo values are generated deterministically by `demo_data.py` and
are not connected to Garmin.

## Use with your own Garmin account

This project is designed for one private fork/deployment per user. It is not a
shared multi-user service and does not collect Garmin passwords in the browser.

1. Fork or copy this repository into your own GitHub account.
2. Install the local dependency and authenticate once:

   ```bash
   pip install garminconnect cryptography
   python verify_garmin.py
   ```

   The helper stores session tokens in your local Garmin profile. Never commit
   that directory or its JSON file.
3. Base64-encode the generated token JSON and add it to your fork as the
   private Actions secret `GARMIN_TOKENS`.
4. Add a strong private `GARMIN_DASHBOARD_PASS` Actions secret.
5. Set the frontend `DEMO_MODE` constant to `false` in your private deployment,
   enable the workflow, and configure GitHub Pages for the fork.

The workflow restores the token only on the runner, fetches the linked account,
computes the payload, encrypts it, and commits only ciphertext plus status
metadata. Missing secrets fail the workflow; there are no fallback passwords.

## Refresh and relay

The public template's Refresh button is read-only unless a fork owner configures
their own relay URL. Do not add a GitHub token to the page. If you deploy
`relay/`, configure its private `GITHUB_TOKEN`, `REPO`, and exact
`ALLOWED_ORIGIN` values as Worker secrets/variables, then set the fork's
`SYNC_RELAY_URL`. The relay never handles Garmin credentials.

## Data and privacy

- `data/demo.json` is the only committed dashboard payload and is synthetic.
- `data/biometrics.json` and Garmin caches are ignored.
- `data/biometrics.enc.json` is generated only by a configured private fork.
- `encrypt_data.py` refuses to run without `GARMIN_DASHBOARD_PASS`.
- Do not put passwords, tokens, session files, or personal health exports in
  issues, pull requests, documentation, or commits.

## Checks

```bash
python -m unittest discover -s tests -t . -v
node tests/check_frontend_syntax.mjs index.html
node tests/check_relay.mjs
python -m py_compile *.py
python -c "import json; json.load(open('data/demo.json', encoding='utf-8'))"
```

The future GitHub repository can be named **Health Track Pro Max** after this
local template has been reviewed. Repository creation and pushing are separate
from this code/data sanitization pass.
