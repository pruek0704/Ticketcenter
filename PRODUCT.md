<!-- impeccable:product-schema 1 -->
# TicketCenter

## Product
Thai internal service desk MVP. Employees submit problems and explain their impact; agents of IT, HR, Facilities/Administration (FAC), Finance/Accounting (FIN) and Procurement (PROC) manage their own queue, assess priority and communicate on each ticket. Admins manage cross-department work, accounts, service availability, announcements and audit history.

## Platform
Web: React, FastAPI, PostgreSQL and Nginx. Desktop workspaces and usable mobile layouts. Browser requests use HTTPS and same-origin /api. Cloud deployment has not yet occurred.

## Users and jobs
- Employee: create a normal-priority request, track own requests, exchange messages and read status history.
- Agent: see only their department, triage normal/urgent work, progress Open → In Progress → Done and respond to employees.
- Admin: see both departments, assign eligible agents, administer accounts and configuration and inspect recorded actions.

## Confirmed constraints
Preserve authentication, backend authorization, department routing, persisted settings, confirmation dialogs, unread counts, chat and history. No invented reporting data or cloud deployment claims. Secrets remain outside source. Public Nginx/frontend and private API/database architecture remains unchanged.

## Brand commitment
The user explicitly requested a familiar FreeScout-like inbox and subsequently confirmed practical use and readability as the design goal. Preserve standard sidebar, ticket list, conversation/detail workspace and ordinary forms. Thai text must remain comfortably readable. Department names are full names; agents do not see other department navigation.

## Design workflow preference
Code-first, confirmed by the user on 2026-10-08. Existing functionality is the acceptance baseline. Prefer purposeful detail and feedback over decorative dashboards. The user explicitly rejected the dark green theme, authorized a replacement palette, requested more working space, and requested immediate chat delivery between separately authenticated browser windows. The current palette is blue/slate; chat uses an authenticated server event stream with reconnect and snapshot recovery.
