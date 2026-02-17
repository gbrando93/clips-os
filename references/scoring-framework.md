# Clips OS Scoring Framework

Shared scoring methodology used across all Clips OS skills to ensure consistent, comparable output.

## Score Rubric (1-5)

| Score | Label | Meaning |
|-------|-------|---------|
| 5 | Excellent | Best-in-class implementation, no changes needed |
| 4 | Good | Solid implementation with minor improvement opportunities |
| 3 | Acceptable | Functional but clear room for optimization |
| 2 | Needs Work | Significant issues likely hurting performance |
| 1 | Critical | Major blockers present — address immediately |

**Page/section scores** are the average of individual criterion scores for that section.
**Overall score** is the average across all pages/sections analyzed.

## Priority Framework (P0-P3)

| Priority | Label | Definition | Action Timeline |
|----------|-------|-----------|----------------|
| P0 | Critical | Likely causing significant revenue loss right now | Fix this week |
| P1 | High | Meaningfully reducing performance metrics | Fix within 2 weeks |
| P2 | Medium | Clear optimization opportunity | Plan for next sprint |
| P3 | Low | Nice-to-have polish items | Backlog |

## Impact-Effort Matrix

Use this to categorize action items:

| | Low Effort | High Effort |
|---|---|---|
| **High Impact** | Quick Win — do first | Strategic — plan and execute |
| **Low Impact** | Fill-in — do if time allows | Deprioritize — skip for now |

## Conversion Impact Estimation

When estimating the revenue impact of a finding, use these qualitative levels:

- **High** — Directly affects purchase/signup completion (checkout friction, CTA visibility, pricing clarity)
- **Medium** — Affects engagement and progression through the funnel (navigation, product discovery, content quality)
- **Low** — Affects perception and long-term metrics (brand consistency, minor UX polish, edge cases)

## Color Coding (for report generators)

```
Score >= 4.5  →  #16a34a (green)    Excellent
Score >= 3.5  →  #65a30d (lime)     Good
Score >= 2.5  →  #ca8a04 (amber)    Acceptable
Score >= 1.5  →  #ea580c (orange)   Needs Work
Score <  1.5  →  #dc2626 (red)      Critical

P0  →  #dc2626 (red)
P1  →  #ea580c (orange)
P2  →  #ca8a04 (amber)
P3  →  #65a30d (lime)
```
