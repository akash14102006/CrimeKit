# WHICH AGENT TO USE - Decision Authority Directory

**Need an expert decision? Don't know who to ask? This guide tells you WHO makes decisions WHAT.**

---

## 🔍 DECISION MATRIX

### ARCHITECTURE DECISIONS

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **Backend Architecture** | Backend Architect | Principal Architect | 5 days |
| **Frontend Architecture** | Frontend Architect | Principal Architect | 5 days |
| **Database Design** | Database Architect | Principal Architect | 5 days |
| **API Design** | Backend Architect | Principal Architect | 3 days |
| **Multi-Domain Design** | Principal Architect | CTO | 7 days |

### TECHNOLOGY DECISIONS

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **New Framework** | Relevant Architect | Principal Architect | 1 week |
| **New Library** | Domain Architect | Principal Architect | 3 days |
| **Language Change** | Principal Architect | CTO | 2 weeks |
| **Infrastructure Change** | DevOps Architect | Principal Architect | 5 days |

### SECURITY DECISIONS

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **Any Security Concern** | Security Architect | Chief Security Officer | 1 day |
| **Authentication Design** | Security Architect | Principal Architect | 3 days |
| **Data Protection** | Security Architect | Chief Security Officer | 5 days |
| **Access Control** | Security Architect | Chief Security Officer | 3 days |

### QUALITY & TESTING

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **Test Strategy** | QA Architect | Principal Architect | 3 days |
| **Coverage Goals** | QA Architect | Principal Architect | 1 day |
| **Release Readiness** | QA Architect | DevOps Architect | 2 days |

### OPERATIONS & INFRASTRUCTURE

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **Deployment Procedure** | DevOps Architect | Principal Architect | 3 days |
| **Monitoring Strategy** | DevOps Architect | Principal Architect | 2 days |
| **Disaster Recovery** | DevOps Architect | VP Operations | 1 week |
| **Infrastructure Cost** | DevOps Architect + Finance | CFO | 1 week |

### DESIGN & USER EXPERIENCE

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **Design System** | UI Architect | Principal Architect | 5 days |
| **Component Library** | UI Architect | Principal Architect | 3 days |
| **Accessibility** | UI Architect | Principal Architect | 3 days |

### AI & GOVERNANCE

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **AI Tool Usage** | AI Governance Architect | CTO | 1 day |
| **Model Selection** | AI Governance Architect | CTO | 3 days |
| **Prompt Standards** | AI Governance Architect | CTO | 2 days |

### STRATEGIC DECISIONS

| Decision | Contact | Escalates To | Timeline |
|----------|---------|--------------|----------|
| **Engineering Strategy** | Principal Architect | CTO | 2 weeks |
| **Budget/Resources** | VP Engineering | CFO | 2 weeks |
| **Policy Changes** | Relevant Architect | Principal Architect | 1 week |

---

## 👥 AGENT PROFILES

### 🏛️ **PRINCIPAL ARCHITECT** (Supreme)

**Responsibility:** Overall architecture, enterprise decisions, final authority  
**Contact:** principal-architect@company  
**Escalates To:** CTO  

**Approves:**
- Multi-domain architectural decisions
- Technology selections
- Enterprise standards
- Policy changes
- Conflicts between domain architects

**When to ask:**
- Architectural designs affecting multiple domains
- New technology adoption (frameworks, languages)
- Enterprise engineering standards
- Conflicts between teams
- Final escalation point

**How to reach:**
1. Send design document (ADD format)
2. Wait 1-2 days for initial review
3. Schedule sync meeting if needed
4. Expect decision within 5 days

---

### 🔌 **BACKEND ARCHITECT**

**Responsibility:** Backend service design, API architecture, performance  
**Contact:** backend-architect@company  
**Escalates To:** Principal Architect  

**Approves:**
- Backend service design
- API architecture and contracts
- Database queries and optimization
- Caching strategy
- Service integration patterns

**When to ask:**
- Designing a backend service
- API design questions
- Performance optimization
- Database query optimization
- Service-to-service communication

**How to reach:**
1. Slack: #backend-architecture
2. Create issue with design details
3. Request sync if complex
4. Expect feedback within 3 days

---

### 🎨 **FRONTEND ARCHITECT**

**Responsibility:** Component architecture, state management, performance  
**Contact:** frontend-architect@company  
**Escalates To:** Principal Architect  

**Approves:**
- Component architecture
- State management approach
- Performance optimization
- UI patterns
- Accessibility implementation

**When to ask:**
- Designing component structure
- State management approach
- Performance optimization
- Complex UI patterns
- Accessibility questions

**How to reach:**
1. Slack: #frontend-architecture
2. Create design PR for review
3. Request sync for complex designs
4. Expect feedback within 3 days

---

### 🗄️ **DATABASE ARCHITECT**

**Responsibility:** Data model, schema design, optimization  
**Contact:** database-architect@company  
**Escalates To:** Principal Architect  

**Approves:**
- Data model design
- Schema structure
- Index strategy
- Query optimization
- Replication strategy

**When to ask:**
- Designing data models
- Schema modifications
- Query optimization
- Performance issues
- Scalability concerns

**How to reach:**
1. Slack: #database-design
2. Share schema proposal
3. Include use cases and queries
4. Expect feedback within 2 days

---

### 🛡️ **SECURITY ARCHITECT** (Supreme)

**Responsibility:** All security concerns, threat modeling, compliance  
**Contact:** security-architect@company  
**Escalates To:** Chief Security Officer  

**Approves:**
- Security architecture
- Threat models
- Data protection
- Authentication/authorization
- Compliance requirements
- Incident response

**When to ask:**
- ANY security concern
- Threat modeling
- Data protection
- Access control
- Compliance questions
- Security incidents

**How to reach:**
1. URGENT: security@company or #security-incidents
2. Email security-architect@company
3. Include threat model if available
4. Expect response within 1 day (critical)

---

### ✅ **QA ARCHITECT**

**Responsibility:** Testing strategy, quality metrics, release readiness  
**Contact:** qa-architect@company  
**Escalates To:** Principal Architect  

**Approves:**
- Test strategy
- Coverage goals
- Automation approach
- Release readiness
- Quality metrics

**When to ask:**
- Testing strategy for feature
- Coverage requirements
- Test automation approach
- Release readiness
- Quality metrics

**How to reach:**
1. Slack: #quality-assurance
2. Create test plan document
3. Request review before implementation
4. Expect feedback within 2 days

---

### 🚀 **DEVOPS ARCHITECT**

**Responsibility:** Infrastructure, deployment, monitoring, disaster recovery  
**Contact:** devops-architect@company  
**Escalates To:** Principal Architect  

**Approves:**
- Deployment procedures
- Infrastructure changes
- Monitoring setup
- Disaster recovery
- Cost optimization
- Incident response infrastructure

**When to ask:**
- Deployment strategy
- Infrastructure needs
- Monitoring setup
- Performance issues
- Incident response
- Cost optimization

**How to reach:**
1. Slack: #devops
2. Create infrastructure proposal
3. Include capacity/performance needs
4. Expect feedback within 2 days

---

### 🎨 **UI ARCHITECT**

**Responsibility:** Design system, component library, accessibility  
**Contact:** ui-architect@company  
**Escalates To:** Principal Architect  

**Approves:**
- Design system changes
- Component library
- Accessibility compliance
- Visual consistency
- Component reusability

**When to ask:**
- Design system questions
- Component design
- Accessibility compliance
- Visual consistency
- Reusable components

**How to reach:**
1. Slack: #design-system
2. Share design specifications
3. Include accessibility audit if available
4. Expect feedback within 3 days

---

### 🤖 **AI GOVERNANCE ARCHITECT** (Supreme)

**Responsibility:** AI tool usage, model governance, safety protocols  
**Contact:** ai-governance@company  
**Escalates To:** CTO  

**Approves:**
- AI tool usage policies
- Model selection
- Prompt engineering standards
- AI safety protocols
- Bias mitigation

**When to ask:**
- Using new AI tool
- Model selection
- Prompt engineering
- AI safety concerns
- Bias mitigation

**How to reach:**
1. Slack: #ai-governance
2. Email ai-governance@company
3. Describe use case
4. Expect response within 1 day

---

## 🔄 ESCALATION PATHS

### When Domain Architect Says NO

If you disagree with a domain architect decision:

1. **Ask for rationale** - Understand their reasoning
2. **Provide new information** - If you have more context
3. **Request re-review** - After addressing concerns
4. **Escalate to Principal Architect** - If still disagreement
5. **Accept decision** - Principal Architect has final say

**Process:**
```
Domain Architect Decision
        ↓
Disagree? (Ask for rationale first)
        ↓
New info? (Request re-review)
        ↓
Still disagree?
        ↓
Email: principal-architect@company
Attach: Original decision + your rationale for appeal
Wait: 3-5 days for response
Accept: Principal Architect final decision
```

### When Multiple Domains Conflict

If backend and frontend architects disagree:

1. **Document both positions**
2. **Present to Principal Architect**
3. **Wait for mediation**
4. **Accept decision**

**Example:**
```
Backend: "API needs X design"
Frontend: "API design Y works better"
        ↓
Principal Architect arbitrates
        ↓
Final decision made
```

---

## 📊 DECISION TIME EXPECTATIONS

| Complexity | Time |
|-----------|------|
| Simple clarification | 1 day |
| Standard decision | 3 days |
| Complex decision | 5 days |
| Strategic decision | 1-2 weeks |
| Emergency decision | 1 day (critical path) |

---

## 🚨 ESCALATION FOR EMERGENCIES

### CRITICAL SECURITY ISSUE
→ **Contact:** security@company or #security-incidents  
→ **Response Time:** < 1 hour  
→ **Process:** INCIDENT_RESPONSE_WORKFLOW

### PRODUCTION DOWN
→ **Contact:** devops@company or #incidents  
→ **Response Time:** < 15 minutes  
→ **Process:** INCIDENT_RESPONSE_WORKFLOW

### MAJOR ARCHITECTURAL CONCERN
→ **Contact:** principal-architect@company  
→ **Response Time:** < 4 hours  
→ **Process:** Direct email with urgency

---

## ✅ CHECKLIST: BEFORE ESCALATING

Before asking for a decision, verify:

- [ ] I've read relevant policies
- [ ] I've consulted the knowledge base
- [ ] I've tried to solve it myself
- [ ] I have all necessary information
- [ ] I've documented my approach
- [ ] I know why I need this decision
- [ ] I've identified the right architect
- [ ] I've checked their availability
- [ ] I have timeline expectations
- [ ] I'm ready to implement decision

---

## 📧 CONTACT REFERENCE

| Role | Email | Slack | Urgency |
|------|-------|-------|---------|
| Principal Architect | principal-architect@company | @principal-architect | 5 days |
| Backend Architect | backend-architect@company | #backend-architecture | 3 days |
| Frontend Architect | frontend-architect@company | #frontend-architecture | 3 days |
| Database Architect | database-architect@company | #database-design | 2 days |
| Security Architect | security@company | #security-incidents | 1 day |
| QA Architect | qa-architect@company | #quality-assurance | 2 days |
| DevOps Architect | devops@company | #devops | 2 days |
| UI Architect | ui-architect@company | #design-system | 3 days |
| AI Governance | ai-governance@company | #ai-governance | 1 day |

---

**Last Updated:** June 2026  
**Questions?** Check [WHICH_FILE_TO_READ](WHICH_FILE_TO_READ.md)

