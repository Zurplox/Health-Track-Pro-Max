/**
 * Sync relay for the Meridian dashboard.
 *
 * Why this exists: the dashboard is a static public page, so it cannot hold the
 * GitHub token that starts a sync. GitHub's secret scanning revokes a leaked token
 * in a public repository, and any token in the page would let every visitor start
 * runs on the owner's account. Instead the token lives here, as the worker's own
 * encrypted secret, and the page only knows this deployment's URL.
 *
 * The worker does one thing: start `daily_sync.yml` on `main`.
 *
 *   * the workflow file and the ref are pinned here, never taken from the request
 *   * only the dashboard's origin may call it (ALLOWED_ORIGIN)
 *   * a second request inside MIN_INTERVAL_SECONDS is refused with 429, so a
 *     stranger who finds the URL cannot spend the owner's Actions minutes
 *   * nothing about the token is ever returned, logged or echoed
 *
 * Environment (set with `wrangler secret put` -- never in a file):
 *   GITHUB_TOKEN        fine-grained token, this fork only, Actions: read and write
 * Optional variables (plain text is fine for these):
 *   REPO                repository slug for this fork
 *   ALLOWED_ORIGIN      exact Pages origin for this fork
 *   MIN_INTERVAL_SECONDS default 300
 */

const DEFAULT_WORKFLOW_FILE = "daily_sync.yml";
const DEFAULT_REF = "main";

// Per-isolate, best effort: Cloudflare may run several isolates, so this stops a
// burst rather than a determined attacker. The GitHub lookup below is the real
// guard -- it sees every run, whichever isolate asked for it.
let lastDispatchAt = 0;

function corsHeaders(origin, allowed) {
  const ok = origin === allowed;
  return {
    "Access-Control-Allow-Origin": ok ? origin : allowed,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

function json(body, status, origin, allowed) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(origin, allowed) },
  });
}

/** Ask GitHub itself when the workflow last ran, so every isolate agrees. */
async function lastRunAt(token, repo, workflowFile) {
  const resp = await fetch(
    `https://api.github.com/repos/${repo}/actions/workflows/${workflowFile}/runs?per_page=1`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "meridian-sync-relay",
      },
    }
  );
  if (!resp.ok) return null; // unknown: fall through to the in-isolate guard
  const data = await resp.json();
  const run = data.workflow_runs && data.workflow_runs[0];
  if (!run) return 0;
  const started = Date.parse(run.run_started_at || run.created_at || 0);
  return Number.isFinite(started) ? started : null;
}

export default {
  async fetch(request, env) {
    const allowed = (env.ALLOWED_ORIGIN || "").replace(/\/$/, "");
    const repo = String(env.REPO || "").trim();
    const workflowFile = String(env.WORKFLOW_FILE || DEFAULT_WORKFLOW_FILE).trim();
    const ref = String(env.REF || DEFAULT_REF).trim();
    const origin = request.headers.get("Origin") || "";
    const minInterval = Number(env.MIN_INTERVAL_SECONDS || 300) * 1000;

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin, allowed) });
    }
    if (request.method !== "POST") {
      return json({ error: "POST only" }, 405, origin, allowed);
    }
    // A browser sends Origin. A request without one is not the dashboard.
    if (!allowed || origin !== allowed) {
      return json({ error: "origin not allowed" }, 403, origin, allowed);
    }
    if (!repo) {
      return json({ error: "relay is not configured: REPO variable is missing" }, 500, origin, allowed);
    }
    if (!env.GITHUB_TOKEN) {
      return json({ error: "relay is not configured: GITHUB_TOKEN secret is missing" }, 500, origin, allowed);
    }

    // The real cooldown reads GitHub's own view of the last run. If the lookup
    // fails, the in-isolate timestamp still catches a burst from this isolate.
    const last = await lastRunAt(env.GITHUB_TOKEN, repo, workflowFile);
    const reference = last === null ? lastDispatchAt : Math.max(last, lastDispatchAt);
    const since = Date.now() - reference;
    if (reference && since < minInterval) {
      const wait = Math.ceil((minInterval - since) / 1000);
      return json(
        { error: "a sync started recently", retry_in_seconds: wait },
        429,
        origin,
        allowed
      );
    }

    const resp = await fetch(
      `https://api.github.com/repos/${repo}/actions/workflows/${workflowFile}/dispatches`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "meridian-sync-relay",
        },
        body: JSON.stringify({ ref }),
      }
    );

    if (resp.status === 204 || resp.ok) {
      lastDispatchAt = Date.now();
      return json({ dispatched: true, workflow: workflowFile, ref }, 202, origin, allowed);
    }
    // Status only. The response body can carry details about the token that a
    // public page must never receive.
    const hint =
      resp.status === 401
        ? "GITHUB_TOKEN was rejected -- it may have expired or been revoked"
        : resp.status === 403
          ? "GITHUB_TOKEN lacks Actions: write on this repository"
          : resp.status === 404
            ? "workflow not found -- does the token see this repository?"
            : "GitHub refused the dispatch";
    return json({ error: hint, status: resp.status }, 502, origin, allowed);
  },
};
