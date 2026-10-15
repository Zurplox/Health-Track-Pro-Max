# Project handoff

## Current state

This workspace is being converted from a single-owner Garmin dashboard into a
public-safe self-hosted template for **Health Track Pro Max**.

- `data/demo.json` is deterministic synthetic data.
- The former encrypted owner vault has been removed.
- `index.html` defaults to passwordless demo mode and has no embedded GitHub
  token or owner-pinned repository.
- Live forks use private `GARMIN_TOKENS` and `GARMIN_DASHBOARD_PASS` Actions
  secrets. The workflow refuses missing secrets.
- The relay is configurable per fork and has no original repository/origin
  fallback.

## Ownership rules

`bio_policy.py` owns thresholds and bands; `bio_analytics.py` owns arithmetic;
`garmin_source.py` is the only Garmin I/O module; `clinical_engine.py` owns
deterministic verdicts and optional narrative; `sync.py` orchestrates;
`encrypt_data.py` encrypts live output; and `index.html` renders resolved data.

## Local checks

```bash
python -m unittest discover -s tests -t . -v
node tests/check_frontend_syntax.mjs index.html
node tests/check_relay.mjs
python -m py_compile *.py
```

## Next step

Review the sanitized local result. Only after approval should a separate task
create and push the new GitHub repository named **Health Track Pro Max**.
