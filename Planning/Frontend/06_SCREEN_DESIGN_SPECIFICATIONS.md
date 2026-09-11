# 06_SCREEN_DESIGN_SPECIFICATIONS

# CrimeKit Screen Design Specifications

## Purpose
Defines every production screen, its layout, components, interactions, states, permissions, and responsive behavior.

---

# Global Screen Template

Every screen must document:
- Purpose
- Primary User
- Route
- Layout
- Components
- User Actions
- Loading State
- Empty State
- Error State
- Permissions
- Keyboard Shortcuts
- Responsive Behavior

---

# 1. Authentication

## Login
Purpose: Secure entry.
Components:
- Logo
- Email
- Password
- Remember Me
- Forgot Password
- Sign In
States:
Loading, Invalid Credentials, Locked Account.

## Forgot Password
## Reset Password
## MFA Verification
## Session Expired

---

# 2. Dashboard

Widgets:
- KPI Cards
- Recent Cases
- Investigation Queue
- AI Insights
- Alerts
- Recent Evidence
- Activity Feed

Actions:
Create Case
Upload Evidence
Open Investigation

States:
Loading
No Cases
Offline
Permission Denied

---

# 3. Cases

## Case List
Filters
Search
Bulk Actions
Sorting
Pagination

## Case Details
Header
Overview
Evidence
Timeline
People
Notes
Reports

## Create Case
Stepper
Validation
Draft Save

---

# 4. Evidence Module

## Upload
Drag & Drop
Progress
Virus Scan
Hash Generation

## Evidence Library
Grid/Table
Filters
Preview

## Evidence Details
Metadata
OCR
Hashes
AI Summary
Chain of Custody

Supported:
Image
Video
Audio
PDF
Disk Image
Mobile Dump

---

# 5. Investigation Workspace

Three-panel layout

Left:
Evidence Tree

Center:
Evidence Viewer

Right:
Metadata
AI Findings
Notes

Toolbar:
Bookmark
Tag
Compare
Timeline
Export

---

# 6. Timeline

Views:
Day
Week
Month

Features:
Zoom
Search
Filter
Grouping
Export

Event Types:
Evidence
AI
User
System

---

# 7. Knowledge Graph

Canvas
Node Inspector
Relationship Panel
Mini Map
Legend
Search

Node Types:
Person
Device
Account
Vehicle
Organization
Location

---

# 8. AI Assistant

Dockable panel

Sections:
Conversation
Sources
Suggested Actions
Prompt History

Capabilities:
Summarize
Explain
Generate Report
Suggest Leads

---

# 9. Reports

Template Gallery
Editor
Preview
Digital Signature
Export PDF
Export DOCX
Print

---

# 10. Administration

Users
Roles
Permissions
Audit Logs
System Health
API Keys

---

# 11. Settings

Profile
Appearance
Notifications
Security
Language
Theme

---

# 12. Global Dialogs

Delete Confirmation
Archive
Export
Share
Assign User
Permission Request

---

# 13. Global States

Loading
Skeleton
Empty
Offline
Maintenance
Unauthorized
Forbidden
Not Found
Server Error

---

# 14. Responsive Rules

Desktop:
3-panel workspace

Tablet:
2-panel workspace

Mobile:
Single-column navigation
Bottom navigation
Drawer filters

---

# 15. Accessibility

WCAG AA
Keyboard Navigation
Focus Order
ARIA Labels
Reduced Motion
High Contrast

---

# 16. Screen Naming

AUTH_LOGIN
AUTH_MFA
DASHBOARD_HOME
CASE_LIST
CASE_DETAILS
EVIDENCE_UPLOAD
EVIDENCE_VIEWER
INVESTIGATION_WORKSPACE
TIMELINE
GRAPH
AI_ASSISTANT
REPORTS
SETTINGS

---

# 17. Production Checklist

✓ Consistent layout
✓ Design tokens applied
✓ Responsive
✓ Accessible
✓ Error states
✓ Empty states
✓ Loading states
✓ Role-based visibility
✓ Performance optimized
✓ Ready for Figma handoff
✓ Ready for React implementation

This document is the master blueprint for every frontend screen in CrimeKit.
