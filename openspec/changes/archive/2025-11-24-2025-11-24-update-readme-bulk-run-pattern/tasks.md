# Update README Bulk Run Pattern Tasks

## Tasks

### 1. Reorder Usage Examples
**Status:** pending
**Description:** Reorder the README usage examples to show bulk Run patterns first, then individual check patterns.

**Implementation:**
- Move the "Run() Function (Multiple Guardrails)" section to appear before individual check examples
- Ensure the bulk Run example is prominently featured
- Keep all existing examples functional

**Validation:**
- README flows logically from bulk usage to individual usage
- All code examples remain syntactically correct

### 2. Add Preference Indicators
**Status:** pending
**Description:** Add clear indicators in the README that bulk Run is the recommended primary pattern.

**Implementation:**
- Add comments or section headers indicating "Recommended" for bulk patterns
- Add "Legacy" or "Alternative" indicators for individual check patterns
- Update any introductory text to mention bulk execution as preferred

**Validation:**
- Users can clearly identify which patterns are recommended
- No confusion about which approach to use

### 3. Update Introductory Text
**Status:** pending
**Description:** Update section introductions and descriptions to emphasize bulk execution benefits.

**Implementation:**
- Modify the "Run() Function" section description to highlight benefits
- Add text explaining why bulk execution is preferred
- Ensure the migration section still makes sense

**Validation:**
- README accurately reflects the current API preferences
- Benefits of bulk execution are clearly communicated

### 4. Validate README Examples
**Status:** pending
**Description:** Ensure all README code examples still work after reordering and updates.

**Implementation:**
- Check that all code blocks are syntactically correct
- Verify import statements are consistent
- Test that examples follow the same patterns as example.py

**Validation:**
- All code examples execute without syntax errors
- Examples are consistent with the updated example.py patterns</content>
<parameter name="filePath">openspec/changes/update-readme-bulk-run-pattern/tasks.md