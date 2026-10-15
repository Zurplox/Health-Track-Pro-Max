# Optional sync relay

The dashboard is a static page. A private fork may deploy this Cloudflare
Worker so its Refresh button can dispatch that fork's workflow without placing a
GitHub token in browser JavaScript. The public demo does not need a relay.

## Configure it

Set these Worker values; never commit them to the repository:

- `GITHUB_TOKEN`: fine-grained token limited to the fork's Actions permission.
- `REPO`: the fork's repository slug, such as `account/project`.
- `ALLOWED_ORIGIN`: the exact Pages origin for that fork.
- `WORKFLOW_FILE`: optional workflow filename, default `daily_sync.yml`.
- `REF`: optional branch, default `main`.
- `MIN_INTERVAL_SECONDS`: optional cooldown, default `300`.

Example commands, with placeholders only:

```bash
npx wrangler deploy worker.js --name health-track-sync-relay
npx wrangler secret put GITHUB_TOKEN --name health-track-sync-relay
npx wrangler secret put REPO --name health-track-sync-relay
npx wrangler secret put ALLOWED_ORIGIN --name health-track-sync-relay
```

Set `SYNC_RELAY_URL` in the fork's `index.html` after deployment. The worker
pins the workflow/ref configuration, checks the caller origin, applies a
cross-isolate cooldown using GitHub's run list, and never forwards GitHub error
bodies or secrets. It does not authenticate Garmin accounts.
