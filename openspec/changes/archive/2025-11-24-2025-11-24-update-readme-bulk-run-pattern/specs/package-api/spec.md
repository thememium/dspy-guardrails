# Package API Specification Delta

## MODIFIED Requirements

### Requirement: Documentation Consistency
The system SHALL maintain consistent API usage patterns between example.py and README.md documentation.

#### Scenario: Unified Bulk Pattern Documentation
Given the example.py demonstrates bulk Run as the primary pattern
When users read the README.md
Then bulk guardrail.Run([gr1, gr2, gr3], text) SHALL be shown as the recommended primary pattern
And individual guardrail.check() examples SHALL be labeled as secondary or legacy
And documentation SHALL reflect the same usage hierarchy as example.py

#### Scenario: Example Ordering and Clarity
Given the README contains multiple usage examples
When examples are presented to users
Then bulk execution examples SHALL appear first
And clear preference indicators SHALL distinguish recommended from legacy patterns
And all examples SHALL remain functional and accurate

#### Scenario: API Pattern Communication
Given users need to understand which patterns to use
When they consult documentation
Then README SHALL clearly communicate bulk execution as the preferred approach
And benefits of bulk execution SHALL be explained
And migration guidance SHALL remain available for legacy users</content>
<parameter name="filePath">openspec/changes/update-readme-bulk-run-pattern/specs/package-api/spec.md