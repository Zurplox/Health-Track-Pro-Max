# Public Health Dashboard Template Design

## Goal

Turn the current single-owner Meridian Garmin dashboard into a public-safe,
self-hosted template for the future **Health Track Pro Max** project. The public
repository must contain only generic code, documentation, tests, and clearly
synthetic demo data. A person who forks the repository must be able to run the
same analytics against their own Garmin account without exposing Garmin, GitHub,
viewer, or encryption credentials in the repository or browser bundle.

The new GitHub repository is intentionally out of scope for this change. This
pass prepares the local project so it can be renamed, reviewed, and published in
a later step.

## Decisions

- Deployment model: one fork/deployment per user; no shared hosted backend.
- Garmin credentials: private GitHub Actions secret containing the user's
  locally generated Garmin session-token JSON, not browser-entered credentials.
- Public demo: passwordless and backed by synthetic JSON data. It must be
  visually representative but must not require or contain a real passphrase.
- Real deployments: encrypted vault mode remains available and requires
  `GARMIN_DASHBOARD_PASS`; no fallback passphrase is allowed.
- Manual refresh: public code may re-read the published vault, but it must not
  include an embedded GitHub token or an owner-pinned relay URL/repository.
  Optional relay setup belongs to each user's fork configuration.
- Preserve the existing analytics, dashboard layout, encryption format, and
  meaningful test coverage unless a change is required to remove owner-specific
  behavior.

## Architecture

### Demo mode

The page loads `data/demo.json` when demo mode is enabled. Demo mode has a
generic identity and synthetic measurements, and bypasses the personal-vault
unlock screen. The fixture is generated from a checked-in deterministic builder
so its values are reproducible and obviously non-personal.

### User fork mode

The existing Python pipeline remains the only Garmin integration. A user:

1. forks the repository;
2. runs `verify_garmin.py` locally to authenticate and create local session
   tokens;
3. base64-encodes that token file into the fork's `GARMIN_TOKENS` Actions
   secret;
4. sets a private `GARMIN_DASHBOARD_PASS` Actions secret;
5. enables the workflow and deploys the fork's Pages site.

The workflow restores only the user's token file on the runner, runs the
existing pipeline, encrypts the resulting payload, and commits only ciphertext
and status metadata. The user's real data never enters the template repository
as plaintext. The page can be switched to encrypted-vault mode by the fork
configuration and asks that deployment's viewer for its passphrase.

### Configuration boundary

Owner-specific values are removed from application code and docs. Repository
slug, Pages origin, relay URL, display name, and demo/live mode become explicit
configuration values with safe empty/generic defaults. A configured relay is
never inferred from the template and never receives Garmin credentials.

## Credential and privacy requirements

- Delete the embedded GitHub sync-token fragments and all code that decodes them.
- Remove the default viewer and master-lock passphrases and their documentation.
- Make encryption fail loudly when `GARMIN_DASHBOARD_PASS` is absent.
- Remove owner names, handles, repository URLs, live-site URLs, exact personal
  metric claims, and account-specific comments from source/docs/tests.
- Keep token-shaped examples schematic or use placeholders that cannot be
  mistaken for credentials.
- Replace the committed encrypted vault with generated synthetic demo JSON; live
  forks create their encrypted vault only after configuring their own secrets.
- Add repository scans that reject owner identity and credential patterns, and
  verify that no embedded token or passphrase fallback remains.

## Error handling

- Missing user secrets produce actionable workflow errors rather than silently
  selecting a public/default credential.
- Demo mode reports that it is synthetic and does not imply Garmin connectivity.
- Live mode reports missing vault configuration without leaking secret values.
- Refresh without a configured user-owned relay/token only re-reads published
  data and clearly says that it did not start a sync.

## Verification

- Python unit tests, including encryption and payload assembly.
- Frontend inline-script syntax check.
- Relay tests with generic configurable repository/origin values.
- Browser-crypto vault verification remains available for a live fork using that
  fork's private passphrase; the public template verifies its synthetic JSON
  fixture without publishing a passphrase.
- Repository-wide scans for personal identity, token-like credentials, fallback
  passphrases, embedded tokens, and accidental plaintext biometric JSON.
- Python compilation for all pipeline modules.

## Out of scope

- Creating or pushing the new GitHub repository.
- Building a shared multi-user backend or Garmin OAuth service.
- Changing the analytics model or redesigning the dashboard UI beyond generic
  identity, demo/live mode, and setup guidance.
