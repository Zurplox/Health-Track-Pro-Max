# Project memory

- Public-template direction approved: one self-hosted fork per Garmin user; no shared backend.
- Demo mode is passwordless and loads deterministic synthetic `data/demo.json`.
- Live mode remains encrypted and requires the user's private `GARMIN_DASHBOARD_PASS`; no fallback password.
- Garmin session tokens stay in local storage/Actions secrets and never enter browser code or committed files.
- The former owner-specific encrypted vault and owner-specific identity/docs were removed.
- Future step, after user review: create/push the separate `Health Track Pro Max` GitHub repository.
