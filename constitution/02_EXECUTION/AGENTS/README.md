# AGENTS — AI Agent Role Definitions (skeleton)

This folder will define each AI agent role, responsibilities, allowed actions, guardrails, and required approvals. Every agent must have a human owner and a security review.

Suggested agent files
- `agent-overview.md` — taxonomy of agents (planner, supervisor, assistant, extractor)
- `development-agent.md` — code-generation and refactor agent rules
- `extractor-agent.md` — corpus extraction, graphify integration, caching rules
- `deployer-agent.md` — automation of deployment tasks (must require manual approval for production)
- `forensic-agent.md` — evidence parsing and timeline creation, chain-of-custody rules

Minimum content for each agent definition
- Role and purpose
- Allowed inputs/outputs
- Security and privacy constraints
- Approval and human-in-loop rules
- Test suites and validation requirements
- Monitoring and logging

TODO
- [ ] Create `agent-overview.md`
- [ ] Define `extractor-agent.md` and `forensic-agent.md`
