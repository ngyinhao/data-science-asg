# Model chart labels clipped at the commented viewport

## Context and intended action

The equal-height model-comparison chart cards were visually reviewed at the 762-by-742 viewport supplied with the browser comment.

## Observable symptom

The RMSE chart's long axis title was clipped, while the grouped error chart's full model names collided and were partly obscured because a right-side legend substantially reduced the plotting width.

## Impact

Although the card boundaries were aligned, OCR could not reliably capture complete chart labels and the row still appeared visually chaotic at the target width.

## Confirmed cause

Long redundant axis text, full estimator names, angled categorical labels, and a right-oriented legend were competing for a narrow two-column chart area.

## Workaround

- Shorten the RMSE axis title while retaining the lower-is-better explanation in the card caption.
- Use concise display labels for models while preserving full names in tooltips.
- Move the metric legend below the chart so the plot receives the full card width.
- Stack label-heavy chart cards vertically so each chart receives the full content width at compact viewports.
- Limit residual and hourly-error axis tick density so OCR receives a small, stable set of labels.

## Prevention

Visually test label-heavy charts at the narrowest supported viewport. Equal card dimensions alone are insufficient; verify axis titles, category labels, and legends remain complete and non-overlapping.
