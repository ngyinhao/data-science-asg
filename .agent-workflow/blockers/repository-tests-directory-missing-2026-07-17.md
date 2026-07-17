# Repository has no tests directory

## Context and intended action

After validating the Streamlit source and theme configuration, the workflow looked for repository tests under the conventional `tests/` directory.

## Observable symptom

`rg --files tests` failed because the directory does not exist.

## Impact

There is no conventional test suite available at that path for validating the cross-page layout changes. Validation must rely on any test files found elsewhere, no-bytecode syntax checks, Streamlit startup checks, and browser QA.

## Confirmed cause

The repository does not contain a top-level `tests/` directory.

## Troubleshooting and workaround

Search the repository for test-like Python filenames outside `tests/`. If none exist, perform AST parsing for source validity and visually inspect every Streamlit page at the target viewport.

## Prevention

Add focused application tests when practical, especially smoke tests that import chart builders and verify that every Streamlit page starts without an exception.
