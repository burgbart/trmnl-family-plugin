---
id: doc-3
title: Precipitation-weighted rain icon selection
type: guide
created_date: '2026-07-23 13:02'
updated_date: '2026-07-23 13:04'
---
# Precipitation-weighted rain icon selection

## Context

The dashboard already thresholds borderline drizzle/shower codes (51/53/80) in `src/weather.py` so that a brief, low-probability drizzle does not render as a full-day rain icon (TASK-5). The current rule downgrades a borderline code to a plain cloud icon only when **both** `precipitation_probability_max < 30%` **and** `precipitation_sum < 1.0 mm`.

A user observed a specific day (Sunday in the forecast) that the dashboard rendered as rainy while Google Weather showed only a single light-drop indicator. This suggests consumer forecasts weight the precipitation amount by the probability of precipitation before choosing an icon. This investigation tests scoring functions that combine amount and probability, compares them against the current TASK-5 logic, and records a recommendation.

## Representative Open-Meteo data

Fetched for Amsterdam (`52.3676, 4.9041`) on 2026-07-23 with all available daily and hourly precipitation fields:

| Date | WMO code | Description | Precip sum (mm) | Max PoP (%) | Precip hours | Cloud cover mean (%) | Current icon |
|------|----------|-------------|-----------------|-------------|--------------|----------------------|--------------|
| 2026-07-23 | 51 | Light drizzle | 0.1 | 4 | 1.0 | 91 | cloud |
| 2026-07-24 | 3 | Overcast | 0.0 | 10 | 0.0 | 83 | cloud |
| 2026-07-25 | 3 | Overcast | 0.0 | 12 | 0.0 | 54 | partly-cloudy* |
| 2026-07-26 (Sun) | 80 | Slight rain showers | 6.4 | 70 | 10.0 | 83 | rain |
| 2026-07-27 | 51 | Light drizzle | 1.7 | 49 | 7.0 | 18 | rain-light |
| 2026-07-28 | 3 | Overcast | 0.0 | 4 | 0.0 | 21 | partly-cloudy* |
| 2026-07-29 | 0 | Clear sky | 0.0 | 4 | 0.0 | 1 | sun |

\* After the partly-cloudy refinement from TASK-8.

Sunday 2026-07-26 is genuinely wet (6.4 mm, 70% probability, 10 wet hours), so all approaches agree it deserves a rain icon. The more interesting cases are the borderline drizzle days such as 2026-07-27 (1.7 mm, 49% probability) and 2026-07-23 (0.1 mm, 4% probability).

Raw data and analysis tables are saved alongside this document in:
- `backlog/docs/weather/open-meteo-precipitation-investigation.json`
- `backlog/docs/weather/synthetic-precipitation-scenarios.json`

## Proposed scoring formulas

Three candidate approaches were evaluated:

### 1. Expected amount (recommended)

```
score = precipitation_sum * (precipitation_probability_max / 100)
```

This is the statistical expectation of liquid precipitation. It treats a high-amount, low-probability day and a low-amount, high-probability day similarly when the expected values are equal.

### 2. Wet-hours score

```
score = precipitation_hours * (precipitation_probability_max / 100)
```

This rewards long-duration, high-probability wet spells and penalizes brief drizzle windows.

### 3. Keep current TASK-5 hard thresholds

Downgrade borderline codes (51/53/80) to cloud only when both `prob < 30%` and `amount < 1.0 mm`; otherwise use amount-based intensity thresholds.

## Comparison against current logic

### Real forecast days

| Date | Code | Sum | Prob | Hours | Current | Expected amount score | Wet-hours score |
|------|------|-----|------|-------|---------|----------------------|-----------------|
| 2026-07-23 | 51 | 0.1 | 4 | 1.0 | cloud | 0.004 | 0.04 |
| 2026-07-26 | 80 | 6.4 | 70 | 10.0 | rain | 4.48 | 7.00 |
| 2026-07-27 | 51 | 1.7 | 49 | 7.0 | rain-light | 0.833 | 3.43 |

### Synthetic scenarios

| Code | Sum (mm) | Prob (%) | Description | Current | Expected-amount icon | Wet-hours icon |
|------|----------|----------|-------------|---------|----------------------|----------------|
| 51 | 0.1 | 4 | brief drizzle, very low prob | cloud | cloud* | cloud* |
| 51 | 0.5 | 20 | light drizzle, low prob | cloud | cloud* | cloud* |
| 51 | 1.0 | 30 | drizzle, borderline | rain-light | rain-light | rain-light |
| 51 | 2.0 | 40 | moderate drizzle, medium prob | rain-light | rain-light | rain-light |
| 80 | 1.5 | 20 | short shower, low prob | rain-light | rain-light | rain-light |
| 80 | 2.0 | 60 | showers, decent prob | rain-light | rain | rain-light |
| 80 | 6.0 | 70 | substantial showers, high prob | rain | rain-heavy | rain |
| 61 | 5.0 | 30 | real rain, lower prob | rain | rain | rain |
| 61 | 5.0 | 70 | real rain, high prob | rain | rain | rain |
| 65 | 12.0 | 90 | heavy rain, high prob | rain-heavy | rain-heavy | rain-heavy |

\* Using borderline-only application of expected amount (see Recommendation).

## Recommendation

Adopt a **probability-weighted expected amount score** for the existing borderline drizzle/shower codes (51/53/80), while keeping the current amount-based thresholds for non-borderline rain codes (61/63/65/66/67/81/82).

### Why borderline codes only

Codes 61-67 and 81-82 already represent unambiguous rain ("Slight/Moderate/Heavy rain"). Downgrading those based on probability would hide real rain. Codes 51/53/80 are the ones most affected by Open-Meteo's "most severe hour of the day" aggregation, so they benefit most from probability weighting.

### Proposed rule

For borderline codes (51/53/80) in daily forecasts:

```python
expected_amount = precipitation_sum * (precipitation_probability_max / 100)

if expected_amount < 0.2:
    return "cloud"
if expected_amount < 1.5:
    return "rain-light"
# otherwise fall through to amount-based intensity
```

Then apply the existing amount-based thresholds:
- `precipitation_sum >= 10.0 mm` → `rain-heavy`
- `precipitation_sum < 2.5 mm` → `rain-light`
- otherwise → `rain`

### Tunable parameters

The thresholds (0.2 mm and 1.5 mm expected amount) are starting values. They can be exposed as environment variables if operational experience shows they need per-location tuning.

### Comparison with current logic

- **Current logic** is binary: borderline codes are either cloud (when both amount and probability are very low) or rain intensity is decided purely by amount.
- **Proposed logic** smooths the transition: low-confidence drizzle becomes `cloud` or `rain-light`, while higher-confidence or higher-amount rain still reaches `rain`/`rain-heavy`.
- For the real Amsterdam forecast above, the proposed rule keeps 2026-07-23 as `cloud` and 2026-07-27 as `rain-light`, matching the current output, but would behave more intuitively for intermediate cases such as 2.0 mm at 40% probability.

## Follow-up work

Create an implementation task to update `src/weather.py` with the probability-weighted expected-amount scoring for borderline rain codes, add tests covering the new thresholds, and consider exposing the thresholds through environment variables for tuning.
