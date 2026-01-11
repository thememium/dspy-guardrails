# /ralphspec:generate-prd

Generate prd.json task breakdown from an OpenSpec proposal's tasks.md.

## Usage

```
/ralphspec:generate-prd <change-id>
```

## Instructions

When this command is invoked:

1. **Validate the change exists**:
   - Check `openspec/changes/<change-id>/tasks.md` exists
   - If not, error with: "No proposal found. Run /openspec:proposal <change-id> first"

2. **Read the OpenSpec files**:
   - `openspec/changes/<change-id>/tasks.md` - for task checklist
   - `openspec/changes/<change-id>/proposal.md` - for context
   - `openspec/changes/<change-id>/design.md` - for implementation details

3. **Parse tasks.md checklist items**:
   - Each `- [ ]` checkbox item becomes a userStory
   - Preserve the exact task title from the checklist
   - Infer acceptance criteria from context

4. **Generate userStory for each task**:
```json
{
  "id": "<change-id>-<task-number>",
  "branchName": "ralph/<change-id>",
  "title": "Exact title from tasks.md checklist",
  "acceptanceCriteria": [
    "Inferred criterion based on task",
    "Additional criterion from design.md context"
  ],
  "priority": <task-number>,
  "passes": false,
  "notes": "Implementation hints from design.md, file paths, patterns to follow",
  "dependencies": ["<change-id>-<previous-task>"],
  "subtasks": []
}
```

5. **Dependency rules**:
   - First task has empty dependencies: `[]`
   - Each subsequent task depends on the previous: `["<change-id>-N"]`
   - If tasks are clearly independent, omit dependencies

6. **Create `.ralphspec/changes/<change-id>/prd.json`**:
   - Create the directory `.ralphspec/changes/<change-id>/` if it doesn't exist
   - Create prd.json in that directory (each feature has its own prd.json)

7. **Mark feature as proposal created**:
   - Update `.ralphspec/features.json`: set `proposalCreated: true` for this feature

8. **Output** summary:
   - Number of tasks generated
   - List of task titles
   - Next steps

## Example

**Input:**
```
/ralphspec:generate-prd add-dark-mode
```

**Given tasks.md:**
```markdown
## Tasks

- [ ] Create ThemeContext provider with light/dark mode support
- [ ] Add theme toggle component to Settings page
- [ ] Persist theme preference to localStorage
- [ ] Update global styles to use CSS variables for theming
- [ ] Run typecheck and fix any type errors
```

**Generated prd.json:**
```json
{
  "userStories": [
    {
      "id": "add-dark-mode-1",
      "branchName": "ralph/add-dark-mode",
      "title": "Create ThemeContext provider with light/dark mode support",
      "acceptanceCriteria": [
        "ThemeContext created with light/dark values",
        "ThemeProvider component wraps application",
        "useTheme hook exported for consuming components"
      ],
      "priority": 1,
      "passes": false,
      "notes": "Create in src/contexts/ThemeContext.tsx. Follow existing context patterns in the codebase.",
      "dependencies": [],
      "subtasks": []
    },
    {
      "id": "add-dark-mode-2",
      "branchName": "ralph/add-dark-mode",
      "title": "Add theme toggle component to Settings page",
      "acceptanceCriteria": [
        "Toggle switch in Settings page",
        "Toggle calls setTheme from context",
        "Current theme state displayed"
      ],
      "priority": 2,
      "passes": false,
      "notes": "Add to existing Settings component. Use existing toggle/switch component if available.",
      "dependencies": ["add-dark-mode-1"],
      "subtasks": []
    },
    {
      "id": "add-dark-mode-3",
      "branchName": "ralph/add-dark-mode",
      "title": "Persist theme preference to localStorage",
      "acceptanceCriteria": [
        "Theme saved to localStorage on change",
        "Theme restored from localStorage on app load",
        "Falls back to system preference if no saved value"
      ],
      "priority": 3,
      "passes": false,
      "notes": "Add persistence logic to ThemeContext initialization.",
      "dependencies": ["add-dark-mode-1"],
      "subtasks": []
    },
    {
      "id": "add-dark-mode-4",
      "branchName": "ralph/add-dark-mode",
      "title": "Update global styles to use CSS variables for theming",
      "acceptanceCriteria": [
        "CSS variables defined for colors, backgrounds",
        "Dark theme variables override light defaults",
        "All components use variables instead of hardcoded colors"
      ],
      "priority": 4,
      "passes": false,
      "notes": "Update global stylesheet. May need to audit components for hardcoded colors.",
      "dependencies": ["add-dark-mode-1"],
      "subtasks": []
    },
    {
      "id": "add-dark-mode-5",
      "branchName": "ralph/add-dark-mode",
      "title": "Run typecheck and fix any type errors",
      "acceptanceCriteria": [
        "npm run type-check passes with no errors",
        "All new code properly typed"
      ],
      "priority": 5,
      "passes": false,
      "notes": "Final validation task. Fix any type errors introduced by previous tasks.",
      "dependencies": ["add-dark-mode-4"],
      "subtasks": []
    }
  ]
}
```

**Output:**
```
Generated 5 tasks for add-dark-mode in .ralphspec/changes/add-dark-mode/prd.json

Tasks:
1. Create ThemeContext provider with light/dark mode support
2. Add theme toggle component to Settings page
3. Persist theme preference to localStorage
4. Update global styles to use CSS variables for theming
5. Run typecheck and fix any type errors

Next steps:
1. Ensure you're on branch: git checkout ralph/add-dark-mode
2. Run first task: ./.ralphspec/scripts/run-task.sh
   Or run all: ./.ralphspec/scripts/run-all-tasks.sh
```

## Guidelines

- **Preserve exact task titles** from tasks.md - don't paraphrase
- **Infer specific acceptance criteria** - don't be vague
- **Add implementation notes** from design.md context
- **Set sensible dependencies** - most tasks depend on setup tasks
- **Final task** should typically be typecheck/validation
