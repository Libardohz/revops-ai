# Superpowers Development Methodology

This workspace has the **Superpowers** skills framework installed in `.agents/skills/`.

## Core Superpowers Workflow Rules

1. **Check and Invoke Skills First**:
   - Before taking action or responding to creative/architectural or troubleshooting tasks, check if a skill in `.agents/skills/` applies.
   - If a skill applies, invoke and follow the skill instructions.

2. **Skill Priority & Routing**:
   - **Frontend styling & UI/UX design**: Use `anti-ai-design` and `hallmark` to enforce bespoke, handcrafted, high-end design engineering, prevent generic AI slop, audit components, or redesign interfaces.
   - **New features / modifications / building**: Use `brainstorming` before implementation or writing plans.
   - **Bug fixes / unexpected behavior**: Use `systematic-debugging` to trace root cause before proposing fixes.
   - **Multi-step implementations**: Use `writing-plans` to specify step-by-step tasks, then execute using `subagent-driven-development` or `executing-plans`.
   - **Code implementation**: Adhere strictly to `test-driven-development` (TDD - red/green/refactor).
   - **Before claiming work complete**: Use `verification-before-completion` to run tests and verify behavior with evidence.
   - **Code review**: Use `requesting-code-review` and `receiving-code-review`.

3. **Task Tracking in Antigravity**:
   - When skills require creating or managing a checklist/todo, use a markdown task artifact or plan artifact rather than background process management.
