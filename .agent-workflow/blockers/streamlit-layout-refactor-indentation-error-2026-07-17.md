# Layout refactor introduced an indentation error

## Context and intended action

Paired model-summary cards were restructured into explicit two-card rows so each pair could use matching stretch height.

## Observable symptom

Python validation reported an `IndentationError` immediately after the new `with st.container(...)` statement in `model_comparison.py`.

## Impact

The model-comparison page could not execute until the card contents were nested inside the new container block.

## Confirmed cause

The loop body retained its previous indentation level when the additional container context manager was inserted.

## Troubleshooting and result

Inspected the numbered source lines, identified the unindented block, and moved all model-card contents one indentation level deeper.

## Prevention

After restructuring nested Streamlit layout context managers, run syntax validation before visual testing and inspect the exact numbered lines for any reported indentation failure.

## Recurrence: shared metric-grid columns

While changing `render_metric_grid` from a horizontal container to explicit full-width rows, the `st.metric(...)` call was initially left level with its new `with column:` statement. Source inspection caught it before application execution. Indent the metric call inside the column context and retain AST validation before restarting Streamlit.
