# Staged diff check rejected a trailing blank line

## Context and intended action

Before committing all approved changes, the workflow ran `git diff --cached --check` to validate the staged patch.

## Observable symptom

The check returned a nonzero exit code and identified a newly added workflow incident note with a blank line at end-of-file.

## Impact

The commit was paused until the formatting issue could be corrected and the staged patch revalidated.

## Confirmed cause

The untracked Markdown note ended with an additional empty line after its final paragraph.

## Troubleshooting and result

The final lines of the note were inspected, and the redundant blank line was removed while preserving the required terminal newline.

## Workaround and prevention

Run `git diff --cached --check` before committing. When it reports a new blank line at EOF, remove only the redundant empty line, restage the file, and rerun the check.
