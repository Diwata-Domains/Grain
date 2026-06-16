# Plan: TASK-0175

## Approach

Introduce one shared observability service that reads and writes packet-local JSON, then thread that data into the smallest useful command surfaces: task inspection/update and workflow-next reporting. Automatic hooks should record only workflow actions Grain already knows about.

---

## Step 1 — Add packet-local observability service

Create a service that resolves the active packet, reads or initializes `observability.json`, and records executor, model class, stage timestamps, and workflow actions deterministically.

---

## Step 2 — Expose CLI inspection and update surfaces

Add a `grain task observe` command that can show the current record or update it for the active or explicit task packet.

---

## Step 3 — Auto-record runner and close events

Update workflow activation and task-close paths so Grain records the last workflow action without inventing background event processing.

---

## Verification

Run focused CLI and workflow tests covering manual record updates, workflow-next output, and automatic activation/close hooks.
