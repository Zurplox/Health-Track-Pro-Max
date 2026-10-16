# Health Track Pro Max

Public-safe Garmin dashboard template with a passwordless synthetic demo.

## Demo

```bash
python -m http.server 8971 --bind 127.0.0.1
```

Open `http://127.0.0.1:8971`. Demo data is synthetic and stored in
`data/demo.json`; it is not connected to Garmin.

## Private Garmin deployment

Use one fork per user:

1. Install dependencies: `pip install garminconnect cryptography`
2. Run `python verify_garmin.py` locally.
3. Add the generated session-token JSON as the private Actions secret
   `GARMIN_TOKENS`.
4. Add a private `GARMIN_DASHBOARD_PASS` secret.
5. Set `DEMO_MODE` to `false` and enable GitHub Pages/Actions.

Garmin credentials stay on the local machine or Actions runner. Missing secrets
fail safely; no fallback passwords or tokens exist.

## Privacy

- The public payload is synthetic only.
- Personal plaintext data and Garmin caches are ignored.
- Live encrypted data is generated only in a user's private fork.
- Published history is limited to the latest 60 days; older data is not archived
  into the public repository.
- Never commit passwords, tokens, session files, or health exports.

## Checks

```bash
python -m unittest discover -s tests -t .
node tests/check_frontend_syntax.mjs index.html
node tests/check_relay.mjs
python -m py_compile *.py
```
