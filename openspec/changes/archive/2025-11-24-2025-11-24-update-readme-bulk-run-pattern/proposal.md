# Update README to Emphasize Bulk Run Pattern

## Problem
The README.md currently shows both individual `guardrail.check()` calls and bulk `guardrail.Run()` calls, but doesn't clearly indicate which is the preferred approach. Since example.py has been updated to use the unified bulk Run method as the primary pattern, the README should be consistent.

## Solution
Update the README.md usage examples to:
- Show bulk `guardrail.Run([gr1, gr2, gr3], text)` as the primary recommended pattern
- Keep individual `check()` examples but mark them as secondary/legacy
- Reorder examples to emphasize the bulk approach first
- Update any introductory text to reflect the preferred bulk execution pattern

## Impact
- **Users**: Will see consistent messaging across documentation and examples about the preferred bulk execution pattern
- **Documentation**: README will align with the updated example.py and demonstrate best practices
- **API Clarity**: Makes it clear which pattern is recommended for production use

## Implementation Notes
- Keep all existing examples functional
- Don't remove individual check examples (for backward compatibility)
- Focus on reordering and adding clear preference indicators
- Ensure the migration section still shows the transition from GuardrailManager</content>
<parameter name="filePath">openspec/changes/update-readme-bulk-run-pattern/proposal.md