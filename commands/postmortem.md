After completing a build, review, or debug session, capture what was learned and update the persistent knowledge base so future sessions don't repeat mistakes.

## Step 1: Gather Context

Ask the user (or review the session) for:
- What was built or reviewed?
- What issues were found?
- What took multiple attempts to get right?
- Were any issues from known-issues.md encountered again?

## Step 2: Check Against Known Issues

Read `~/.claude/docs/memory/known-issues.md`. For each issue found in this session:
- If it matches an existing KI entry: Flag it as a **RECURRENCE**. This means the prevention rule isn't working. Update the prevention rule to be more specific or add it to CLAUDE.md as a hard rule.
- If it's a NEW issue: Create a new KI entry with all required fields (ID, Category, Severity, First found, Symptom, Root cause, Fix, Prevention rule).

## Step 3: Update Color Decisions

If any color token issues were found or token values were changed:
- Read `~/.claude/docs/memory/color-decisions.md`
- Update contrast ratios for affected pairings
- Add new dangerous pairings if discovered
- Update safe pairings if new ones were verified

## Step 4: Update Debugging Solutions

If any debugging insights were gained:
- Read `~/.claude/docs/memory/debugging.md`
- Add new Problem/Root cause/Fix/Prevention entries

## Step 5: Update Patterns

If any new reusable patterns were established:
- Read `~/.claude/docs/memory/patterns.md`
- Add new Pattern entries with Used in/When/Implementation/Notes

## Step 6: Flag Tool Improvements

If any tools or skills failed to catch issues they should have:
- Read `~/.claude/docs/memory/tool-changelog.md`
- Add to "Known gaps" for the relevant tool
- Add to "Improvement backlog" with specific description of what to add
- If the improvement is small and obvious, apply it now

## Step 7: Summary

Present a summary of all changes made to the knowledge base:
- New KI entries added
- Updated KI entries (recurrences)
- Color decisions updated
- Debugging solutions added
- Patterns added
- Tool improvements flagged

This is the feedback loop that makes the system learn. Every postmortem makes future builds better.
