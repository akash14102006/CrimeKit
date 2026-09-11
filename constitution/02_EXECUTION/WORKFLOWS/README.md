# WORKFLOWS — Execution Tier (skeleton)

This folder will hold canonical workflow definitions, runbooks, and decision gates used by engineering teams. Each workflow must reference the relevant domain constitutions and testing gates.

Required workflows (create one file per workflow):
- `feature-development.md` — branching, code review, testing, merge, release checklist
- `release-management.md` — release windows, rollback plan, release evidence, approvals
- `incident-response.md` — detection, triage, escalation, communication, postmortem
- `deployment.md` — CI/CD flows, canary, blue/green, verification
- `security-vulnerability.md` — disclosure, triage, patching
- `ai-agent-runbook.md` — agent invocation, guardrails, human-in-the-loop

Minimum content for each workflow
- Purpose and scope
- Actors and owners
- Inputs and outputs
- Steps (numbered)
- Required checks (link to `00_CORE/TESTING_SUPREME_CONSTITUTION.md`)
- Approval gates (who signs off)
- Evidence artifacts (what to attach to release)
- Metrics and KPIs

TODO
- [ ] Create `feature-development.md`
- [ ] Create `release-management.md`
- [ ] Create `incident-response.md`
- [ ] Create `ai-agent-runbook.md`
