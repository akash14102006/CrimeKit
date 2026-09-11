#!/usr/bin/env python3
import os
import csv

ROOT = os.path.join(os.path.dirname(__file__), '..', 'constitution')
ROOT = os.path.abspath(ROOT)

def suggest_owner(path):
    p = path.replace('\\', '/').lower()
    if '/00_core/' in p:
        return 'Engineering Council'
    if '/01_intelligence/constitutions/' in p:
        if 'frontend' in p: return 'Frontend Architect'
        if 'backend' in p: return 'Backend Architect'
        if 'database' in p: return 'Database Architect'
        if 'testing' in p: return 'Test Architect'
        return 'Domain Architect'
    if '/01_intelligence/skills/' in p:
        return 'Subject Matter Expert'
    if '/02_execution/policies/' in p:
        return 'Policy Owner'
    if '/02_execution/workflows/' in p:
        return 'Release Manager'
    if '/02_execution/agents/' in p:
        return 'AI Platform'
    if '/03_governance/' in p:
        return 'Governance Board'
    if '/04_knowledge/' in p:
        return 'Knowledge Owner'
    if '/05_project_context/' in p:
        return 'Product / Architect'
    if '/06_workspace/' in p:
        return 'Team Lead'
    if '/07_bootstrap/' in p:
        return 'DevOps'
    return 'Unassigned'

def detect_status(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            txt = f.read().lower()
            if 'todo' in txt or 'skeleton' in txt or 'placeholder' in txt:
                return 'skeleton'
    except Exception:
        return 'missing'
    return 'exists'

rows = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.lower().endswith('.md'):
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT).replace('\\','/')
        owner = suggest_owner(rel)
        status = detect_status(full)
        note = ''
        # capture first header line as short description
        try:
            with open(full, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        note = line[:200]
                        break
        except Exception:
            pass
        rows.append((rel, owner, status, note))

out = os.path.join(ROOT, 'CONSTITUTION_FILES.csv')
with open(out, 'w', newline='', encoding='utf-8') as csvf:
    w = csv.writer(csvf)
    w.writerow(['path','suggested_owner','status','notes'])
    for r in sorted(rows):
        w.writerow(r)

print('Wrote', out)
