---
name: orchestrate
description: Master orchestration skill for ClassManager. Analyzes every incoming task, activates the correct skill combination, loads only the necessary context, gates ambiguity before coding, and self-verifies output before responding.
---

# Orchestrate — ClassManager Agent Director

Before executing any task, run through this file top to bottom.
Do not skip any phase. Do not write a single line of code until Phase 4 clears.

---

## Phase 1 — Task Classification

Read the user's request and classify it into exactly one of the following types.
State the classification explicitly before proceeding.

| Type | Description | Example |
|------|-------------|---------|
| `NEW_FEATURE` | Building something that does not yet exist | "Add OTP login for students" |
| `MODIFY` | Extending or changing existing code | "Add rejection reason to teacher approval" |
| `BUG_FIX` | Fixing a specific broken behavior | "Weekly lock cron runs at wrong timezone" |
| `REFACTOR` | Improving code without changing behavior | "Extract point calculation into a utility" |
| `QUESTION` | Explanation, analysis, or advice — no code output | "Why do we use immutable logs?" |

> If the task spans multiple types (e.g., fix a bug AND refactor), treat it as the highest-impact type and note the secondary type.

---

## Phase 2 — Skill Activation

Activate skills based on which **layers are actually touched**, not just the task surface.
Always activate `full-output-enforcement` — no exceptions.

### Layer → Skill mapping

| Layer touched | Skill to activate |
|---------------|-------------------|
| Any layer | `/full-output-enforcement` ← always |
| JPA Entity, Repository, Service, Controller, DTO | `/spring-backend-expert` |
| `point_logs`, `weekly_reports`, Cron Job, OTP, Class end/freeze | `/postgresql-transactions` |
| React component, page, hook, service, type | `/react-frontend-expert` |
| UI layout, color, spacing, table, chart, badge | `/minimalist-ui` |

### Common combinations

```
New backend endpoint:
  /spring-backend-expert + /full-output-enforcement

Cron Job or audit log:
  /postgresql-transactions + /spring-backend-expert + /full-output-enforcement

New React page with data table:
  /react-frontend-expert + /minimalist-ui + /full-output-enforcement

Full-stack feature (BE + FE):
  /spring-backend-expert + /postgresql-transactions (if DB write)
  + /react-frontend-expert + /minimalist-ui (if UI involved)
  + /full-output-enforcement

Bug fix (BE only):
  /spring-backend-expert + /full-output-enforcement
  + /postgresql-transactions (if bug involves transactions)
```

### Combination warnings

```
⚠️  Writing Cron Job without /postgresql-transactions
    → Risk: race condition on weekly_report insert

⚠️  Writing point-related service without /postgresql-transactions
    → Risk: accidental UPDATE or cached total read

⚠️  Full-stack task with only one skill activated
    → Risk: missing conventions on the other layer

⚠️  Writing Dashboard UI without /minimalist-ui
    → Risk: inconsistent color usage for at-risk badges
```

---

## Phase 3 — Context Loading

Load only what is needed for the task type. Do not read the entire SRS for every task.

### NEW_FEATURE
```
Required:
  docs/AGENT.md                              ← constraints & implementation flow
  docs/02-domain/business-rules.md           ← all BR-* relevant to the feature
  docs/03-data/database-schema.md            ← tables being touched
  docs/04-api/<resource>-api.md              ← API contract for this resource
  docs/02-domain/permissions.md              ← which roles can access this

Load if needed:
  docs/SRS.md                                ← full context when spec is ambiguous
  docs/02-domain/domain-model.md             ← entity relationships
```

### MODIFY
```
Required:
  docs/02-domain/business-rules.md           ← BR relevant to the change
  The existing file(s) being modified        ← read current implementation first

Load if needed:
  docs/04-api/<resource>-api.md              ← only if API contract changes
  docs/02-domain/permissions.md              ← only if role logic changes
```

### BUG_FIX
```
Required:
  The broken file(s)                         ← read current implementation
  docs/02-domain/business-rules.md           ← verify what correct behavior is

Do NOT load:
  Unrelated API specs, full SRS, domain model ← unnecessary noise
```

### REFACTOR
```
Required:
  docs/05-architecture/coding-conventions.md ← target conventions
  The file(s) being refactored

Do NOT load:
  Business rules, API specs                  ← behavior is not changing
```

### QUESTION
```
Load what is directly relevant to the question.
No code output required — answer clearly and cite the source doc.
```

---

## Phase 4 — Clarification Gate

**Do not write any code until all questions below are resolved.**

Answer each question explicitly. If any answer is unclear, ask the user before proceeding.

```
□ SCOPE
  Which files / layers will this task touch?
  Is this backend only, frontend only, or full-stack?

□ DATA
  Which DB tables are involved?
  Are there any write operations? (→ triggers postgresql-transactions)
  Does this touch point_logs in any way? (→ immutable, no UPDATE/DELETE)

□ PERMISSIONS
  Which roles are allowed to perform this action?
  Is this covered by the existing permission matrix?
  Does the JWT payload contain all needed claims?

□ BUSINESS RULES
  Which BR-* rules apply to this task?
  Is there any BR that could be violated by the naive implementation?

□ DEPENDENCIES
  Does the required Entity exist?
  Does the required Repository / Service exist?
  Does the API endpoint exist (for FE tasks)?

□ OUTPUT FORMAT
  Is the expected output a new file, a modification to an existing file,
  or an explanation with no code?
  For API changes: does the response shape match the SRS contract?
```

> If any box cannot be checked with confidence → stop and ask the user.
> Do not make assumptions on ambiguous business rules.

---

## Phase 5 — Output Checklist

Before returning any output, self-verify against this checklist.
If any item fails → fix before responding.

### Backend checks
```
□ @Transactional placed at Service layer only (never Controller)
□ @Transactional(readOnly = true) on all read-only methods
□ No UPDATE or DELETE on point_logs
□ Current point calculated from SUM(point_logs), never from cached field
□ Custom exception thrown from Service, caught in @RestControllerAdvice
□ Request and Response DTOs are separate from JPA Entities
□ All request fields validated with Bean Validation annotations
□ assertClassActive() called before any write operation
□ weekly_report.is_locked checked before adding point_log
□ Error response matches the standard format (timestamp, status, error, message, details, path)
□ No hardcoded URLs, secrets, or credentials — all read from ${ENV_VAR}
□ Audit Log emitted for sensitive mutations (BR-AUDIT-02) with old_value/new_value JSONB
□ Compiles cleanly: ./mvnw compile
```

### Cron Job specific checks
```
□ Cron expression: 0 59 23 * * SUN
□ Timezone: Asia/Ho_Chi_Minh (not UTC)
□ is_locked checked before processing — skip if already locked
□ saveAll() used for batch insert — never save() in a loop
□ Exception caught inside the scheduler — never re-thrown
□ INFO log at start and end with record count
□ UNIQUE (student_id, week_start_date) violation caught gracefully
```

### Frontend checks
```
□ No use of `any` type — all API data typed with interface or type
□ All API calls go through src/services/ — no direct axios in components
□ Loading state: Skeleton shown while fetching (not spinner for tables)
□ Error state: ApiError.message displayed on failure
□ Role-based Route Guards in place for protected pages
□ No hardcoded URLs — all from import.meta.env.VITE_*
□ Point badge uses correct semantic colors (green/blue/amber/red)
□ Lint passes: npm run lint && npx tsc --noEmit
□ Component modularity: No monolithic component/page files (files exceeding 300 lines should be split into modular subcomponents under components/)
```

### Universal checks
```
□ No // TODO, // ..., or placeholder comments
□ No incomplete logic left for "later"
□ Code is consistent with existing patterns in the codebase
□ Output is complete and immediately usable
```

---

## Phase 6 — Edge Case Handling

### Full-stack tasks (BE + FE in one task)
```
1. Implement and verify backend first
2. Confirm the API response shape before writing frontend
3. Write TypeScript interface to exactly match the API response
4. Write the frontend service call
5. Build the UI component last
Never implement FE against an assumed API shape.
```

### Tasks touching point_logs
```
Always ask: "Is this a write operation on point_logs?"
  Yes → activate /postgresql-transactions
        enforce immutability (INSERT only)
        verify week_start_date is not locked
        verify student is in leader's group (if GROUP_LEADER)
  No  → proceed with standard read logic
```

### Tasks adding a new Role or Permission
```
1. Update docs/02-domain/permissions.md first
2. Update JWT payload claims if the new role needs different data
3. Add @PreAuthorize or manual check in Service layer
4. Add Route Guard in frontend router
5. Update permission matrix in AGENT.md if structural change
Never add role logic in only one layer.
```

### Tasks touching Class Status
```
Every write operation must call assertClassActive() first.
Read operations on ENDED classes are allowed (audit trail).
Never allow new point_logs for an ENDED class.
```

### Refactoring tasks
```
1. Read the current implementation fully before changing anything
2. Write the refactored version
3. Verify behavior is identical — no business logic changes
4. Run relevant tests before declaring done
```

### Bug fix tasks
```
1. Identify the exact BR-* rule being violated
2. Reproduce the bug scenario in a comment before fixing
3. Fix only the broken behavior — do not refactor unrelated code
4. Add a note explaining why the fix is correct per the BR
```