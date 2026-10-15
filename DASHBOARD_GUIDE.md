# Health Track Pro Max dashboard guide

The dashboard is a reader-friendly view over Garmin measurements and
deterministic derived signals. In the public template, every visible value is
synthetic demo data and the header says so. A private fork replaces the demo
fixture with its own encrypted vault.

## Reading the page

- **Today at a glance** shows steps, recent sessions, and last night's sleep.
- **Daily briefing** explains recovery, sleep, workload, readiness, and injury
  risk. The rule engine owns every number; an optional model may write prose only.
- **HRV and resting heart rate** are read against the account's own baselines,
  not population claims.
- **Sleep architecture** separates total, deep, REM, light, and awake time.
- **Body Battery and stress** disclose whether values were measured, estimated,
  or synthetic demo values.
- **Capacity and forecasts** use profile/device values when a private Garmin
  account supplies them; absent values render as `--`.
- **Correlation Lab** publishes only sufficiently supported paired-day patterns
  and labels them as associations, not causes.
- **Coach** turns measured history into actions. A training domain with no
  history says `NOT MEASURED` instead of inventing a prescription.

## Demo versus live mode

Demo mode loads `data/demo.json` without a passphrase. It is intentionally
passwordless because the dataset is synthetic. A private deployment sets
`DEMO_MODE` to `false`; the page then decrypts `data/biometrics.enc.json` with
the private viewer passphrase configured for that fork. There is no public
default passphrase and no emergency passphrase in the template.

## Garmin setup

Garmin authentication happens through `verify_garmin.py` and the Python
pipeline, never through browser JavaScript. Store the generated session-token
JSON in the fork's private `GARMIN_TOKENS` Actions secret. Rotate it by running
the helper again if Garmin invalidates the session. Keep the local token store
outside the repository.

## Refresh, lock, and report

Refresh re-reads published data. A sync starts only when the fork owner has
configured a private relay; the public demo never starts a GitHub workflow.
`L` purges the rendered dashboard and returns to the live-vault lock screen.
`P` opens the browser print dialog for the clinical report. `M` toggles sound
and haptic feedback, `T` switches themes, and `1`–`9` jump to sections.

This dashboard is an analytics and visualization tool, not a diagnosis. Treat
unusual readings as a reason to review the raw measurement and seek appropriate
professional advice.
