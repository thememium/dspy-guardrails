# /ralphspec:create-feature

Create a new feature definition for RalphSpec automated implementation.

## Usage

```
/ralphspec:create-feature <feature-description>
```

## Instructions

When this command is invoked:

1. **Parse the feature description** from the argument provided

2. **Use the appropriate question tool** to gather clarity before creating the feature. Never skip this step, even if the description seems clear. 

   - **For Claude Code**: Use the `AskUserQuestion` tool.
   - **For OpenCode**: Use the `question` tool.

   Both tools allow you to ask 1-4 questions at once with selectable options.

   **Tool usage guidelines:**
   - Each question needs a `header` (max 12 chars), `question` text, and 2-4 `options`
   - Users can always select "Other" to provide custom input
   - Use `multiSelect: true` (if supported by the tool) when multiple options can apply
   - Add "(Recommended)" to the end of suggested option labels

   **Question categories to consider (pick 3-4 relevant ones):**

   **Scope & Functionality:**
   - What specific problem does this feature solve?
   - What should users be able to do when this feature is complete?
   - Are there any edge cases or error scenarios to handle?

   **Technical Context:**
   - What parts of the codebase will this likely touch?
   - Are there existing patterns or similar features to follow?
   - Any specific libraries, APIs, or technologies to use or avoid?

   **Acceptance Criteria:**
   - How will we know this feature is "done"?
   - Are there specific behaviors that must work?
   - Any performance or security requirements?

   **Constraints & Dependencies:**
   - Does this depend on other features or systems?
   - Are there any constraints (backwards compatibility, browser support, etc.)?
   - Who is the target user for this feature?

   Tailor questions to the specific feature - don't ask generic questions that don't apply. Provide sensible default options based on the feature description.

3. **Wait for user responses** before proceeding. Use the answers to craft detailed acceptance criteria and notes.

4. **Generate a feature ID** by converting the description to kebab-case (lowercase, hyphens for spaces, max 30 chars)

5. **Create or update `.ralphspec/features.json`**:
   - If file doesn't exist, create it with the features array
   - If file exists, append the new feature to the array
   - Ensure no duplicate feature IDs

6. **Feature schema** (all fields required):
```json
{
  "id": "feature-id-kebab-case",
  "branchName": "ralph/feature-id-kebab-case",
  "title": "Human readable feature title",
  "description": "Detailed description of what this feature does",
  "acceptanceCriteria": [
    "Specific measurable criterion 1",
    "Specific measurable criterion 2",
    "typecheck passes"
  ],
  "priority": 1,
  "proposalCreated": false,
  "completed": false
}
```

7. **Output** the created feature and next steps:
   - Show the generated feature JSON
   - Instruct user to run `/openspec:proposal <feature-id>` next
   - Remind them to create a branch: `git checkout -b ralph/<feature-id>`

## Example

**User Input:**
```
/ralphspec:create-feature Add user authentication with OAuth
```

**Assistant uses AskUserQuestion tool:**
```json
{
  "questions": [
    {
      "header": "Providers",
      "question": "Which OAuth providers should be supported?",
      "multiSelect": true,
      "options": [
        { "label": "Google (Recommended)", "description": "Most common, easy setup with Google Cloud Console" },
        { "label": "GitHub", "description": "Good for developer-focused apps" },
        { "label": "Microsoft", "description": "Enterprise/Azure AD integration" },
        { "label": "Apple", "description": "Required for iOS apps with social login" }
      ]
    },
    {
      "header": "Post-Auth",
      "question": "What should happen after successful authentication?",
      "multiSelect": false,
      "options": [
        { "label": "Redirect to dashboard (Recommended)", "description": "Send user to main app area after login" },
        { "label": "Redirect to previous page", "description": "Return user to where they were before login" },
        { "label": "Stay on login page", "description": "Show success message, user navigates manually" }
      ]
    },
    {
      "header": "Sessions",
      "question": "How should sessions be managed?",
      "multiSelect": false,
      "options": [
        { "label": "JWT in httpOnly cookie (Recommended)", "description": "Secure, automatic with requests, 7-day default" },
        { "label": "JWT in localStorage", "description": "Client-controlled, requires manual header attachment" },
        { "label": "Server-side sessions", "description": "Traditional sessions with session ID cookie" }
      ]
    },
    {
      "header": "Login UI",
      "question": "What should the login UI look like?",
      "multiSelect": false,
      "options": [
        { "label": "Dedicated /login page (Recommended)", "description": "Standalone page with provider buttons" },
        { "label": "Modal overlay", "description": "Login form appears in modal over current page" },
        { "label": "Inline component", "description": "Embeddable login form for any page" }
      ]
    }
  ]
}
```

**User selects options via the form UI, then assistant receives answers and creates feature:**

**Assistant creates feature:**
```json
{
  "id": "add-user-auth-oauth",
  "branchName": "ralph/add-user-auth-oauth",
  "title": "Add user authentication with OAuth",
  "description": "Implement user authentication using Google and GitHub OAuth providers with JWT session management",
  "acceptanceCriteria": [
    "Users can sign in with Google OAuth",
    "Users can sign in with GitHub OAuth",
    "New users are created in database on first sign-in",
    "Successful auth redirects to dashboard",
    "JWT stored in httpOnly cookie with 7-day expiry",
    "Dedicated /login page with provider buttons",
    "Already authenticated users redirect away from /login",
    "Logout clears session and redirects to /login",
    "typecheck passes"
  ],
  "priority": 1,
  "proposalCreated": false,
  "completed": false
}
```

**Next steps displayed:**
```
Feature created in .ralphspec/features.json

Next steps:
1. Create a branch: git checkout -b ralph/add-user-auth-oauth
2. Create the proposal: /openspec:proposal add-user-auth-oauth
3. Generate prd.json: /ralphspec:generate-prd add-user-auth-oauth
4. Run tasks: ./.ralphspec/scripts/run-task.sh
```

## Guidelines

- **ALWAYS ask follow-up questions** - Never create a feature without first asking clarifying questions, even if the request seems straightforward. Better questions lead to better acceptance criteria.
- **Tailor questions to the feature** - Don't ask about OAuth for a "remove button" feature. Ask relevant questions.
- **Use user's answers** to craft specific acceptance criteria - The whole point of asking questions is to create detailed, actionable criteria.
- **Always include "typecheck passes"** as the final acceptance criterion
- **Keep IDs short** but descriptive (max 30 characters)
- **Be specific** in acceptance criteria - vague criteria lead to unclear tasks
- **Priority** should be 1 unless user specifies otherwise
- **Branch naming** always uses `ralph/` prefix
