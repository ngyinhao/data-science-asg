# Streamlit fixed chart columns stayed narrow at 762 pixels

## Context and intended action

Paired chart cards used `st.columns(2)` with stretch-matched inner containers and were reviewed for OCR legibility at the 762-by-742 browser-comment viewport.

## Observable symptom

The cards had equal outer dimensions, but Streamlit kept them side by side at roughly 286 to 322 pixels each instead of stacking. Charts with dense axes or controls remained cramped, and matched borders concealed substantial differences in internal chart start positions and unused space.

## Impact

Strict border alignment alone did not create a predictable OCR-friendly reading experience. Several chart labels overlapped or clipped, and paired content began at visibly different vertical offsets.

## Confirmed cause

Native fixed `st.columns` layouts do not provide an application-level breakpoint setting that stacks these specific rows at the target viewport.

## Workaround

Use full-width, vertically stacked chart cards for OCR-heavy analytical views. This guarantees one reading column, complete axis-label space, consistent left and right edges, and a predictable top-to-bottom sequence at both compact and desktop widths.

## Prevention

Do not assume equal-height columns are responsive enough for accessibility. Test actual chart plotting width and label geometry at the narrow target viewport; use one-column chart flow when labels or controls need more space.
