---
name: laravel-advanced-concepts
description: >
  Advanced Laravel architectural patterns: Feature Flags, State Machines, and Event Sourcing.
  Use this skill whenever a user asks about: toggling features for users/groups, gradual rollouts,
  A/B testing, beta access (→ Feature Flags); modeling workflows like order status, subscription
  lifecycle, booking states, anything with defined transitions (→ State Machines); financial ledgers,
  credit/wallet systems, audit trails, undo history, GDPR-compliant data deletion, analytics replay
  (→ Event Sourcing). Also trigger when users mention spatie/laravel-model-states, Laravel Pennant,
  spatie/laravel-event-sourcing, hirethunk/verbs, or ask "how should I model X in Laravel" for any
  complex domain. This skill provides library recommendations, code patterns, and decision guidance —
  use it proactively whenever the user's domain sounds like it fits one of these patterns.
---

# Laravel Advanced Concepts

Three patterns that solve common but complex problems in Laravel apps. Each has a clear "home turf" — when the problem fits the pattern well, you get enormous benefits; when it doesn't, you're adding accidental complexity.

## Quick Pattern Selector

| Situation | Pattern | Why |
|---|---|---|
| Credit, wallet, points, ledger | Event Sourcing | Every balance change needs an immutable audit trail; balance = sum of events |
| Order status, booking lifecycle | State Machine | Transitions are the business rules; illegal transitions must be prevented at the model level |
| New feature rollout, beta access | Feature Flags | Decouple deploy from release; control who sees what without code changes |
| GDPR "right to be forgotten" | Event Sourcing | Encrypt events per user; "forget" = destroy the key |
| Subscription plan management | State Machine | `active → paused → cancelled` is a classic FSM |
| A/B testing, experiments | Feature Flags | Define variant logic once, measure separately |
| Full audit log / time travel | Event Sourcing | Rebuild state at any point in time from the event stream |

---

## Feature Flags

**Primary library: [Laravel Pennant](https://laravel.com/docs/pennant)** (official, first-party, Laravel 10.2+)

Pennant is the recommended choice for almost all use cases. It ships with Laravel and has first-class support.

### When to use Feature Flags
- Rolling out a new feature to a percentage of users
- Beta programs / early access lists
- A/B testing UI or pricing
- Kill switches for risky features
- Gradual infrastructure migrations (e.g., "10% of traffic uses new payment processor")

### Core concepts
- **Feature**: a named flag that resolves to `true`/`false` (or a variant value)
- **Scope**: what the flag is evaluated against — usually the authenticated user, but can be any model
- **Driver**: where flag state is stored — `database` (per-scope state), `array` (in-memory for tests)

See `references/feature-flags.md` for installation, full API, and patterns.

---

## State Machines

**Primary library: [spatie/laravel-model-states](https://github.com/spatie/laravel-model-states)**

The standard choice for Laravel. Tight Eloquent integration, transition validation, custom transition classes.

### When to use State Machines
- The entity has a `status` field that controls what actions are allowed
- Illegal transitions should be rejected (e.g., can't go from `cancelled` back to `active`)
- You want the transition itself to carry logic (send email, fire event, update timestamps)
- Multiple places in your code change the same status and you need consistency

### When NOT to use State Machines
- The "states" are just labels with no transition logic — a plain `enum` is simpler
- Transitions are completely unrestricted — just update the field directly

See `references/state-machines.md` for installation, state/transition classes, and patterns.

---

## Event Sourcing

**Primary libraries:**
- **[spatie/laravel-event-sourcing](https://github.com/spatie/laravel-event-sourcing)** — mature, full-featured, well-documented
- **[hirethunk/verbs](https://verbs.thunk.dev/)** — newer, opinionated, simpler API, excellent for new projects

### When to use Event Sourcing
- Financial data: credits, debits, wallet balances, points — **the canonical use case**
- You need a complete audit log that cannot be altered
- You need to replay history to rebuild state (analytics, projections, debugging)
- GDPR compliance: per-user encryption keys let you "forget" a user by deleting their key
- The domain is complex enough that understanding "how did we get here" matters

### When NOT to use Event Sourcing
- Simple CRUD with no audit requirements — overhead isn't worth it
- The team is unfamiliar with event sourcing — it's a significant mental model shift
- You just need soft deletes + timestamps — that's usually enough

### Choosing between Spatie and Verbs
- **Spatie**: battle-tested, more users/resources, traditional event sourcing concepts (Aggregates, Projectors, Reactors)
- **Verbs**: simpler syntax, type-safe state, better for greenfield projects, fewer concepts to learn

See `references/event-sourcing.md` for installation, aggregates, projectors, and patterns for both libraries.

---

## Combining Patterns

These patterns compose well:

- **State Machine + Event Sourcing**: record each state transition as an event. The state machine enforces valid transitions; the event log gives you full history. Good for order workflows where you need both correctness and auditability.
- **Feature Flags + anything**: use Pennant to gate access to new aggregates or state machine variants during a migration.
