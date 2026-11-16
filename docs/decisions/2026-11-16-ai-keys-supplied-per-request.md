# AI Provider Keys Are Supplied Per Request

**Status:** Accepted
**Date:** 16 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

As in the Qt app, users enter their own AI provider key (Gemini, OpenAI, Azure OpenAI, OpenRouter, Groq, and in the web app Anthropic)
with each explanation request. The API uses the key once and never stores, logs, or returns it: it is a
`SecretStr` hidden from `repr`, request validation errors log only field paths and error types, and
provider error bodies are logged only after the key is removed. No provider key is configured in env files.

## Context

The Qt app held keys in memory only. A server-side key would make the operator pay for every user's
requests and would need access control the stateless API does not have.

## Alternatives Considered

- **One server-side key per provider:** simpler for users, but needs accounts and rate limits.
- **Keys stored per user:** needs accounts, encryption at rest, and a store.

## Consequences

- Keys travel in request bodies: **HTTPS must be enabled in Nginx before the AI explanation is used on the
  VPS** (the HTTPS block is prepared but commented out).
- Provider failures map to distinct public messages (rejected key 502, rate limit 502, timeout 504, other
  502) without echoing the provider's raw response.

## Related Work

- Plan: [Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](../plans/2026-11-16-port-backend-to-fastapi-api-plan.md)
- Decision: [Each service has its own env file](./2026-11-16-each-service-has-its-own-env-file.md)
