# TECHNICAL DEBT MANAGEMENT WORKFLOW

**Status:** Production  
**Version:** 1.0  
**Last Updated:** June 2026  

---

## PURPOSE

Process for identifying, categorizing, prioritizing, and systematically reducing technical debt to maintain codebase health and team velocity.

---

## DEBT CATEGORIES

### TYPE A: CODE QUALITY DEBT
- Poor naming
- Complex functions
- Duplicated code
- Outdated patterns
- Missing tests

**Interest Rate:** Medium  
**Mitigation:** Refactor

---

### TYPE B: ARCHITECTURAL DEBT
- Wrong pattern chosen
- Components too coupled
- Scalability concerns
- Design flaws
- Inadequate separation

**Interest Rate:** High  
**Mitigation:** Major refactoring

---

### TYPE C: DEPENDENCY DEBT
- Outdated dependencies
- Vulnerable packages
- Security patches needed
- Deprecated APIs
- Version mismatches

**Interest Rate:** High (Security)  
**Mitigation:** Update dependencies

---

### TYPE D: DOCUMENTATION DEBT
- Missing documentation
- Outdated documentation
- Poor architecture docs
- No API documentation
- No runbooks

**Interest Rate:** Low-Medium  
**Mitigation:** Documentation effort

---

### TYPE E: TEST DEBT
- Low code coverage
- Missing edge cases
- Brittle tests
- No performance tests
- No security tests

**Interest Rate:** High (Quality)  
**Mitigation:** Test implementation

---

### TYPE F: INFRASTRUCTURE DEBT
- Outdated servers
- Inefficient deployments
- Poor monitoring
- Manual processes
- Lack of automation

**Interest Rate:** High (Operational)  
**Mitigation:** Infrastructure upgrade

---

## WORKFLOW PHASES

### PHASE 1: DEBT IDENTIFICATION

**Inputs:**
- Code reviews
- Metrics dashboards
- Team feedback
- Automated analysis

**Identification Methods:**
1. **Code Review:** Identified during reviews
2. **Metrics:** Tracked by linters and analyzers
3. **Team Feedback:** Noted by developers
4. **Automated Tools:** SonarQube, Snyk, etc.
5. **Performance Monitoring:** Slowdowns detected
6. **Security Scanning:** Vulnerabilities found

**Tracking:**
- Repository for debt items
- Category classification
- Priority assessment
- Estimated effort
- Owner assignment

**Output:** Debt item created with metadata

---

### PHASE 2: CATEGORIZATION & ASSESSMENT

**Inputs:**
- Debt items
- Current codebase
- Team capacity

**Activities:**
1. Classify debt type
2. Assess impact
3. Estimate remediation effort
4. Determine risk level
5. Prioritize

**Assessment Questions:**
- ✅ What is the impact?
- ✅ How much effort to fix?
- ✅ What is the risk?
- ✅ How urgent?
- ✅ Does it block other work?
- ✅ Can it wait?

**Impact Levels:**
- 🔴 CRITICAL - Blocks features, causes outages
- 🟠 HIGH - Slows team, impacts quality
- 🟡 MEDIUM - Reduces maintainability
- 🟢 LOW - Nice to have

**Output:** Debt prioritized

---

### PHASE 3: DEBT BACKLOG MANAGEMENT

**Inputs:**
- Prioritized debt items
- Development roadmap
- Team capacity

**Activities:**
1. Maintain debt backlog
2. Rank by priority
3. Plan remediation schedule
4. Allocate capacity
5. Assign owners

**Backlog Composition:**
- 10% of sprint capacity for debt reduction
- Critical debt prioritized immediately
- High debt in next 2 sprints
- Medium debt in next quarter
- Low debt as time permits

**20% Rule:**
- Reserve 20% of team capacity for debt
- Prevents debt accumulation
- Maintains velocity
- Improves team satisfaction

**Output:** Debt backlog prioritized and scheduled

---

### PHASE 4: REMEDIATION PLANNING

**Inputs:**
- Prioritized debt item
- Estimated effort
- Technical approach

**Activities:**
1. Design remediation
2. Estimate effort
3. Plan testing approach
4. Plan rollback strategy
5. Get approval

**Planning:**
- [ ] Goal clearly defined
- [ ] Approach documented
- [ ] Effort estimated
- [ ] Testing strategy planned
- [ ] Dependencies identified
- [ ] Owner assigned

**Output:** Remediation plan approved

---

### PHASE 5: IMPLEMENTATION

**Inputs:**
- Remediation plan
- Team resources
- Timeline

**Activities:**
1. Execute remediation
2. Follow appropriate workflow (Refactoring, etc.)
3. Document changes
4. Test thoroughly
5. Review code

**Implementation:**
- See Refactoring Workflow for code changes
- See Bug Fix Workflow for urgent debt
- See Dependency Update Workflow for updates
- See Infrastructure Workflow for infrastructure

**Output:** Debt remediated

---

### PHASE 6: VERIFICATION & METRICS

**Inputs:**
- Remediated debt
- Metrics baseline
- Quality measurements

**Activities:**
1. Verify debt resolved
2. Measure impact
3. Update metrics
4. Document results
5. Share learnings

**Metrics Tracked:**
- Code quality score (pre/post)
- Test coverage (pre/post)
- Performance metrics (pre/post)
- Team velocity (pre/post)
- Defect rate (pre/post)

**Verification:**
- [ ] Debt item resolved
- [ ] Quality improved
- [ ] No new debt introduced
- [ ] Documentation updated
- [ ] Team trained if needed

**Output:** Metrics updated, debt closed

---

## DEBT QUADRANT

```
              URGENT
                ↑
                |
        Q2      |      Q1
     (Schedule) | (Now!)
                |
    IMPORTANT ↔+─────────→ NOT IMPORTANT
                |
        Q3      |      Q4
    (Consider)  | (Ignore)
                |
              NOT URGENT
```

**Q1 (Urgent & Important):** Address immediately  
**Q2 (Important, Not Urgent):** Schedule next sprint  
**Q3 (Urgent, Not Important):** Quick fix if time  
**Q4 (Not Important, Not Urgent):** Skip, focus on Q1/Q2

---

## DEBT INTEREST CALCULATION

```
Debt Interest = Impact × Frequency × Technical Debt Cost

Impact:        1-10 (how bad if no fix)
Frequency:     1-10 (how often encountered)
Tech Debt Cost: 1-10 (effort to fix)

Example:
- Code quality debt: 3 × 8 × 2 = 48 interest
- Security debt: 10 × 3 × 5 = 150 interest
- Documentation debt: 2 × 10 × 1 = 20 interest
```

---

## DEBT MONITORING DASHBOARD

| Debt Type | Count | Priority | Effort | Estimated Fix |
|-----------|-------|----------|--------|----------------|
| Code Quality | 45 | Medium | 60 hrs | 2 weeks |
| Architecture | 8 | High | 200 hrs | 6 weeks |
| Dependency | 12 | High | 40 hrs | 1 week |
| Documentation | 30 | Low | 50 hrs | 2 weeks |
| Test | 15 | High | 80 hrs | 2 weeks |
| Infrastructure | 5 | High | 120 hrs | 4 weeks |
| **TOTAL** | **115** | | **550 hrs** | **~4 months** |

---

## METRICS & TRENDING

**Track:**
- ✅ Total debt count trend
- ✅ Critical debt count
- ✅ Average time to resolve
- ✅ Debt density (per 1000 LOC)
- ✅ Debt interest rate

**Goals:**
- ✅ Reduce debt by 10% per quarter
- ✅ Critical debt = 0
- ✅ Average resolution < 2 weeks
- ✅ Debt density < 2 per 1000 LOC

---

## PREVENTION PRINCIPLES

✅ **Create less debt:**
- Use patterns and standards
- Code review for early detection
- Pair programming
- Architecture review

✅ **Pay off debt regularly:**
- 20% capacity allocation
- Prioritize systematically
- Monitor metrics
- Share learnings

✅ **Track debt explicitly:**
- Central registry
- Prioritization system
- Trending dashboard
- Regular reviews

---

**Workflow Status:** ACTIVE  
**Last Review:** June 2026  
**Next Review:** September 2026

