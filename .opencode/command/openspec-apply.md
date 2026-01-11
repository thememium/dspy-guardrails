---
agent: build
description: Implement an approved OpenSpec change and keep tasks in sync.
---
The user has requested to implement the following change proposal. Find the change proposal and follow the instructions below. If you're not sure or if ambiguous, ask for clarification from the user.
<UserRequest>
  $ARGUMENTS
</UserRequest>
<!-- OPENSPEC:START -->
**Ralph Integration Mode**
If `.ralphspec/features.json` exists, this command can operate in Ralph mode:
1. **Identify Task**: 
   - If `$ARGUMENTS` (or `<UserRequest>`) contains a task ID (format: `[change-id]-[number]`), use it.
   - Otherwise, read `.ralphspec/features.json` to find the first incomplete feature, then read its `prd.json` at `.ralphspec/changes/[change-id]/prd.json` for the first incomplete task.
2. **Execute Task**:
   - Read the task details (`title`, `acceptanceCriteria`, `notes`) from the correct `prd.json`.
   - Read `openspec/changes/[change-id]/proposal.md`, `design.md`, and `tasks.md` for context.
   - Implement ONLY the specific task.
   - Mark the checklist item `[x]` in `openspec/changes/[change-id]/tasks.md`.
   - Run typecheck: `npm run type-check` (or project-specific command).
3. **Finish & Update**:
   - Commit with message: `feat: [task title]` (include AI attribution).
   - **CRITICAL: Update prd.json IMMEDIATELY**:
     - Set `passes: true` for the task.
     - Use jq: `jq --arg id "[task-id]" '(.userStories[] | select(.id == $id) | .passes) = true' .ralphspec/changes/[change-id]/prd.json > tmp && mv tmp .ralphspec/changes/[change-id]/prd.json`
   - Update progress file: `.ralphspec/changes/[change-id]/progress.md` with learnings.
4. **STOP** - do not continue to other tasks.

**Note on Commit Footer**:
Use the correct footer based on your CLI tool:
- **Claude Code**: `🤖 Generated with [Claude Code](https://claude.com/claude-code)` and `Co-Authored-By: Claude <noreply@anthropic.com>`
- **OpenCode**: `🤖 Generated with [OpenCode](https://opencode.ai/)` and `Co-Authored-By: OpenCode <noreply@opencode.ai>`


**Guardrails**
- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` (located inside the `openspec/` directory—run `ls openspec` or `openspec update` if you don't see it) if you need additional OpenSpec conventions or clarifications.

**Steps**
Track these steps as TODOs and complete them one by one.
1. Read `changes/<id>/proposal.md`, `design.md` (if present), and `tasks.md` to confirm scope and acceptance criteria.
2. Work through tasks sequentially, keeping edits minimal and focused on the requested change.
3. Confirm completion before updating statuses—make sure every item in `tasks.md` is finished.
4. Update the checklist after all work is done so each task is marked `- [x]` and reflects reality.
5. Reference `openspec list` or `openspec show <item>` when additional context is required.

**Reference**
- Use `openspec show <id> --json --deltas-only` if you need additional context from the proposal while implementing.
<!-- OPENSPEC:END -->
