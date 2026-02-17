#!/usr/bin/env python3
"""
Generate an interactive HTML CRO Audit Report from structured JSON data.

Usage:
    python generate_report.py --input audit_data.json --output report.html

Input JSON structure:
{
    "site_url": "https://example.com",
    "site_name": "Example Store",
    "platform": "Shopify",
    "audit_date": "2026-02-14",
    "overall_score": 3.2,
    "executive_summary": "...",
    "top_findings": [
        {"title": "...", "priority": "P0", "impact": "high", "description": "..."}
    ],
    "pages": [
        {
            "page_type": "Homepage",
            "url": "https://example.com",
            "page_score": 3.5,
            "desktop_screenshot_path": "/path/to/screenshot.png",
            "mobile_screenshot_path": "/path/to/mobile_screenshot.png",
            "findings": [
                {
                    "criterion_id": "H1",
                    "criterion_name": "Hero Section & Value Proposition",
                    "score": 3,
                    "issue": "Generic headline that doesn't communicate value proposition",
                    "recommendation": "Replace 'Welcome to Our Store' with benefit-driven headline",
                    "priority": "P1",
                    "lens": "clarity"
                }
            ]
        }
    ],
    "cross_cutting_issues": [
        {"title": "...", "description": "...", "affected_pages": ["Homepage", "PDP"], "priority": "P1"}
    ],
    "action_plan": {
        "quick_wins": [{"action": "...", "page": "...", "impact": "high", "effort": "low"}],
        "medium_term": [{"action": "...", "page": "...", "impact": "medium", "effort": "medium"}],
        "strategic": [{"action": "...", "page": "...", "impact": "high", "effort": "high"}]
    }
}
"""

import json
import base64
import sys
import os
from pathlib import Path
from datetime import datetime


def encode_image(image_path: str) -> str:
    """Encode an image file to base64 data URI."""
    if not image_path or not os.path.exists(image_path):
        return ""
    ext = Path(image_path).suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext.lstrip("."), "image/png")
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def score_color(score: float) -> str:
    """Return a CSS color based on score."""
    if score >= 4.5:
        return "#16a34a"  # green
    elif score >= 3.5:
        return "#65a30d"  # lime
    elif score >= 2.5:
        return "#ca8a04"  # amber
    elif score >= 1.5:
        return "#ea580c"  # orange
    else:
        return "#dc2626"  # red


def score_label(score: float) -> str:
    if score >= 4.5:
        return "Excellent"
    elif score >= 3.5:
        return "Good"
    elif score >= 2.5:
        return "Acceptable"
    elif score >= 1.5:
        return "Needs Work"
    else:
        return "Critical"


def priority_color(priority: str) -> str:
    return {
        "P0": "#dc2626",
        "P1": "#ea580c",
        "P2": "#ca8a04",
        "P3": "#65a30d"
    }.get(priority, "#6b7280")


def priority_label(priority: str) -> str:
    return {
        "P0": "Critical",
        "P1": "High",
        "P2": "Medium",
        "P3": "Low"
    }.get(priority, priority)


def lens_icon(lens: str) -> str:
    return {
        "clarity": "&#128269;",     # magnifying glass
        "relevance": "&#127919;",   # target
        "friction": "&#9888;&#65039;",  # warning
        "anxiety": "&#128274;",     # lock
        "urgency": "&#9201;",       # timer
        "technical": "&#9881;&#65039;"  # gear
    }.get(lens, "&#128300;")


def generate_html(data: dict) -> str:
    site_name = data.get("site_name", data.get("site_url", "Unknown"))
    site_url = data.get("site_url", "")
    platform = data.get("platform", "Unknown")
    audit_date = data.get("audit_date", datetime.now().strftime("%Y-%m-%d"))
    overall_score = data.get("overall_score", 0)
    executive_summary = data.get("executive_summary", "")
    top_findings = data.get("top_findings", [])
    pages = data.get("pages", [])
    cross_cutting = data.get("cross_cutting_issues", [])
    action_plan = data.get("action_plan", {})

    # Build top findings HTML
    top_findings_html = ""
    for f in top_findings[:5]:
        pc = priority_color(f.get("priority", "P2"))
        top_findings_html += f"""
        <div class="finding-card" style="border-left: 4px solid {pc};">
            <div class="finding-header">
                <span class="priority-badge" style="background:{pc};">{f.get('priority', 'P2')}</span>
                <strong>{f.get('title', '')}</strong>
            </div>
            <p>{f.get('description', '')}</p>
        </div>"""

    # Build pages HTML
    pages_html = ""
    page_nav_html = ""
    for i, page in enumerate(pages):
        page_type = page.get("page_type", f"Page {i+1}")
        page_id = page_type.lower().replace(" ", "-").replace("/", "-")
        page_score = page.get("page_score", 0)
        sc = score_color(page_score)
        sl = score_label(page_score)

        page_nav_html += f'<a href="#{page_id}" class="page-nav-link"><span class="page-score-mini" style="background:{sc};">{page_score:.1f}</span> {page_type}</a>'

        # Screenshots
        desktop_img = encode_image(page.get("desktop_screenshot_path", ""))
        mobile_img = encode_image(page.get("mobile_screenshot_path", ""))
        screenshots_html = '<div class="screenshots">'
        if desktop_img:
            screenshots_html += f'<div class="screenshot"><h4>Desktop</h4><img src="{desktop_img}" alt="{page_type} desktop"></div>'
        if mobile_img:
            screenshots_html += f'<div class="screenshot mobile"><h4>Mobile</h4><img src="{mobile_img}" alt="{page_type} mobile"></div>'
        screenshots_html += '</div>'

        # Findings table
        findings_html = ""
        for f in page.get("findings", []):
            fs = f.get("score", 0)
            fsc = score_color(fs)
            fpc = priority_color(f.get("priority", "P2"))
            li = lens_icon(f.get("lens", ""))
            findings_html += f"""
            <tr>
                <td>{li} {f.get('criterion_id', '')}</td>
                <td>{f.get('criterion_name', '')}</td>
                <td><span class="score-badge" style="background:{fsc};">{fs}</span></td>
                <td>{f.get('issue', '')}</td>
                <td>{f.get('recommendation', '')}</td>
                <td><span class="priority-badge-sm" style="background:{fpc};">{f.get('priority', 'P2')}</span></td>
            </tr>"""

        pages_html += f"""
        <section id="{page_id}" class="page-section">
            <div class="page-header">
                <h2>{page_type}</h2>
                <div class="page-score-large" style="background:{sc};">
                    <span class="score-number">{page_score:.1f}</span>
                    <span class="score-label">{sl}</span>
                </div>
            </div>
            <p class="page-url"><a href="{page.get('url', '')}" target="_blank">{page.get('url', '')}</a></p>
            {screenshots_html}
            <table class="findings-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Criterion</th>
                        <th>Score</th>
                        <th>Issue</th>
                        <th>Recommendation</th>
                        <th>Priority</th>
                    </tr>
                </thead>
                <tbody>
                    {findings_html}
                </tbody>
            </table>
        </section>"""

    # Cross-cutting issues
    cross_html = ""
    for issue in cross_cutting:
        pc = priority_color(issue.get("priority", "P2"))
        affected = ", ".join(issue.get("affected_pages", []))
        cross_html += f"""
        <div class="finding-card" style="border-left: 4px solid {pc};">
            <div class="finding-header">
                <span class="priority-badge" style="background:{pc};">{issue.get('priority', 'P2')}</span>
                <strong>{issue.get('title', '')}</strong>
                <span class="affected-pages">Affects: {affected}</span>
            </div>
            <p>{issue.get('description', '')}</p>
        </div>"""

    # Action plan
    def action_rows(items):
        html = ""
        for item in items:
            html += f"<tr><td>{item.get('action','')}</td><td>{item.get('page','')}</td><td>{item.get('impact','')}</td><td>{item.get('effort','')}</td></tr>"
        return html

    quick_wins = action_rows(action_plan.get("quick_wins", []))
    medium_term = action_rows(action_plan.get("medium_term", []))
    strategic = action_rows(action_plan.get("strategic", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clips OS — CRO Audit — {site_name}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
header {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); color: white; padding: 3rem 2rem; margin-bottom: 2rem; border-radius: 12px; }}
header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
header .meta {{ opacity: 0.8; font-size: 0.9rem; }}
.overall-score {{ display: flex; align-items: center; gap: 1.5rem; margin-top: 1.5rem; padding: 1.5rem; background: rgba(255,255,255,0.1); border-radius: 8px; }}
.overall-score .big-score {{ font-size: 3.5rem; font-weight: 800; color: {score_color(overall_score)}; }}
.overall-score .score-context {{ font-size: 1.1rem; }}
.executive-summary {{ background: white; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.executive-summary h2 {{ margin-bottom: 1rem; font-size: 1.3rem; }}
.top-findings {{ margin-bottom: 2rem; }}
.top-findings h2 {{ margin-bottom: 1rem; font-size: 1.3rem; }}
.finding-card {{ background: white; padding: 1.25rem; border-radius: 8px; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.finding-header {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; flex-wrap: wrap; }}
.priority-badge {{ color: white; padding: 2px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }}
.priority-badge-sm {{ color: white; padding: 1px 8px; border-radius: 3px; font-size: 0.75rem; font-weight: 600; }}
.affected-pages {{ font-size: 0.8rem; color: #64748b; margin-left: auto; }}
.page-nav {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 2rem; position: sticky; top: 0; background: #f8fafc; padding: 1rem 0; z-index: 10; }}
.page-nav-link {{ display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: white; border-radius: 6px; text-decoration: none; color: #1e293b; font-weight: 500; box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: transform 0.15s; }}
.page-nav-link:hover {{ transform: translateY(-1px); box-shadow: 0 2px 6px rgba(0,0,0,0.12); }}
.page-score-mini {{ color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; }}
.page-section {{ background: white; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.page-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
.page-header h2 {{ font-size: 1.5rem; }}
.page-score-large {{ color: white; padding: 0.75rem 1.25rem; border-radius: 8px; text-align: center; }}
.page-score-large .score-number {{ font-size: 2rem; font-weight: 800; display: block; }}
.page-score-large .score-label {{ font-size: 0.8rem; opacity: 0.9; }}
.page-url {{ margin-bottom: 1.5rem; }}
.page-url a {{ color: #3b82f6; text-decoration: none; }}
.screenshots {{ display: flex; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }}
.screenshot {{ flex: 1; min-width: 300px; }}
.screenshot.mobile {{ max-width: 250px; flex: 0 0 auto; }}
.screenshot h4 {{ margin-bottom: 0.5rem; color: #64748b; font-size: 0.9rem; }}
.screenshot img {{ width: 100%; border: 1px solid #e2e8f0; border-radius: 6px; }}
.findings-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
.findings-table th {{ background: #f1f5f9; padding: 0.75rem; text-align: left; font-weight: 600; border-bottom: 2px solid #e2e8f0; }}
.findings-table td {{ padding: 0.75rem; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
.score-badge {{ color: white; padding: 2px 10px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; }}
.action-plan {{ background: white; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.action-plan h2 {{ margin-bottom: 1.5rem; font-size: 1.3rem; }}
.action-plan h3 {{ margin: 1.5rem 0 0.75rem; font-size: 1.1rem; }}
.action-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; margin-bottom: 1rem; }}
.action-table th {{ background: #f1f5f9; padding: 0.5rem 0.75rem; text-align: left; font-weight: 600; }}
.action-table td {{ padding: 0.5rem 0.75rem; border-bottom: 1px solid #e2e8f0; }}
footer {{ text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 2rem; }}
@media (max-width: 768px) {{
    .container {{ padding: 1rem; }}
    header {{ padding: 2rem 1rem; }}
    .overall-score {{ flex-direction: column; text-align: center; }}
    .page-header {{ flex-direction: column; gap: 1rem; }}
    .screenshots {{ flex-direction: column; }}
    .screenshot.mobile {{ max-width: 100%; }}
}}
</style>
</head>
<body>
<div class="container">
    <header>
        <h1>Clips OS CRO Audit</h1>
        <div class="meta">{site_name} &bull; {site_url} &bull; {platform} &bull; Audited on {audit_date}</div>
        <div class="overall-score">
            <span class="big-score">{overall_score:.1f}<span style="font-size:1.2rem;opacity:0.7;">/5</span></span>
            <div class="score-context">
                <strong>Overall Conversion Optimization Score</strong><br>
                {score_label(overall_score)} — {len([p for p in pages])} pages analyzed, {sum(len(p.get('findings',[])) for p in pages)} findings
            </div>
        </div>
    </header>

    <div class="executive-summary">
        <h2>Executive Summary</h2>
        <p>{executive_summary}</p>
    </div>

    <div class="top-findings">
        <h2>Top Priority Findings</h2>
        {top_findings_html}
    </div>

    <nav class="page-nav">
        {page_nav_html}
    </nav>

    {pages_html}

    {"<section class='page-section'><h2>Cross-Cutting Issues</h2>" + cross_html + "</section>" if cross_html else ""}

    <div class="action-plan">
        <h2>Prioritized Action Plan</h2>

        <h3>&#9889; Quick Wins (High Impact, Low Effort)</h3>
        <table class="action-table">
            <thead><tr><th>Action</th><th>Page</th><th>Impact</th><th>Effort</th></tr></thead>
            <tbody>{quick_wins if quick_wins else "<tr><td colspan='4'>No quick wins identified</td></tr>"}</tbody>
        </table>

        <h3>&#128736; Medium-Term Improvements</h3>
        <table class="action-table">
            <thead><tr><th>Action</th><th>Page</th><th>Impact</th><th>Effort</th></tr></thead>
            <tbody>{medium_term if medium_term else "<tr><td colspan='4'>None identified</td></tr>"}</tbody>
        </table>

        <h3>&#127919; Strategic Initiatives</h3>
        <table class="action-table">
            <thead><tr><th>Action</th><th>Page</th><th>Impact</th><th>Effort</th></tr></thead>
            <tbody>{strategic if strategic else "<tr><td colspan='4'>None identified</td></tr>"}</tbody>
        </table>
    </div>

    <footer>
        <p>Generated by Clips OS CRO Audit &bull; Framework: LIFT Model + Baymard Heuristics &bull; Scoring: 1-5 scale</p>
        <p>Scores reflect UX/CRO analysis at time of audit. Results may vary with traffic source, user segment, and device.</p>
    </footer>
</div>
</body>
</html>"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate HTML CRO Audit Report")
    parser.add_argument("--input", required=True, help="Path to audit_data.json")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    html = generate_html(data)

    with open(args.output, "w") as f:
        f.write(html)

    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
