# Don Aurelius Project & Agent Execution Protocol

## Mandatory Operating System: Get Shit Done (GSD) Protocol

For every task requested in this project, the agent MUST strictly enforce the **Get Shit Done (GSD)** protocol:

1. **Spec-Driven Architecture**:
   - State the exact objective and deliverables before modifying any code.
   - For complex tasks, outline a concise milestone roadmap (`[ ] Step 1`, `[ ] Step 2`, etc.) and check items off as completed.

2. **Context Hygiene (Zero Context Rot)**:
   - Keep the context window lean, focused, and free of junk.
   - Delegate large-scale file reading or exploration to subagents (`research` or `self`) to prevent context window degradation.

3. **Relentless Verification**:
   - Never make unverified assumptions or say "this should work".
   - Proactively run tests, verification scripts, linters, and network checks using `run_command`.
   - Never ask the user to manually verify things that the agent can test directly.

4. **Anti-Slop & Complete Code**:
   - Strictly ban placeholders: `// TODO`, `// ... rest of code`, `/* existing code unchanged */`, or partial snippets.
   - Every modified file must be 100% complete, correct, and production-ready.

5. **Atomic Git Discipline**:
   - Maintain a pristine working tree.
   - Commit verified milestones atomically using standard semantic commit messages (`feat:`, `fix:`, `refactor:`, `test:`).

---

## Mandatory Persistence Engine: Ralph Loop Protocol

1. **Stop-Hook Completion Gate**:
   - The agent is strictly forbidden from declaring completion or stopping while unresolved errors, failing tests, or broken builds exist.
   - If an error or test failure occurs, the agent MUST immediately loop: parse the stack trace, formulate a new hypothesis, apply the fix, and re-verify.

2. **Zero-Surrender Autonomous Self-Correction**:
   - Never stop to ask "What should I do?" or apologize when a build or test fails.
   - If a fix fails twice, shift hypothesis and take an alternative architectural route.

3. **Externalized State Tracking**:
   - Save task state and milestones to disk so progress is durable across turns and sessions.

---

## Mandatory Code Quality Gate: CodeRabbit Protocol

1. **Pre-Commit Static Audit**:
   - Before staging or committing non-trivial changes, audit the diff against CodeRabbit standards (security, memory management, numerical stability, and performance).
   - Enforce domain-specific rules configured in `.coderabbit.yaml`.

2. **Zero Security & Regression Compromise**:
   - Never commit unvalidated inputs, exposed secrets, or relaxed Content Security Policies.
   - Ensure all public functions and modified components have clean error handling.
