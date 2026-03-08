Recursively improve existing LoveSpark tools and skills by reviewing them against accumulated knowledge in the memory system. This is how our tools get smarter over time.

## Step 1: Read Current Knowledge

Read these files to understand what we've learned:

- `~/.claude/docs/memory/known-issues.md` — issues tools should catch
- `~/.claude/docs/memory/tool-changelog.md` — current tool capabilities and gaps
- `~/.claude/docs/memory/color-decisions.md` — token values and constraints
- `~/.claude/docs/memory/debugging.md` — solutions that could be automated
- `~/.claude/docs/memory/patterns.md` — patterns that tools could enforce

## Step 2: Gap Analysis

For each tool/skill listed in tool-changelog.md:

1. Compare its "Known gaps" against known-issues.md entries — if a tool SHOULD catch an issue but doesn't, that's a priority improvement
2. Check if any "Improvement backlog" items can now be implemented based on accumulated knowledge
3. Check if the tool's hardcoded data (e.g., color values in audit-contrast.py) matches the current canonical values in color-decisions.md
4. Identify any NEW gaps based on recent known-issues that weren't there when the tool was last updated

Present the analysis as a priority-ranked table:

| Tool | Gap | Impact | Effort |
|------|-----|--------|--------|

## Step 3: Apply Improvements

For each high-impact, low-effort improvement:

1. Read the current tool/skill file
2. Make the targeted improvement
3. Test if applicable (run audit-contrast.py to verify changes work)
4. Update tool-changelog.md with the change

For high-effort improvements, add them to the backlog with clear specifications.

## Step 4: Cross-Reference

After improvements:

- Run `audit-contrast.py --verbose` to verify contrast tool still works
- Check that slash commands reference the latest memory file paths
- Verify CLAUDE.md context module table is up to date
- Verify known-issues.md prevention rules match what tools now check

## Step 5: Update Changelog

Update `~/.claude/docs/memory/tool-changelog.md`:

- Increment version numbers for modified tools
- Move completed backlog items to changes list
- Add any newly discovered gaps
- Add any new improvement ideas that came up during the review

## When to Run This

- After adding 3+ new entries to known-issues.md
- After a build where tools missed issues they should have caught
- Periodically (monthly) as a maintenance task
- When Joona requests a tools review
