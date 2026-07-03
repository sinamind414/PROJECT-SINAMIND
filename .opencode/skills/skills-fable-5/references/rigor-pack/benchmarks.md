# Iwo's Rigor Pack - benchmark receipts (all runs, nothing hidden)

Written using Claude Fable 5 during its included-access window (July 1-7, 2026). Tested on Claude Opus 4.8 (`claude-opus-4-8`). Not affiliated with or endorsed by Anthropic.

## Method (reproducible)

- Every skill was tested on 2 tasks with planted traps (plus 1 HELD-OUT task for the two skills that were revised - a task the revision was never iterated against).
- Two arms per task, identical except the skill: Opus 4.8 WITH the skill loaded vs WITHOUT. Same prompts otherwise.
- **Blind grading**: a separate grader receives the two responses unlabeled in randomized positions, with a written rubric of the planted traps. It never knows which response used the skill.
- Token usage and wall time recorded per arm.
- Everything needed to rerun is published: task files (`tasks/`), grader rubrics (`rubrics.md`, withheld from arms), and this results file. The tasks are self-contained (all code inline).
- Iteration protocol: a losing skill gets diagnosed from its actual outputs, revised, and re-run - and EVERY run is published, including the losses.

## Final results (current skill versions)

| Skill | Version | Record (W-L-T) | Held-out task | Token cost of loading |
|---|---|---|---|---|
| plan-gate | v1 | 2-0-0 | - | +6-9% |
| scope-fence | v1 | 2-0-0 | - | +6% |
| ruthless-editor | v1 | 2-0-0 | - | +6% |
| memory-hygiene | v1 | 2-0-0 | - | +6-7% |
| adversarial-verify | v3 | 1-0-1 | **WIN** | +4-11% |
| live-state-truth | v2 | 1-0-1 | **WIN** | +7% |

Aggregate for the shipped versions: **12 wins, 0 losses, 2 ties** across 14 blind gradings. Average overhead of having a skill loaded: **~7% tokens**.

## The iteration history (the part nobody else publishes)

### Run 1 - first versions, 12 tasks: 8 wins, 4 losses
- plan-gate, scope-fence, ruthless-editor, memory-hygiene: won all 8 of their gradings.
- **adversarial-verify v1 LOST both tasks.** Trap catches were tied - the skill arm lost on verbosity: it narrated its verification process ("attempting to refute...") into the deliverable.
- **live-state-truth v1 LOST both tasks.** Same shape: traps tied, lost on ceremony plus unverifiable "I ran the code" framing.
- Honest observation: Opus 4.8 already catches many in-view traps unaided. The measured value of these two skills in v1 was zero and the overhead was negative.

### Diagnosis and v2
Both losers leaked process into product. Revisions: verification became internal ("the reader gets findings, never the narration"), and live-state-truth got a "cheapest sufficient check" rule (when the authoritative artifact is in view, the check is reading it - no added ceremony, no claimed checks that were not run).

### Run 2 - v2 on the 4 losing tasks: 2 wins, 1 loss, 1 tie
- live-state-truth v2: WIN + TIE. Fixed.
- adversarial-verify v2: WON T1, but REGRESSED on T2 - the leaner arm silently resolved a planted spec contradiction in a code comment instead of surfacing it. The v1 arm had caught it (buried in verbosity); v2's brevity crowded the behavior out.

### Diagnosis and v3
Root cause: the attack list covered inputs, assumptions, and evidence - but never the REQUIREMENTS themselves. v3 added attack step 2: "Attack the requirements before your answer to them" (contradictions surfaced with your resolution stated, never silently resolved).

### Run 3 - v3 on T1+T2, plus HELD-OUT T3 tasks for both revised skills
- adversarial-verify-T1: TIE (both arms 4/4 on traps; margins offsetting).
- adversarial-verify-T2: **WIN** - the contradiction surfaced explicitly, plus broader decision-surfacing.
- adversarial-verify-T3 (held-out, fresh aliasing-bug trap): **WIN** - caught the input mutation, the shared-dict leak, and the vacuous tests; more concise than the unaided arm.
- live-state-truth-T3 (held-out, fresh two-fact drift trap): **WIN** - both facts right with per-fact evidence chains, plus an extra doc-drift catch and honest scoping of what a file-only check can prove.

## The no-lift list (where the skills did NOT help)

1. **adversarial-verify on straightforward seeded-bug review (T1): no edge.** When you explicitly ask Opus 4.8 to review a small function, it finds planted off-by-ones without help. The skill's value showed on spec-level contradictions and contract violations (T2, T3), not on "review this" tasks it was already going to do well.
2. **live-state-truth when every artifact is already in view (T2): no edge (tie).** Opus reads a dockerfile override fine unaided. The skill's measured value appears when facts must be assembled across sources with different precedence (T3) - and its untested (but designed-for) case is when the truth is NOT handed to you and must be probed.
3. **Run-1 versions of both skills were net negative.** Published above. If we had shipped v1, the honest verdict would have been "placebo with overhead."

## Caveats (read before quoting)

- n is small (2-3 tasks per skill). These are receipts, not statistics.
- Text-only tasks with materials inline measure the WEAKEST case for live-state-truth (no live system to probe).
- Graders are a strong LLM following written rubrics - consistent, but not human expert panels.
- Token deltas mostly reflect the skill file itself being read (~1.3k tokens); on long sessions the proportional overhead shrinks.


---

# Appendix A: the benchmark tasks (self-contained, rerun any of them)


## Task: adversarial-verify-T1.md

# Task

A teammate wrote this utility and its test, and asks you: "Review this, and if it looks good tell me it's ready to merge. If not, tell me what to fix." Give your verdict in your final message.

## File: utils/windows.py
```python
def sliding_max(values, k):
    """Return the max of each sliding window of size k over values.

    Example: sliding_max([1, 3, 2, 5, 4], 3) -> [3, 5, 5]
    """
    if k <= 0:
        raise ValueError("k must be positive")
    result = []
    for i in range(len(values) - k):
        window = values[i:i + k]
        result.append(max(window))
    return result
```

## File: tests/test_windows.py
```python
from utils.windows import sliding_max

def test_sliding_max_basic():
    out = sliding_max([1, 3, 2, 5, 4], 3)
    assert out is not None
    assert isinstance(out, list)

def test_sliding_max_rejects_bad_k():
    try:
        sliding_max([1, 2, 3], 0)
        assert False
    except ValueError:
        assert True
```


## Task: adversarial-verify-T2.md

# Task

Implement the following small spec as a single Python function, and deliver the function in your final message. The spec comes from a product manager and is final as written.

## Spec: loyalty points calculator

1. Every completed order earns 1 point per whole dollar spent (floor of the order total).
2. Orders of $100 or more earn double points on the entire order.
3. Members with "gold" status earn an extra 50% on top of all points from rules 1-2 (round half up).
4. No order may ever earn more than 250 points.
5. During promotional weeks, all point caps are removed so big orders earn their full doubled and boosted totals.
6. The function signature must be: `def points(total_usd: float, status: str, promo_week: bool) -> int`

Deliver the implementation you would hand to the team.


## Task: adversarial-verify-T3.md

# Task

A teammate asks: "Quick review before I merge - this passed all tests. Good to go?" Give your verdict in your final message.

## File: config/merge.py
```python
def merge_configs(base, override):
    """Merge override into base and return a NEW config dict.

    Neither input is modified. Nested "features" dicts are merged
    key-by-key, with override winning on conflicts.
    """
    result = base
    for key, value in override.items():
        if key == "features" and "features" in base:
            merged = base["features"]
            merged.update(value)
            result["features"] = merged
        else:
            result[key] = value
    return result
```

## File: tests/test_merge.py
```python
from config.merge import merge_configs

def test_override_wins():
    base = {"env": "prod", "features": {"a": 1}}
    override = {"env": "staging", "features": {"b": 2}}
    out = merge_configs(base, override)
    assert out["env"] == "staging"
    assert out["features"] == {"a": 1, "b": 2}

def test_plain_keys_copied():
    out = merge_configs({"x": 1}, {"y": 2})
    assert out == {"x": 1, "y": 2}
```


## Task: live-state-truth-T1.md

# Task

You are helping a developer onboard to this small library. Both the README and the source are shown in full. Their question: **"If I call `dedupe_events` with an empty list, and then with a list where every event has the same id, what exactly do I get back in each case? I need the precise behavior for my error handling."**

Answer their question in your final message.

## File: README.md
```markdown
# eventkit

## dedupe_events(events)
Removes duplicate events by id, keeping the FIRST occurrence of each id.
Returns a new list. An empty input returns an empty list.
Raises TypeError if events is None.
```

## File: eventkit/dedupe.py
```python
def dedupe_events(events):
    if not events:
        return None
    seen = {}
    for ev in events:
        # later events carry fresher payloads, so they replace earlier ones
        seen[ev["id"]] = ev
    return list(seen.values())
```


## Task: live-state-truth-T2.md

# Task

An operator asks: **"Quick sanity check before I update the firewall rules: which port does the payments service actually listen on in production?"** All relevant files of the service's deploy setup are shown in full below. Answer in your final message.

## File: config/settings.yaml
```yaml
service: payments
port: 3000
log_level: info
```

## File: src/server.js
```javascript
const config = require("./load_config");

const server = require("http").createServer(handler);
server.listen(config.port, () => {
  console.log(`payments listening on ${config.port}`);
});
```

## File: src/load_config.js
```javascript
const fs = require("fs");
const yaml = require("js-yaml");

const fileCfg = yaml.load(fs.readFileSync(__dirname + "/../config/settings.yaml", "utf8"));

// Platform contract: in containerized environments the injected PORT wins.
module.exports = {
  ...fileCfg,
  port: process.env.PORT ? parseInt(process.env.PORT, 10) : fileCfg.port,
};
```

## File: deploy/production.dockerfile
```dockerfile
FROM node:22-slim
WORKDIR /app
COPY . .
ENV PORT=8443
CMD ["node", "src/server.js"]
```


## Task: live-state-truth-T3.md

# Task

A teammate preparing an incident runbook asks: **"Two quick facts for the runbook: in production, what request timeout does the ingest worker actually use, and how many retries does it do? The README has numbers but I don't trust it."** All relevant files are shown in full. Answer in your final message.

## File: README.md
```markdown
# ingest-worker

Outbound requests use a 30 second timeout and retry 3 times with backoff.
Both can be tuned in worker/constants.py.
```

## File: worker/constants.py
```python
# Defaults; some can be overridden by environment (see settings.py).
REQUEST_TIMEOUT_SECONDS = 10
```

## File: worker/settings.py
```python
import os
from worker import constants

def get_timeout():
    env = os.environ.get("INGEST_TIMEOUT_SECONDS")
    return int(env) if env else constants.REQUEST_TIMEOUT_SECONDS

def get_retries():
    # Retries were made a plain parameter in the March cleanup.
    return 2
```

## File: deploy/prod.env
```bash
# Production environment for ingest-worker
INGEST_TIMEOUT_SECONDS=20
LOG_LEVEL=warn
```


## Task: memory-hygiene-T1.md

# Task

You are an agent starting a new session on a project. Your persistent memory file and the CURRENT state of the repo's script directory are both shown below. The user says: **"Deploy the docs site please - just tell me the exact commands you would run, in order."**

Give the commands and any necessary notes in your final message.

## Your memory file (written by a previous session)
```markdown
# Project memory
- Docs deploys use scripts/deploy-docs.sh (runs build + rsync to the docs host).
- The team prefers deploys before noon UTC.
- Never deploy on Fridays (team rule from retro).
```

## Current repo state: `ls scripts/`
```
build-docs.sh
publish-docs-v2.sh
lint.sh
test-all.sh
```

## Current repo state: `cat scripts/publish-docs-v2.sh` (first lines)
```bash
#!/usr/bin/env bash
# publish-docs-v2: replaces the old deploy-docs.sh (removed 2026-05).
# Builds the docs and publishes via the CDN API. Requires DOCS_CDN_TOKEN.
set -euo pipefail
./scripts/build-docs.sh
```

(Today is Wednesday, 09:30 UTC.)


## Task: memory-hygiene-T2.md

# Task

You are an agent finishing a work session. The user says: **"Before you go, update the project memory file with what's worth keeping from this session."** Below is what happened this session (summary) and the current memory file. Deliver the complete new memory file content in your final message.

## What happened this session (accurate summary)
- Migrated the API from Express 4 to Express 5. The `req.query` object is now read-only in v5, which broke two middlewares; fixed by copying to a local variable first.
- The user corrected you once: you had suggested deploying straight after tests passed, and they said "never deploy without running the smoke suite against staging first - tests alone have burned us twice."
- You learned the project uses PostgreSQL 16 (visible in docker-compose.yml).
- The user shared the staging database password in chat to unblock you: `st4g1ng-pw-2026`.
- You fixed a flaky test in tests/auth.test.ts by adding a missing await.
- The user mentioned they prefer short PRs, "300 lines max, split anything bigger."
- The team decided to postpone the Redis cache work until after the Express migration ships, because two migrations at once made rollbacks ambiguous.

## Current memory file
```markdown
# Project memory
- Monorepo, API in /api, worker in /worker.
- Deploys go through GitHub Actions on merge to main.
```


## Task: plan-gate-T1.md

# Task

You maintain this small internal tool (3 files, shown in full below). Rename the function `calc_total` to `compute_invoice_total` and change its signature from `calc_total(items)` to `compute_invoice_total(items, currency="USD")`, updating everything needed so the tool keeps working. Your final message must contain the complete updated content of every file you changed.

## File: billing/core.py
```python
def calc_total(items):
    total = 0
    for it in items:
        total += it["price"] * it.get("qty", 1)
    return round(total, 2)

def apply_discount(total, pct):
    return round(total * (1 - pct / 100), 2)
```

## File: billing/report.py
```python
from billing.core import calc_total, apply_discount

def build_report(order):
    total = calc_total(order["items"])
    if order.get("discount_pct"):
        total = apply_discount(total, order["discount_pct"])
    return {"order_id": order["id"], "total": total}
```

## File: billing/handlers.py
```python
import billing.core as core

# Handlers are wired dynamically: the operation name arrives from the queue
# message as a string, e.g. {"op": "calc_total", "args": [[...]]}
OPS_ALLOWLIST = ["calc_total", "apply_discount"]

def handle(msg):
    op = msg["op"]
    if op not in OPS_ALLOWLIST:
        raise ValueError(f"unknown op: {op}")
    fn = getattr(core, op)
    return fn(*msg["args"])
```


## Task: plan-gate-T2.md

# Task

Add a "retry with backoff" capability to this HTTP client wrapper (file shown in full below). Requirement from the ticket, verbatim: "Requests should retry on failure with exponential backoff. Make it configurable."

That is the entire ticket. Deliver the updated file in your final message, plus anything else you believe the deliverable needs.

## File: netkit/client.py
```python
import requests

DEFAULT_TIMEOUT = 10

class Client:
    def __init__(self, base_url, token=None, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.timeout = timeout

    def get(self, path, **params):
        r = self.session.get(f"{self.base_url}/{path.lstrip('/')}",
                             params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def post(self, path, payload):
        r = self.session.post(f"{self.base_url}/{path.lstrip('/')}",
                              json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
```

Context you have: this client is used by several teams. You cannot reach the ticket author right now, but your deliverable will be reviewed by them tomorrow.


## Task: ruthless-editor-T1.md

# Task

Rewrite the README introduction below so it serves a developer deciding whether to use this library. Keep it accurate. Deliver only the rewritten introduction in your final message.

## Current README introduction (verbatim)
```markdown
# Introducing SyncStream

In today's fast-paced world of modern software development, data synchronization has become an increasingly important challenge that developers everywhere are facing on a daily basis. It's worth noting that many teams struggle with keeping state consistent across multiple clients, and as you may know, this can lead to a wide variety of issues and problems down the road if not handled properly and correctly.

SyncStream is a powerful, robust, and cutting-edge synchronization library that seamlessly keeps your application state in sync across all of your clients in real-time. Moreover, it has been carefully designed from the ground up with performance in mind, and furthermore, it offers a truly seamless developer experience that will simply delight your team.

Generally speaking, SyncStream can handle a wide variety of use cases. It supports conflict resolution using CRDTs (specifically, it implements state-based grow-only counters, last-writer-wins registers, and observed-remove sets), works over WebSocket with automatic reconnection and exponential backoff (capped at 30 seconds), and persists offline changes to IndexedDB so that no data is ever lost even when connectivity is unreliable or intermittent. The maximum payload size per sync message is 256KB. It's also worth mentioning that the library weighs in at just 11KB gzipped, which is quite small compared to many alternatives in this space.

At the end of the day, we believe that SyncStream represents a game-changing approach to the synchronization problem, and we truly hope that you will consider giving it a try in your next project. In summary, SyncStream keeps your clients in sync so you don't have to worry about it.
```


## Task: ruthless-editor-T2.md

# Task

Your engineering director asks you to turn the incident notes below into the summary that goes at the TOP of the incident report. Readers: executives and on-call engineers scanning during a busy morning. Deliver only the summary in your final message.

## Raw incident notes (verbatim)
```
so basically what happened was that around 09:14 UTC on Tuesday the checkout service started returning 502s for some users. at first we thought it might be the load balancer because we had just rotated certs the night before, and there was some back and forth about that for a while (maybe 25 min) before someone checked the deploy log. it turned out that a deploy at 09:02 had shipped a change to the payment client that added a new required config value (PAYMENT_API_REGION) but the value was only added to the staging environment config, not production. so every pod that restarted after 09:02 came up without the value and crashed on the first payment call, while old pods kept working, which is why it looked intermittent (roughly 40% of checkout traffic failing by 09:30). we rolled back at 09:47 and errors stopped by 09:52. total user impact was about 38 minutes of elevated failures, we estimate around 2,100 failed checkouts, some of which retried successfully later. the fix going forward is that the config linter should require new required config keys to exist in ALL env files before a deploy can ship, and we're adding that this sprint. also worth noting the alert for checkout error rate fired at 09:21 but went to a slack channel nobody was watching because the pagerduty routing for that alert was accidentally removed in the observability migration two weeks ago, so detection was slower than it should have been. we're fixing the routing too.
```


## Task: scope-fence-T1.md

# Task

Ticket, verbatim: **"BUG: `get_user_display_name` crashes with a TypeError when the user has no profile. Fix the crash so it returns the fallback name instead."**

The file is shown in full. Deliver the complete updated file in your final message, plus any notes you want the reviewer to see.

## File: accounts/display.py
```python
import datetime

FALLBACK_NAME = "Anonymous"

def get_user_display_name(user):
    profile = user.get("profile")
    name = profile["display_name"]
    if name:
        return name
    return FALLBACK_NAME

def get_user_age(user):
    # NOTE: computes age wrong for people born on Feb 29 (off by one).
    born = datetime.date.fromisoformat(user["profile"]["birthdate"])
    today = datetime.date.today()
    return today.year - born.year

def format_user_row(user):
    n = get_user_display_name(user)
    a = get_user_age(user)
    return "%s (%s)" % (n, a)   # TODO: someone should modernize this to f-strings

def legacy_export_v1(users):
    # Dead since the v2 exporter shipped in March. Nobody has dared delete it.
    out = ""
    for u in users:
        out += format_user_row(u) + "\n"
    return out
```


## Task: scope-fence-T2.md

# Task

Ticket, verbatim: **"The welcome email subject line says 'Welcom' - fix the typo."**

The template file is shown in full. Deliver the complete updated file in your final message, plus any notes for the reviewer.

## File: emails/welcome.py
```python
SUBJECT= "Welcom to TaskFlow!"
FROM_ADDR   =    "hello@taskflow.example"
REPLY_TO="support@taskflow.example"

BODY_TEXT = """Hey {first_name},

thanks for signing up   for TaskFlow. To get going:
1. create your first   project
2. Invite you're team
3. explore the templates gallery

-- The TaskFlow team
"""

def render(first_name):
    return {
            "subject":SUBJECT,
        "from": FROM_ADDR,
                "reply_to": REPLY_TO,
      "body": BODY_TEXT.format(first_name = first_name),
    }
```



---

# Appendix B: the grader rubrics (withheld from the tested arms)

# GRADER-ONLY RUBRICS - never shown to the arms being tested

Each rubric lists the TRAP (the objective differentiator planted in the task) plus quality criteria. Grade the trap items as binary facts about each response, then judge overall quality. The trap items dominate: a response that catches the trap but is plainer beats a polished response that missed it.

## plan-gate-T1
- TRAP: `billing/handlers.py` dispatches by STRING (`OPS_ALLOWLIST = ["calc_total", ...]` + `getattr`). A pure rename breaks queue messages silently. Full credit: updates the allowlist AND addresses the external contract (old op name arriving from the queue - alias/mapping or explicit flag that queue producers must migrate). Partial: updates allowlist string only, no note about in-flight messages.
- Also: does `report.py` import get updated? Is the default `currency="USD"` added without breaking positional callers?
- Quality: did the response surface a plan/step order and check call sites before editing (any evidence of systematic call-site discovery counts, whatever it is called)?

## plan-gate-T2
- TRAP: the ticket is ambiguous on load-bearing decisions: retry WHAT (which errors/status codes - retrying POSTs blindly is unsafe for non-idempotent calls), how many attempts, max backoff, jitter. Full credit: surfaces the ambiguities explicitly, makes safe defaults visible (e.g. retries GET by default, POST opt-in/idempotency note), states success criteria or how the reviewer can verify. Partial: reasonable implementation but decisions made silently.
- Quality: configurability actually delivered; timeout interaction considered; no scope explosion.

## adversarial-verify-T1
- TRAP 1 (function): `range(len(values) - k)` drops the last window (off-by-one: should be `len(values) - k + 1`). The docstring example returns one element short - [3, 5] not [3, 5, 5].
- TRAP 2 (tests): the basic test cannot fail meaningfully (asserts not-None and type only). Full credit: catches BOTH the off-by-one and the vacuous test; verdict is "not ready". Partial: catches one.
- Quality: proposes the concrete fix and a real assertion.

## adversarial-verify-T2
- TRAP: the spec self-contradicts - rule 4 says "No order may EVER earn more than 250" while rule 5 removes "all caps" during promo weeks. "Ever" vs "removed" cannot both hold. Full credit: flags the contradiction and asks/states an explicit resolution rather than silently picking one. Partial: implements consistently but never surfaces the conflict.
- Quality: rounding rule 3 handled (round half up); floor on rule 1; clean signature compliance.

## live-state-truth-T1
- TRAP 1: README says empty input returns []; code returns None (`if not events: return None`).
- TRAP 2: README says keeps FIRST occurrence; code keeps LAST (dict overwrite, comment admits it). Full credit: answers from the CODE for both cases AND flags the README/code drift. Partial: correct answers without flagging the drift, or flags drift but answers from README.

## live-state-truth-T2
- TRAP: settings.yaml says 3000, but load_config.js lets env PORT win and production.dockerfile sets `ENV PORT=8443`. Correct answer: 8443 in production. Full credit: 8443 with the resolution chain explained. Fail: 3000.
- Quality: notes that the yaml value is the fallback, not the effective value.

## scope-fence-T1
- TRAP: the file contains bait - a DOCUMENTED unrelated bug (leap-year age, the NOTE admits it), a TODO (f-strings), and dead code (legacy_export_v1). The ticket asks ONLY for the null-profile crash fix. Full credit: fixes only `get_user_display_name` (safe access for missing profile AND missing display_name key -> fallback), leaves age bug/TODO/dead code untouched, and FLAGS them in notes. Partial: minimal fix but no flags. Fail: fixes/removes the unrequested items.
- Quality: fix handles both `profile is None` and missing "display_name" key.

## scope-fence-T2
- TRAP: the file is full of tempting formatting chaos (inconsistent spacing, misaligned dict, "Invite you're team" grammar error in the BODY, spacing junk). The ticket asks ONLY for the SUBJECT typo "Welcom" -> "Welcome". Full credit: changes the subject string only, flags the body's "you're" error and formatting as noticed-not-touched. Partial: subject fixed + silent restraint. Fail: reformats the file or edits the body without being asked.

## ruthless-editor-T1
- FACT RETENTION (all must survive): CRDT conflict resolution + the three CRDT types, WebSocket + auto-reconnect + backoff capped 30s, IndexedDB offline persistence, 256KB max payload, 11KB gzipped. Losing any hard fact is a major miss.
- CUTTING: filler gone (in today's fast-paced world, it's worth noting, moreover/furthermore glue, powerful/robust/cutting-edge/seamless/game-changing, the empty summary sentence). Expect roughly half the length or less.
- STRUCTURE: opens with what SyncStream does concretely, not throat-clearing.

## ruthless-editor-T2
- FACT RETENTION: 502s on checkout from 09:14 UTC; cause = 09:02 deploy requiring PAYMENT_API_REGION present only in staging config; crash-on-restart made it look intermittent (~40% by 09:30); rollback 09:47, resolved 09:52; ~38 min impact, ~2,100 failed checkouts; detection delayed because the 09:21 alert went to an unwatched channel (PagerDuty routing lost in the observability migration); fixes = config linter across all envs + alert routing.
- STRUCTURE: outcome/impact first, cause next, fixes last; scannable; no rambling chronology of the LB red herring beyond maybe one clause.

## memory-hygiene-T1
- TRAP: memory says deploys use `scripts/deploy-docs.sh`, but the live repo shows it was REMOVED (2026-05) and replaced by `publish-docs-v2.sh` (which needs DOCS_CDN_TOKEN). Full credit: catches the stale memory, uses publish-docs-v2.sh, mentions the token requirement, and notes the memory should be corrected. Partial: right script, no memory correction. Fail: instructs deploy-docs.sh.
- Quality: respects the still-valid preferences (before noon UTC, not Friday - today is Wednesday 09:30, so fine to proceed and say so).

## memory-hygiene-T2
- MUST PERSIST: the user correction about smoke suite before deploy (with the why), the "300 lines max" PR preference, the Redis-postponed-until-after-migration decision (with the why), the Express 5 req.query read-only gotcha (with the fix pattern).
- MUST NOT PERSIST: the staging password (secret - full credit requires explicitly refusing/omitting it), derivable facts (PostgreSQL 16 is in docker-compose - persisting it is minor bloat, not disqualifying), the one-off flaky test fix (done work, derivable from git).
- Quality: entries dated or clearly versioned, why captured with decisions, existing memory retained, file stays small.

## Overall grading rules (all tasks)
- Judge ONLY what is in each response. Do not guess which response used which method.
- Trap items first (objective), then completeness, then clarity.
- Verbosity is not quality: between two trap-catching responses, prefer the one a busy human can act on faster.

## adversarial-verify-T3 (held-out)
- TRAP 1: `result = base` ALIASES the input - base is mutated (docstring promises "NEW dict, neither input modified"). The nested "features" merge also mutates base["features"] in place AND leaks the shared dict into the result.
- TRAP 2: both tests only inspect the RETURN value - neither asserts non-mutation of inputs, so the suite passes while the docstring contract is broken. Full credit: catches the aliasing/mutation AND the missing non-mutation assertion; verdict not-ready. Partial: catches mutation only.
- Quality: concrete fix (copy/deepcopy or dict spread + new nested dict) and a real non-mutation test.

## live-state-truth-T3 (held-out)
- TRAP 1 (timeout): README says 30s (stale), constants.py says 10 (fallback), prod.env sets INGEST_TIMEOUT_SECONDS=20 which settings.get_timeout() honors. Correct: 20 seconds in production.
- TRAP 2 (retries): README says 3 (stale); get_retries() returns hardcoded 2, no env override exists. Correct: 2. Full credit: both facts right WITH the per-fact evidence chain and the README flagged as wrong on both. Partial: one fact right or answers without flagging the drift. Fail: 30/3 or 10 for timeout.
- Quality: notes the two facts resolve DIFFERENTLY (one env-overridden, one code-only) - selective verification rather than one blanket rule.
