# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 8 — Enterprise Knowledge Graph Visualization
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 8

Objective:

Develop ONLY the Enterprise Knowledge Graph module.

This is the intelligence visualization engine of CrimeKit.

It visualizes every relationship discovered by the backend AI pipeline,
Neo4j Knowledge Graph,
RAG Pipeline,
Entity Extraction,
Timeline Extraction,
Evidence Correlation,
and Investigation Engine.

This is NOT a graph demo.

This is NOT a static diagram.

This is NOT generated inside the frontend.

Everything MUST come from the existing Neo4j-powered backend.

NO mock nodes.

NO fake edges.

NO hardcoded graph.

Everything must be rendered from backend APIs.

This module should feel comparable to:

• Palantir Gotham Graph
• IBM i2 Analyst Notebook
• Maltego
• Linkurious Enterprise
• Neo4j Bloom
• Cellebrite Pathfinder Relationship Explorer
• Magnet AXIOM Connections

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal Graph Visualization Engineer

Principal AI UX Architect

Principal React Architect

Principal Cytoscape Engineer

Principal React Flow Engineer

Principal Neo4j Visualization Architect

Principal Investigation Platform Architect

Senior Product Designer

------------------------------------------------------------------------------

# SOURCE OF TRUTH

Before writing ANY code

Read EVERYTHING.

Priority

1.

graphify-out/

graph.json

GRAPH_REPORT.md

2.

Planning/

Knowledge Graph Planning

AI Planning

Workspace Planning

Investigation Planning

3.

Architecture/

4.

Knowledge Graph Constitution

5.

Frontend Constitution

6.

Backend Constitution

7.

Neo4j APIs

8.

Knowledge Graph APIs

9.

AI APIs

10.

Entity Extraction APIs

11.

Timeline APIs

12.

Evidence APIs

13.

Case APIs

14.

Search APIs

15.

Workspace APIs

16.

Compliance APIs

17.

OpenAPI

18.

Existing Frontend

19.

Existing Components

20.

Existing Design System

Never redesign.

Never invent APIs.

Reuse existing architecture.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Create fake graph

Create random nodes

Generate relationships

Hardcode Neo4j data

Duplicate graph algorithms

Duplicate AI

Duplicate backend logic

Duplicate graph layout

Everything MUST come from backend APIs.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Knowledge Graph Visualization

Includes

✓ Interactive Graph

✓ Entity Visualization

✓ Relationship Visualization

✓ Search

✓ Filters

✓ Node Details

✓ Edge Details

✓ Multi-hop Expansion

✓ Graph Navigation

✓ Graph Export

✓ Graph Analytics

✓ Graph Legends

✓ Backend Integration

Nothing else.

------------------------------------------------------------------------------

# GRAPH PURPOSE

The Knowledge Graph represents the entire investigation.

Every AI-discovered relationship should become an interactive graph.

Examples

Person

↓

Email

↓

Device

↓

Browser

↓

Downloaded File

↓

Process

↓

Registry

↓

Network

↓

URL

↓

Timeline

↓

Case

↓

Evidence

Everything must be visualized.

------------------------------------------------------------------------------

# VISUALIZATION ENGINE

Preferred

React Flow

OR

Cytoscape.js

Choose whichever best fits the backend graph.

Requirements

Large graph support

Virtualization

Smooth pan

Zoom

Selection

Context Menu

Node Groups

Collapse

Expand

Animated layout

Performance optimized

------------------------------------------------------------------------------

# GRAPH LAYOUTS

Support

Force Directed

Hierarchical

Circular

Radial

Tree

Dagre

Concentric

Grid

Auto Layout

User can switch layouts.

Persist preference.

------------------------------------------------------------------------------

# NODE TYPES

Visualize

Person

Device

Computer

Laptop

Phone

Email

Email Address

Browser

Browser History

Cookie

URL

IP Address

Domain

Hostname

Process

Registry

Service

Application

File

Folder

PDF

Image

Video

Audio

Office Document

ZIP

RAR

Memory Artifact

Disk Artifact

Timeline Event

Evidence

Case

Organization

Investigator

Report

Location

GPS

WiFi

Bluetooth

Social Account

WhatsApp

Telegram

Signal

SMS

Call

Photo

Video Frame

AI Entity

Knowledge Entity

Everything comes from backend.

------------------------------------------------------------------------------

# EDGE TYPES

Display

Communicates With

Downloaded

Uploaded

Created

Modified

Deleted

Connected To

Owns

Uses

Visited

Logged Into

Executed

Generated

Extracted

Contains

References

Appears In

Related To

Mentioned In

Shared Hash

Shared Device

Shared Person

Shared Location

Timeline Relation

AI Correlation

KG Relation

Processing Relation

------------------------------------------------------------------------------

# GRAPH CONTROLS

Support

Zoom In

Zoom Out

Fit View

Center Graph

Reset Layout

Collapse

Expand

Undo

Redo

Mini Map

Fullscreen

Search

Selection

Multiple Selection

Context Menu

Keyboard Shortcuts

------------------------------------------------------------------------------

# SEARCH

Backend Search

Support

Person

Email

Device

Hash

URL

IP

File

Evidence

Case

Entity

Timeline

Relationship

Organization

Tag

No frontend graph search.

------------------------------------------------------------------------------

# FILTERS

Backend filters

Entity Type

Relationship Type

Evidence Type

Timeline

Case

Date

AI Confidence

Risk Level

Processing Status

Organization

Department

------------------------------------------------------------------------------

# NODE DETAILS PANEL

Selecting a node displays

Entity ID

Entity Type

Name

Description

Properties

Metadata

Evidence References

Timeline Events

Related Entities

Related Cases

AI Findings

Processing Results

Knowledge Confidence

Risk Score

Quick Actions

Everything from backend.

------------------------------------------------------------------------------

# EDGE DETAILS PANEL

Display

Relationship

Source

Target

Confidence

Created By

AI Source

Timeline Source

Evidence Source

Weight

Metadata

Quick Actions

------------------------------------------------------------------------------

# MULTI-HOP EXPANSION

Support

1 Hop

2 Hop

3 Hop

Custom Depth

Lazy Load

Backend expansion only.

Never expand locally.

------------------------------------------------------------------------------

# GRAPH ANALYTICS

Display

Node Count

Edge Count

Communities

Connected Components

Most Connected Entity

Centrality

Graph Density

Evidence Coverage

AI Confidence

Everything from backend.

------------------------------------------------------------------------------

# RELATED TIMELINE

Selecting a node should

Highlight timeline events.

Open workspace.

Open evidence.

Open case.

Open processing.

Everything synchronized.

------------------------------------------------------------------------------

# EXPORT

Backend only.

Support

PNG

SVG

PDF

GraphML

JSON

Neo4j Export

Investigation Snapshot

Court Export

------------------------------------------------------------------------------

# REALTIME

Support

Polling

WebSocket (if backend supports)

Incremental updates

Live node insertion

Live edge insertion

Refresh

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API layer.

Integrate

Knowledge Graph APIs

Neo4j APIs

Entity APIs

Evidence APIs

Timeline APIs

Case APIs

AI APIs

Workspace APIs

Search APIs

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Graph Store

Selection Store

Layout Store

Filter Store

Search Store

No duplicate state.

------------------------------------------------------------------------------

# LOADING

Graph Skeleton

Node Skeleton

Edge Skeleton

Analytics Skeleton

Details Skeleton

Progressive loading.

------------------------------------------------------------------------------

# ERROR HANDLING

Handle

401

403

404

429

500

Neo4j unavailable

Timeout

Offline

Retry

Graph too large

Per-panel isolation.

------------------------------------------------------------------------------

# EMPTY STATES

No Graph

No Entities

No Relationships

No Search Results

No Permission

Backend Offline

------------------------------------------------------------------------------

# PERFORMANCE

Graph Virtualization

Lazy Expansion

Incremental Rendering

Memoization

Chunk Loading

Viewport Rendering

Streaming

Worker-based Layout Calculation

Large Graph Optimization

Support graphs with 100,000+ nodes.

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2 AA

Keyboard Navigation

ARIA

Screen Reader

Focus Management

High Contrast

Reduced Motion

Accessible Graph Controls

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Large Monitor

Ultra-wide

Tablet (limited exploration mode)

Maintain enterprise layout.

------------------------------------------------------------------------------

# SECURITY

Respect backend RBAC.

Never expose

Hidden Entities

Restricted Evidence

Hidden Relationships

Other Organizations

Confidential Nodes

Private AI Findings

------------------------------------------------------------------------------

# AUDIT

Graph interactions

Node Open

Edge Open

Expand

Export

Search

Filter

Must call backend audit APIs.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Graph loads

✓ Live Neo4j integration works

✓ Nodes render correctly

✓ Relationships render correctly

✓ Search works

✓ Filters work

✓ Layout switching works

✓ Multi-hop expansion works

✓ Node details work

✓ Edge details work

✓ Timeline integration works

✓ Workspace integration works

✓ Export works

✓ Analytics work

✓ Existing design preserved

✓ Existing components reused

✓ No mock data

✓ No runtime errors

✓ No TypeScript errors

✓ No ESLint errors

✓ Production-ready

------------------------------------------------------------------------------

# DELIVERABLES

Produce

1.

Knowledge Graph Architecture

2.

Neo4j Integration Flow

3.

Backend API Mapping

4.

Graph Rendering Architecture

5.

Component Hierarchy

6.

Node Type Specification

7.

Relationship Specification

8.

Layout Strategy

9.

Performance Strategy

10.

Files Created

11.

Files Modified

12.

Files Reused

13.

Security Report

14.

Accessibility Report

15.

Knowledge Graph Validation Report

16.

Knowledge Graph Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

AI Chat

Reports

Compliance

Administration

Settings

Stop immediately after the Enterprise Knowledge Graph module is fully integrated with the existing Neo4j-powered backend and all validation criteria pass.

Only after successful completion should Phase 9 (Enterprise AI Intelligence Center) begin.