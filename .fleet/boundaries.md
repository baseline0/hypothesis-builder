# hypothesis-builder Boundaries

## Role
Experimental research project for hypothesis generation and automated test discovery from API specs.

## Scope
- **What we own:** Hypothesis synthesis algorithms, automated test generation framework, research prototypes
- **What we don't own:** Production deployment (experimental phase only)
- **What we provide:** Research artifacts, test generation strategies, API-to-test mapping

## Key Boundaries

### 1. Research Status
- This is an experimental/research project, not production-ready
- APIs and internal structures subject to change without notice
- Use for exploration and prototyping only

### 2. Dependency Boundaries
- **Depends on:** fleet-base (for logging), Python standard library
- **Does NOT depend on:** Other fleet application repos (standalone experimental)
- **Integration:** Can be integrated into fleet-ops once mature

### 3. Protected Paths
- `automation/` — Data and synthesis results (do not commit large outputs)
- `synthesis/` — Generated artifacts (ephemeral)
- `AUTHORIZATION_GATE.md` — Trial/security boundaries (do not modify without review)

## Hard Invariants

### Authorization Gate
- **I-AUTH-001:** No code execution without AUTHORIZATION_GATE.md approval
  - Enforced by: AUTHORIZATION_GATE.md documents trial status
  - Verified by: Manual review before deployment

## Lifecycle
- **Status:** Experimental
- **Layer:** Layer 2 (research/exploration)
- **Maintainer:** Mark Alexiuk
- **Last Updated:** 2026-09-21
