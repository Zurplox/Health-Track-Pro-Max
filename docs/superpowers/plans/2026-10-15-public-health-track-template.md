# Public Health Track Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the current owner's credentials and biometric data, ship a passwordless synthetic demo, and prepare a safe per-user Garmin fork workflow for the future Health Track Pro Max repository.

**Architecture:** Keep the existing Python analytics and encrypted live-vault pipeline. Add an explicit frontend demo mode that loads checked-in synthetic JSON without a passphrase; live forks disable demo mode and use a required Actions-provided vault passphrase. Garmin authentication remains local/runner-side through session tokens, never browser-side.

**Tech Stack:** Python 3.12+, `garminconnect`, `cryptography`, GitHub Actions YAML, vanilla HTML/JavaScript, Web Crypto API, Node.js test scripts, Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-15-public-health-track-template-design.md`

## Global Constraints

- Deployment model is one fork/deployment per user; no shared hosted backend.
- Public demo is passwordless and backed by synthetic JSON data.
- Real deployments require `GARMIN_DASHBOARD_PASS`; no fallback passphrase is allowed.
- `GARMIN_TOKENS` is a private Actions secret and never enters source or browser JavaScript.
- No owner names, handles, URLs, exact personal metric claims, or token/passphrase literals remain in committed source or docs.
- No embedded GitHub sync token or owner-pinned relay/repository remains.
- Preserve analytics, dashboard layout, encryption format, and meaningful tests.
- Do not create or push the future GitHub repository during this implementation.

## Review Focus

- **Demo/live mode boundary:** a demo load must never prompt for or require a passphrase, while live mode must refuse an absent passphrase rather than falling back. Pin in frontend tests and the generated fixture check.
- **Credential removal:** encoded or split values must not be able to reconstruct an owner token or password. Pin with repository scans and source assertions.
- **Missing Actions secrets:** a workflow with no `GARMIN_TOKENS` or `GARMIN_DASHBOARD_PASS` must fail with an actionable message, not publish fallback data. Pin in workflow/source tests.
- **Generic configuration:** empty repository/relay settings must not dispatch to the original owner or send a request to an unknown endpoint. Pin in frontend and relay tests.
- **Synthetic-data clarity:** demo payload identity and status must say it is synthetic/demo and must not retain an owner-specific encrypted vault. Pin in fixture/content tests.

---

### Task 1: Replace owner-specific configuration and browser credential paths

**Files:**
- Modify: `index.html` — title, identity copy, demo/live configuration, vault startup, refresh configuration, footer, and remove master-lock/embedded-token paths.
- Modify: `relay/worker.js` — use request/configuration values that do not default to the original repository or origin.
- Modify: `relay/README.md` — generic per-fork relay instructions with placeholders.
- Test: `tests/test_pipeline.py` — replace owner/token/passphrase assertions with public-template assertions.
- Test: `tests/check_relay.mjs` — use generic test repository/origin values and preserve origin/cooldown/error checks.

**Interfaces:**
- Consumes: `DEMO_MODE`/generic runtime configuration; Task 2 supplies the demo file before final integration verification.
- Produces: a page that loads demo data without unlock, and a live-vault path that only asks for a user-supplied passphrase.

- [ ] **Step 1: Write failing source-contract tests** for generic title/identity, `DEMO_MODE`, no `EMBEDDED_SYNC_TOKEN_*`, no original repo/origin, no hardcoded viewer/master password, and refresh without a configured trigger being read-only.
- [ ] **Step 2: Run the focused source-contract tests** and confirm they fail against the current owner-specific page.
- [ ] **Step 3: Add explicit frontend configuration** near the JavaScript engine: a safe generic demo mode default, empty repository/workflow/relay values, and no token fallback or token-fragment decoder.
- [ ] **Step 4: Implement demo startup** so demo mode fetches `data/demo.json`, marks the page as synthetic in the UI, sets `globalBioData`, and calls the existing renderer without showing the passphrase lock. Keep encrypted-vault unlock available behind live mode.
- [ ] **Step 5: Remove or neutralize owner-only browser paths**: embedded GitHub token constants/decoder, original repository slug, master-lock passphrase/hash/copy, and owner identity in title/header/footer/greeting.
- [ ] **Step 6: Make refresh read-only unless the current fork explicitly configures a relay/token route**, with no original-owner fallback and no request to an empty endpoint.
- [ ] **Step 7: Generalize relay defaults and tests** so the worker has no original repository/origin fallback while keeping its origin gate and cooldown semantics.
- [ ] **Step 8: Run `node tests/check_frontend_syntax.mjs index.html` and the focused source/relay checks**; expected result is parse success and all new public-template assertions passing.

### Task 2: Create and publish deterministic synthetic demo data

**Files:**
- Create: `demo_data.py` — deterministic builder for a clearly synthetic payload using existing analytics/policy shape.
- Create: `data/demo.json` — generated synthetic payload consumed only by demo mode.
- Modify: `.gitignore` — keep real plaintext output ignored while allowing the committed demo fixture.
- Delete: `data/biometrics.enc.json` — the owner-specific encrypted vault must not remain; live forks generate this file after configuring their own secrets.
- Modify: `data/status.json` — generic demo status metadata.
- Test: `tests/test_pipeline.py` — fixture identity/shape/synthetic marker tests.

**Interfaces:**
- Produces: `demo_data.build_demo_payload() -> dict` and a JSON payload compatible with the existing `renderDashboard()` contract.
- Consumes: existing pure analytics/policy helpers where useful; it must not import Garmin authentication or read environment secrets.

- [ ] **Step 1: Write failing fixture tests** requiring a generic athlete identity, explicit synthetic/demo metadata, required top-level dashboard keys, no owner strings, and deterministic output across two builder calls.
- [ ] **Step 2: Run the fixture tests** and confirm the builder/file is absent or invalid.
- [ ] **Step 3: Implement `build_demo_payload()`** with fixed dates/seeded values and the dashboard's existing payload keys; label the dataset as synthetic and avoid copying values from the current vault/docs.
- [ ] **Step 4: Generate `data/demo.json`** from the builder and validate it with `json.load`.
- [ ] **Step 5: Delete the owner-specific encrypted vault** and keep live-vault output generated only by a configured fork workflow; do not replace it with ciphertext whose passphrase would need to be published.
- [ ] **Step 6: Replace `data/status.json`** with generic demo metadata and ensure the real plaintext `data/biometrics.json` remains ignored.
- [ ] **Step 7: Run the fixture tests and JSON validation**; expected result is a valid deterministic demo payload with no passphrase committed.

### Task 3: Harden live Garmin/Actions configuration and documentation

**Files:**
- Modify: `encrypt_data.py` — require `GARMIN_DASHBOARD_PASS`; remove default password and owner-specific comments/docstring.
- Modify: `.github/workflows/daily_sync.yml` — require/validate `GARMIN_TOKENS` and `GARMIN_DASHBOARD_PASS`, remove fallback secret expressions, and retain private runner-only token restoration.
- Modify: `.github/workflows/tests.yml` — verify the committed synthetic demo path; encrypted-vault verification remains a user-fork check that uses that fork's secret.
- Modify: `verify_garmin.py` — generic public-template copy and guidance; never print or persist user passwords in the repo.
- Modify: `garmin_source.py`, `sync.py` — generic fallback labels/copy and no owner-name defaults.
- Rewrite: `README.md` — public setup, demo mode, fork/secret workflow, and no live owner claims.
- Rewrite: `DASHBOARD_GUIDE.md` — generic metric guide, no owner metrics/passphrases/live URL.
- Modify: `ARCHITECTURE.md`, `HANDOFF.md` — generic ownership/setup notes and remove stale historical secrets/URLs.
- Test: `tests/test_pipeline.py` — encryption/workflow/documentation contracts.

**Interfaces:**
- `encrypt_data.main()` requires `GARMIN_DASHBOARD_PASS` and exits nonzero with an actionable message when absent.
- Workflow requires `GARMIN_TOKENS` and `GARMIN_DASHBOARD_PASS` as secrets; neither expression supplies a literal fallback.

- [ ] **Step 1: Write failing tests** for missing encryption passphrase failure, absence of `DEFAULT_PASS`, absence of fallback secret expressions, generic docs, and required secret validation.
- [ ] **Step 2: Run the focused tests** and confirm the existing defaults/docs fail them.
- [ ] **Step 3: Remove the encryption fallback** and make missing/blank `GARMIN_DASHBOARD_PASS` produce a concise error before reading/writing payload files.
- [ ] **Step 4: Harden the workflow** with explicit shell checks for both secrets, preserve `chmod 600`, and remove all literal fallback values.
- [ ] **Step 5: Generalize Garmin and orchestration copy/defaults** so missing account profile fields remain `None`/generic rather than falling back to the owner.
- [ ] **Step 6: Rewrite setup and guide docs** around the self-hosted fork flow, local Garmin session-token generation, GitHub secret creation, demo/live switch, and future repository naming.
- [ ] **Step 7: Run Python unit tests, `python -m py_compile *.py`, and documentation/source contract tests**; expected result is all tests pass and no owner-specific identifiers remain.

### Task 4: Final privacy audit and handoff

**Files:**
- Modify: `tests/test_pipeline.py` — final repository-wide privacy guard.
- Modify: `HANDOFF.md` or create `docs/HANDOFF.md` only if the current handoff cannot be safely generalized.
- Verify: all repository files under the project directory, including `data/` and workflow files.

**Interfaces:**
- Produces: a locally reviewable public-safe project ready for a separate GitHub repository creation step.

- [ ] **Step 1: Add scans** for owner names/handles/URLs, credential-like strings, embedded-token constants, known passphrase literals, and tracked plaintext biometric JSON.
- [ ] **Step 2: Run the complete verification set:**
  - `python -m unittest discover -s tests -t . -v`
  - `node tests/check_frontend_syntax.mjs index.html`
  - `node tests/check_relay.mjs`
  - `python -m py_compile *.py`
  - `python -c "import json; json.load(open('data/demo.json', encoding='utf-8'))"`
- [ ] **Step 3: Read the final changed-file list and diff-equivalent file contents**, confirming that no owner-specific encrypted vault or secret-bearing local artifacts were added.
- [ ] **Step 4: Update project-local memory/handoff** with changed files, actual checks, and the next step: create the new `Health Track Pro Max` GitHub repository only after the user reviews the final local result.
