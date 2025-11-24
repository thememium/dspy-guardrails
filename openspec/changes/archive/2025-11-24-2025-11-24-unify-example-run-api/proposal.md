# Unify Example.py to Use Bulk Run Method

## Problem
The current `example.py` demonstrates guardrail usage with two different patterns:
1. Individual guardrail checks using `gr.check(test_text)` (lines 64-78)
2. Bulk execution using `guardrail.Run()` (lines 87-127)

This creates inconsistency and doesn't showcase the unified bulk Run API as the primary pattern. Users may be confused about which method to use for checking multiple guardrails.

## Solution
Update `example.py` to use the unified bulk `Run()` method for all guardrail testing, replacing the individual `gr.check()` calls. This will:
- Demonstrate the preferred bulk execution pattern
- Show how to check all guardrails in a single operation
- Maintain the same functionality while using consistent API patterns
- Align with the simplified Run API specification

## Impact
- **Users**: Will see a cleaner, more consistent example that demonstrates the recommended bulk execution pattern
- **Code**: No breaking changes, just reorganization of the example
- **Documentation**: Example will better reflect the intended API usage patterns

## Alternatives Considered
1. **Keep both patterns**: Would maintain confusion about which method to prefer
2. **Remove Run examples**: Would lose demonstration of the bulk API
3. **Add more individual examples**: Would make the example even more inconsistent

## Implementation Notes
- Replace the individual check loop (lines 64-78) with a single `guardrail.Run(all_guardrails, test_text)` call
- Update the output formatting to handle the list of results
- Ensure all existing functionality is preserved
- Keep the separate Run() examples section for detailed API demonstration</content>
<parameter name="filePath">openspec/changes/unify-example-run-api/proposal.md