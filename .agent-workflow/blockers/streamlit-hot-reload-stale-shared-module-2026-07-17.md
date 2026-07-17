# Streamlit hot reload retained a stale shared module

## Context and intended action

A reusable `render_metric_grid` helper was added to `app.app_utils` and imported by multiple page modules while the Streamlit development server was already running.

## Observable symptom

After a browser reload, a page raised `ImportError: cannot import name 'render_metric_grid' from 'app.app_utils'`, even though the function existed in the source file and AST validation passed.

## Impact

The revised pages could not render under the existing live server process.

## Confirmed cause

Streamlit re-executed the changed page module but retained the previously imported `app.app_utils` module object, which did not yet contain the newly added function.

## Workaround

Restart the verified local Streamlit server after adding or renaming symbols in shared imported modules, then reload the browser page.

## Prevention

Do not rely solely on hot reload for cross-module API changes. Restart the development server whenever a page begins importing a newly introduced shared helper.
