#!/usr/bin/env bash
#
# Drives the 90-second Grain demo cast. It types each command character by
# character so the recording looks live, without the risk of a typo on camera.
#
#   uv tool install asciinema
#   uv tool install --force --refresh grain-kit     # must be >= 0.6.0
#   bash products/grain/scripts/demo_cast.sh --check    # dry run, no recording
#   asciinema rec --idle-time-limit 2 --cols 92 --rows 28 \
#       -c "bash products/grain/scripts/demo_cast.sh" grain-demo.cast
#
# The workspace is rebuilt from products/grain/examples/demo on every run, so
# the cast is reproducible and you can re-record until you like the pacing.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
EXAMPLE="$REPO_ROOT/products/grain/examples/demo"
STAGE="${DEMO_STAGE_DIR:-/tmp/grain-demo-cast}"

TYPE_DELAY="${TYPE_DELAY:-0.035}"   # per-character
READ_PAUSE="${READ_PAUSE:-2.0}"     # after output, so viewers can read
BEAT_PAUSE="${BEAT_PAUSE:-1.0}"     # before the next command
SAY_PAUSE="${SAY_PAUSE:-1.2}"       # after a narration line
DRY_RUN=0

PROMPT='\033[1;32m$\033[0m '

die() { printf 'demo_cast: %s\n' "$1" >&2; exit 1; }

[[ -d "$EXAMPLE" ]] || die "example workspace not found at $EXAMPLE"
command -v grain >/dev/null || die "grain is not on PATH — uv tool install --force --refresh grain-kit"

version="$(grain --version 2>/dev/null || true)"
case "$version" in
  *"0.6."*|*"0.7."*|*"0.8."*|*"0.9."*|*"1."*) ;;
  *) die "need grain >= 0.6.0, found: ${version:-none}. Run: uv tool install --force --refresh grain-kit" ;;
esac

# Rebuild a pristine stage from the committed example.
rm -rf "$STAGE"
cp -R "$EXAMPLE" "$STAGE"
cd "$STAGE"
git init -q .
git add -A
git -c user.email=demo@northwind.test -c user.name="Northwind" commit -qm "Northwind Internal" >/dev/null

if [[ "${1:-}" == "--check" ]]; then
  DRY_RUN=1
  TYPE_DELAY=0; READ_PAUSE=0; BEAT_PAUSE=0; SAY_PAUSE=0
  printf 'demo_cast: dry run in %s\n\n' "$STAGE"
fi

# Type a command out, then run it.
run() {
  local cmd="$1"
  printf "%b" "$PROMPT"
  local i
  for (( i=0; i<${#cmd}; i++ )); do
    printf '%s' "${cmd:$i:1}"
    sleep "$TYPE_DELAY"
  done
  printf '\n'
  sleep 0.25
  # `|| true` so a nonzero exit (the whole point of beat 3) does not kill the cast
  eval "$cmd" || true
  sleep "$READ_PAUSE"
  printf '\n'
  sleep "$BEAT_PAUSE"
}

# A line of narration, shown dim, for viewers watching without audio.
say() {
  printf '\033[2m# %s\033[0m\n' "$1"
  sleep "$SAY_PAUSE"
}

# Keep the dry run's output on screen; only the real cast starts clean.
(( DRY_RUN )) || clear

say "Northwind: one repo holding a Python service AND the company's documents."
run "ls services/api company"

say "Grain sees three queued tasks: one in code, one in a spreadsheet, one in a doc."
run "grain status"

say "Open the first one."
run "grain task create --phase 1 --task-num 1 --title 'Add /health endpoint to the status service'"

say "Now try to mark it done without doing the work."
run "grain task close --id TASK-0001"

say "It refused. No results file, no review. The agent cannot self-certify."

say "Same gate, but on a spreadsheet. Ask for a change to the Q3 budget."
run "grain office spreadsheet propose --source company/q3-budget.xlsx --set 'Sheet1!B2=14' --task-id TASK-0001"

say "The change was PROPOSED, not applied. Look at what actually changed on disk:"
run "git status --short"

say "company/q3-budget.xlsx is untouched. The proposal waits in the task packet."
say "That is Grain: one reviewed loop, whether the work is code or not."
sleep "$BEAT_PAUSE"
