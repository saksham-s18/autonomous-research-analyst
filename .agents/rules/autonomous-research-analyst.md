---
trigger: always_on
---

# Autonomous Research Analyst — Permanent Project Rules

## Project

This repository is the Autonomous Research Analyst portfolio project.

The project follows a 15-day roadmap. The current architecture and previous implementation decisions must be preserved unless explicitly changed by the user.

## Architecture

Current core stack:

- Python 3.12
- FastAPI
- LangGraph
- PostgreSQL
- SQLAlchemy async
- Alembic
- Pydantic
- Redis
- pytest
- Docker

Do not replace or redesign the existing architecture without explicit user approval.

In particular:

- Do not replace LangGraph.
- Do not replace PostgreSQL.
- Do not replace SQLAlchemy.
- Do not replace FastAPI.
- Do not introduce LangGraph native checkpointing.
- Preserve the existing application-level PostgreSQL checkpoint mechanism.
- Do not introduce new infrastructure merely because it is popular.

## Architecture Principle

LLMs perform reasoning and generation.

Python performs deterministic:

- orchestration
- routing
- validation
- lifecycle management
- persistence
- retries
- checkpointing
- progress calculation
- evidence handling
- citation mapping
- API behavior

Do not delegate deterministic application logic to an LLM when Python can perform it reliably.

## Evidence and Traceability

The system is evidence-first.

Do not weaken:

- evidence traceability
- source tracking
- citation mapping
- conflict detection
- research provenance

Prefer deterministic citation mapping and validation whenever possible.

## Research Workflow

Preserve the existing workflow structure and meaningful status lifecycle.

Do not invent a generic "running" status.

Existing meaningful statuses include states such as:

- pending
- planning
- researching
- synthesizing
- synthesis_failed

Do not change status semantics without explicit approval.

## Checkpointing

The project uses application-level PostgreSQL checkpoint persistence.

Preserve:

- workflow_state
- checkpoint persistence
- resume behavior
- retry behavior
- persisted research state

Do not replace this with LangGraph native checkpointing unless explicitly instructed.

## API

Preserve the existing API lifecycle:

POST /api/research

GET /api/research

GET /api/research/{research_id}/status

GET /api/research/{research_id}

DELETE /api/research/{research_id}

Do not add duplicate endpoints when existing functionality already satisfies the requirement.

The existing GET /api/research/{research_id} endpoint already provides persisted research result information including final_report and confidence.

## Testing

Every meaningful behavior change must have appropriate tests.

Always:

1. Run focused tests after implementation.
2. Run broader relevant tests before declaring the task complete.
3. Never claim tests passed unless they were actually executed.

Pytest normally runs from the backend directory because backend/.env is used by the application configuration.

## Git

Use genuine incremental Git history.

Do not:

- fabricate commits
- create spam commits
- manipulate contribution history
- create meaningless commits
- make giant unrelated commits

Prefer small, logical commits with natural messages.

Before committing:

- inspect git status
- inspect git diff
- inspect changed files
- run relevant tests

Never commit or push unless the user explicitly approves it.

## Files That Must Not Be Committed

Never commit:

- .env
- secrets
- API keys
- passwords
- credentials
- tokens
- __pycache__
- .pytest_cache
- generated build artifacts
- backend.egg-info/

## Database

Before creating an Alembic migration:

1. Verify that the database schema actually needs a change.
2. Inspect existing migrations.
3. Avoid migrations for application-only changes.

Never create a migration simply because a Pydantic schema changed.

## Code Quality

Prefer:

- simple code
- explicit behavior
- type hints
- focused functions
- clear names
- existing project conventions
- minimal abstractions
- useful tests

Avoid:

- unnecessary refactoring
- unnecessary abstractions
- dead code
- unrelated formatting changes
- speculative infrastructure
- rewriting working components

## Change Discipline

For every task:

1. Inspect the existing implementation first.
2. Understand the current architecture.
3. Explain the proposed plan.
4. Make the smallest correct change.
5. Run tests.
6. Inspect the final diff.
7. Report what changed.
8. Stop before committing unless the user explicitly approves the commit.

Never silently redesign the project.

## Roadmap Discipline

Follow the authoritative 15-day roadmap.

Do not invent a different objective for the current day.

Current project state:

- Days 1–10 are complete.
- Day 11 is Observability.
- Day 12 is Frontend / polished API presentation.
- Day 13 is Performance.
- Day 14 is Docker / CI/CD / deployment.
- Day 15 is Final integration / documentation / demo / portfolio polish.

Do not jump ahead unless explicitly asked.

## Portfolio Quality

This project is intended for an AI/ML internship portfolio.

Implementations must be understandable and explainable in an interview.

Prefer explicit, traceable engineering decisions over clever abstractions.

The user should be able to explain why a component exists and how it works.

## Agent Behavior

Do not modify files immediately when given a broad task.

First inspect the repository and provide an implementation plan.

For substantial tasks, wait for user approval before implementation.

Do not commit or push without explicit approval.