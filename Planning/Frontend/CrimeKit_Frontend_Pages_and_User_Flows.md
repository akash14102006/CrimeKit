# CrimeKit Frontend Pages & User Flows

# Purpose

This document defines every frontend page, navigation flow, user
journey, and screen responsibility for CrimeKit.

------------------------------------------------------------------------

# Global Navigation

Top Navigation - Global Search - Notifications - AI Assistant -
Profile - Settings

Sidebar - Dashboard - Cases - Evidence - Investigation - Timeline -
Knowledge Graph - Reports - AI Assistant - Administration - Settings

------------------------------------------------------------------------

# Authentication

## Login

-   Email
-   Password
-   MFA
-   Remember Me

## Forgot Password

## Reset Password

## Session Timeout

Flow: Login → MFA → Dashboard

------------------------------------------------------------------------

# Dashboard

Widgets - KPI Cards - Active Cases - Recent Evidence - AI Insights -
Investigation Queue - Recent Activity - Alerts

Actions - Create Case - Upload Evidence - Start Investigation

------------------------------------------------------------------------

# Case Management

Pages - Case List - Create Case - Case Details - Team Members - Notes -
Attachments

Flow Dashboard → Cases → Case Details

------------------------------------------------------------------------

# Evidence Module

Pages - Upload - Evidence Library - Metadata - OCR - Hash - Preview - AI
Analysis

Supported Types - Images - Videos - Audio - Documents - Mobile Dumps -
Disk Images

Flow Case → Upload → Processing → AI → Investigation

------------------------------------------------------------------------

# Investigation Workspace

Three Panel Layout

Left - Evidence Tree

Center - Viewer

Right - Metadata - AI Findings - Notes

Actions - Tag - Bookmark - Link Evidence - Generate Timeline

------------------------------------------------------------------------

# Timeline

Views - Day - Week - Month

Features - Zoom - Filters - Categories - Export

------------------------------------------------------------------------

# Knowledge Graph

Entities - Person - Device - Vehicle - Location - Organization

Relations - Calls - Messages - Financial - Social - Physical

Features - Search - Expand - Collapse - Highlight Path

------------------------------------------------------------------------

# AI Assistant

Capabilities - Chat - Explain Evidence - Summarize Case - Suggest
Leads - Generate Reports

Panels - Chat - References - Actions - History

------------------------------------------------------------------------

# Reports

Templates - Investigation - Court - Executive - Technical

Exports - PDF - DOCX

------------------------------------------------------------------------

# Administration

Users Roles Permissions Audit Logs System Health

------------------------------------------------------------------------

# Settings

Profile Appearance Notifications Security API Keys

------------------------------------------------------------------------

# Responsive Behaviour

Desktop - Full Workspace

Tablet - Collapsible Sidebar

Mobile - Single Panel Navigation - Bottom Navigation

------------------------------------------------------------------------

# Common UI States

Loading Empty Error Offline Permission Denied No Results Processing

------------------------------------------------------------------------

# End-to-End User Flow

Login → Dashboard → Create Case → Upload Evidence → AI Processing →
Investigation → Timeline → Knowledge Graph → Report Generation → Export
→ Archive Case

This document should be used together with the Frontend Design System as
the implementation blueprint for every screen in CrimeKit.
