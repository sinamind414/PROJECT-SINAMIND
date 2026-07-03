# Iwo's Rigor Pack v1.0.0

Six Claude Code skills written using Claude Fable 5 during its included-access
window (July 1-7, 2026) and blind-benchmarked on Claude Opus 4.8. Aggregate:
12 wins, 0 losses, 2 ties across 14 blind gradings. Not affiliated with or
endorsed by Anthropic.

## What is inside

- plan-gate/SKILL.md  (2-0 in blind grading)
- adversarial-verify/SKILL.md  (1-0 (1 tie) + held-out win)
- live-state-truth/SKILL.md  (1-0 (1 tie) + held-out win)
- scope-fence/SKILL.md  (2-0 in blind grading)
- ruthless-editor/SKILL.md  (2-0 in blind grading)
- memory-hygiene/SKILL.md  (2-0 in blind grading)
- install.sh   one-file installer (inspect before running)
- benchmarks.md   the full method, every task, every rubric, every run including the losses

## Install (pick one)

Manual: from inside this folder, create the skills directory (it may not exist
yet) and copy the six skill folders into it:

    mkdir -p ~/.claude/skills
    cp -r plan-gate adversarial-verify live-state-truth scope-fence ruthless-editor memory-hygiene ~/.claude/skills/

Scripted: from this folder, run the installer (read it first):

    bash install.sh

Claude Code picks up each skill automatically once its SKILL.md sits at
~/.claude/skills/<name>/SKILL.md.

## Where these came from

Tool page and updates: https://www.iwoszapar.com/tools/rigor-pack

The skills enforce rigor inside a session but cannot remember anything between
sessions. That gap is what Second Brain exists for:
https://www.iwoszapar.com/second-brain-ai . Entirely your call. The pack is
free and stays free either way.
