---
description: Run a CRO audit on a DTC ecommerce site
argument-hint: <url> [focus area]
---

The user wants a CRO audit. Activate the cro-audit skill.

If the user provided a URL and/or focus area: $ARGUMENTS

Follow the cro-audit skill workflow:
1. Clarify scope — confirm URL, output format preference, any specific concerns
2. Discovery — visit homepage, auto-discover page types (Collection, PDP, Cart, Checkout, Search)
3. Page-by-page analysis — screenshot each page, evaluate against CRO criteria, score 1-5
4. Compile report — generate HTML report with findings, scores, and prioritized action plan

If the user just drops a URL without context, proceed with the full audit and default to HTML output.
