# Clips OS — Project Instructions

## Overview
Clips OS is a Claude AI plugin that serves as a Growth Engine for DTC ecommerce founders and marketers. It provides on-demand audits and analysis through a skill-based architecture triggered by slash commands.

**Current version:** 0.1.0
**License:** MIT
**Author:** Giovanni Brando Dalla Rizza

## Architecture

This is NOT a traditional web app. It's a **Claude plugin** with a skill-based command system:

- `/commands/*.md` — Command routers (thin files that trigger skills)
- `/skills/*/SKILL.md` — Skill implementations (workflows, criteria, scripts)
- `/references/` — Shared frameworks (scoring, methodology)
- `/scripts/` — Shared Python utilities (report generation helpers)
- `/.claude-plugin/` — Plugin manifest and marketplace config

### Skill Structure
Every skill follows this layout:
```
skill-name/
├── SKILL.md          # YAML frontmatter + markdown workflow instructions
├── references/       # Evaluation criteria, rubrics, docs
├── scripts/          # Python/Bash for deterministic operations (reports)
├── evals/            # Test cases and expected outputs
└── assets/           # Templates, images (if needed)
```

## Active Features

| Command | Skill | Status |
|---------|-------|--------|
| `/cro` | `cro-audit` | Implemented |
| `/landing` | `landing-optimizer` | Planned |
| `/email` | `email-analyzer` | Planned |
| `/ads` | `ad-reviewer` | Planned |
| `/funnel` | `funnel-analyzer` | Planned |
| `/journey` | `journey-mapper` | Planned |
| `/retention` | `retention-analyzer` | Planned |
| `/abtest` | `abtest-planner` | Planned |
| `/intel` | `competitor-intel` | Planned |
| `/unit-econ` | `unit-economics` | Planned |

## MCP Servers

Three MCP servers are configured in `.mcp.json`:

1. **Playwright** — Browser automation (screenshots, navigation, page interaction)
2. **Exa** — Web search, company research, competitive intelligence, deep research
3. **Ref** — Official documentation fetching

### MCP Usage Priority
- **Always use Exa MCP first** for any external information needs: competitor research, industry benchmarks, best practices, market data, current trends, technology lookups, and any real-world context gathering. Exa tools include: `web_search_exa`, `crawling_exa`, `company_research_exa`, `linkedin_search_exa`, `deep_researcher_start`, `deep_researcher_check`, `get_code_context_exa`.
- **Use Ref MCP** specifically for fetching official library/framework/API documentation when implementing code.
- **Use Playwright MCP** for browser automation: taking screenshots, navigating sites, interacting with page elements during audits.

## Scoring & Priority Framework

Shared across all skills (see `references/scoring-framework.md`):

**Scores (1-5):**
- 5 = Excellent (no changes needed)
- 4 = Good (minor improvements)
- 3 = Acceptable (clear optimization room)
- 2 = Needs Work (significant issues)
- 1 = Critical (major blockers)

**Priorities (P0-P3):**
- P0 = This week (critical revenue loss)
- P1 = 2 weeks (meaningfully hurting metrics)
- P2 = Next sprint (optimization opportunity)
- P3 = Backlog (polish/nice-to-have)

## Key Files

| File | Purpose |
|------|---------|
| `skills/cro-audit/SKILL.md` | Flagship CRO audit workflow |
| `skills/cro-audit/references/cro-criteria.md` | 30+ evaluation criteria by page type |
| `skills/cro-audit/scripts/generate_report.py` | HTML report generator |
| `scripts/report_utils.py` | Shared utilities (scoring colors, labels, encoding) |
| `references/scoring-framework.md` | Universal scoring & priority system |
| `.mcp.json` | MCP server configuration |
| `.claude-plugin/plugin.json` | Plugin metadata |

## Development Conventions

### Naming
- Skills: kebab-case directories (`cro-audit`, `landing-optimizer`)
- Commands: lowercase `.md` matching skill name (`cro.md`)
- Python: snake_case functions and variables
- References: kebab-case descriptive names (`cro-criteria.md`)

### Principles
- **Specificity over generics** — Recommendations must reference exact elements (colors, sizes, positions), never vague advice
- **Revenue impact first** — Prioritize findings by business impact, not technical severity
- **DTC-focused** — All analysis targets DTC ecommerce patterns (brand storytelling, subscriptions, post-purchase UX, mobile-first)
- **Progressive disclosure** — Keep SKILL.md lean (<300 lines); push detailed criteria to `references/`
- **Self-contained skills** — Each skill is an independent module with its own references and scripts
- **Markdown-first** — Commands, skills, and documentation are all Markdown; code only for deterministic operations (report generation)

### Report Generation
- Reports use structured JSON data → Python HTML generator
- Screenshots encoded as base64 data URIs for portability
- Color-coded scores: green (#16a34a) → red (#dc2626)
- Output formats: HTML (default), PDF, DOCX (via docx skill), Notion

### When Building New Skills
1. Follow the skill structure template above
2. Create a command router in `/commands/`
3. Reuse `references/scoring-framework.md` for scoring consistency
4. Reuse `scripts/report_utils.py` for report helper functions
5. Add evaluation cases in `evals/evals.json`
6. Use Exa MCP to research current industry best practices and benchmarks before defining evaluation criteria

### External Research Workflow
When building or updating any skill that needs external knowledge:
1. **Use Exa `web_search_exa`** to find current best practices, benchmarks, and industry standards
2. **Use Exa `company_research_exa`** to analyze competitors and market leaders
3. **Use Exa `deep_researcher_start/check`** for in-depth research on complex topics
4. **Use Exa `crawling_exa`** to extract detailed content from specific URLs
5. **Use Ref MCP** only when you need official library/API documentation for code implementation

## CRO Audit Methodology

The flagship skill uses a hybrid framework:
- **LIFT Model** — 5 lenses: Clarity, Relevance, Friction, Anxiety, Urgency (+ Technical)
- **Baymard Research Heuristics** — E-commerce UX best practices
- **DTC-Specific Criteria** — Brand storytelling, subscription flows, post-purchase upsells, loyalty programs, social proof (UGC/influencer), mobile-first (70%+ DTC traffic)

### Page Types Analyzed
Homepage, Collection/Category, Product Detail Page (PDP), Cart, Checkout, Search

### Audit Workflow
1. Clarify scope with user (URL, format, specific concerns)
2. Discovery: navigate homepage, auto-crawl core page types
3. Screenshot: desktop (1440px) + mobile (390px) for each page
4. Evaluate: score each page against type-specific criteria
5. Synthesize: cross-cutting issues, prioritized action plan
6. Generate: HTML report with embedded screenshots and findings
