---
artifact_type: plan
status: approved            # draft | approved
owner: Alberto Galimberti
last_updated: 2026-10-19
---

# PLAN — release plan

> Living document, owned by the PO. Agents read it and do not change it, except the "Status" column after reconciliation.

## 1. Objective
R1 delivers a secured local portal (`make portal`) that shows workflow state, plan and backlog, launches workflow steps with the tier model, streams runs, stops at human gates and lets the owner approve or request changes — working on a greenfield and on an adopted repository. R2 adds codebase health and settings; R3 turns findings into actions.

## 2. Releases

| Release | Content | Target | Exit criterion |
|---|---|---|---|
| R1 | EP-01, EP-02 (Must), EP-03, EP-04 | 2026-11-20 | On a greenfield and an adopted repo: `make portal` starts from the bundle, a step is launched, streamed and stopped at a gate, and the gate is passed only through the portal by a human |
| R2 | EP-05 (AP0501–AP0505), EP-06, AP0205, AP0206 | 2026-12-04 | Weak files, security, untested code and diagrams visible; settings and theme available |
| R3 | AP0506 | 2026-12-04 | A finding can be turned into a launched workflow action |

## 3. Sprints

> Parsed by `tools/next_step.py`: keep the 4 columns; list story IDs or epic IDs (EP-xx) in the last one. Order inside a sprint = development order.
> Owner constraints: 1-week sprints, capacity 12 points/sprint (S=1, M=2, L=3). start 2026-10-19.

| Sprint | Dates | Goal | Stories |
|---|---|---|---|
| S0 | 19/10 – 23/10 | Analysis | Analysis and workshops of S1–S2 |
| S1 | 26/10 – 30/10 | Foundations: skeleton, security, upstream contract and launcher, app shell | AP0101, AP0103, AP0106, AP0108, AP0102, AP0110, AP0109 |
| S2 | 02/11 – 06/11 | Contract client, gates, bundle, first views | AP0104, AP0105, AP0107, AP0201, AP0202, AP0203 |
| S3 | 09/11 – 13/11 | Story detail, portability, launch and streaming | AP0204, AP0207, AP0301, AP0302, AP0303, AP0304 |
| S4 | 16/11 – 20/11 | Human gates (R1 closure) | AP0305, AP0401, AP0402, AP0403, AP0404 |
| S5 | 23/11 – 27/11 | Health framework, settings, navigation | AP0501, AP0503, AP0502, AP0601, AP0205, AP0206, AP0505 |
| S6 | 30/11 – 04/12 | Remaining analyzers, theme, findings to actions | AP0504, AP0602, AP0506 |

## 4. Risks and assumptions
- 12 points per 1-week sprint leaves almost no slack in S1–S5 (11–12 points each); S6 (5 points) is the only buffer.
- S4 is one serial chain (AP0305 → AP0401 → AP0402 → AP0403 → AP0404): any delay pushes R1 past 2026-11-20.
- AP0103, AP0105 and AP0106 are upstream changes to the skeleton; the portal is blocked from S2 if they are not merged.
- Analysis runs one sprint ahead: S0 must analyse 11 stories in one week.
- Headless agent CLI streaming (AP0303) is an unvalidated assumption (vision §8).

## 5. Decisions
- 2026-10-19 (owner): start date 2026-10-19; R2 and R3 ship together on 2026-12-04; plan approved.
