#!/usr/bin/env python3
import csv
import os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'constitution')
ROOT = os.path.abspath(ROOT)
IN = os.path.join(ROOT, 'CONSTITUTION_FILES.csv')
OUT = os.path.join(ROOT, 'CONSTITUTION_OWNERS.csv')

def owner_for(path):
    p = path.replace('\\','/').lower()
    if p.startswith('00_core/'):
        return 'Engineering Council'
    if p.startswith('01_intelligence/constitutions/'):
        if 'frontend' in p: return 'Frontend Architect'
        if 'backend' in p: return 'Backend Architect'
        if 'database' in p: return 'Database Architect'
        if 'testing' in p: return 'Principal Test Architect'
        return 'Domain Architect'
    if p.startswith('01_intelligence/skills/'):
        return 'SME (Skill Lead)'
    if p.startswith('02_execution/policies/'):
        if 'security' in p: return 'Security Team'
        if 'finops' in p or 'cost' in p: return 'FinOps'
        return 'Policy Owner'
    if p.startswith('02_execution/workflows/'):
        return 'Release Manager'
    if p.startswith('02_execution/agents/'):
        return 'AI Platform'
    if p.startswith('03_governance/agents/'):
        return 'Architecture Office'
    if p.startswith('03_governance/policies/'):
        return 'Governance Board'
    if p.startswith('03_governance/compliance/'):
        return 'Compliance Officer'
    if p.startswith('04_knowledge/'):
        return 'Knowledge Manager'
    if p.startswith('05_project_context/'):
        return 'Product Owner'
    if p.startswith('06_workspace/'):
        return 'Team Lead'
    if p.startswith('07_bootstrap/'):
        return 'DevOps'
    if path in ('CONSTITUTION_MAPPING.md','PHASE1_ANALYSIS.md'):
        return 'Program Manager'
    if path == 'prompt.md':
        return 'Principal Architect'
    return 'Unassigned'

rows = []
with open(IN, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        p = row['path']
        assigned = owner_for(p)
        rows.append({'path':p, 'assigned_owner':assigned, 'status':row.get('status',''), 'notes':row.get('notes','')})

with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['path','assigned_owner','status','notes'])
    w.writeheader()
    for row in rows:
        w.writerow(row)

print('Wrote', OUT)
