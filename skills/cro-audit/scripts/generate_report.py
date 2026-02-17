#!/usr/bin/env python3
"""
Generate a modern, interactive HTML CRO Audit Report from structured JSON data.

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
import sys
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Import shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from report_utils import (
    encode_image, score_color, score_label, priority_color, priority_label,
    lens_icon, svg_score_gauge, svg_score_ring, svg_score_bar, svg_priority_donut,
)


# ---------------------------------------------------------------------------
# Data computation helpers
# ---------------------------------------------------------------------------

def compute_lens_averages(pages: list) -> dict:
    """Compute average score per LIFT lens across all findings."""
    totals = defaultdict(float)
    counts = defaultdict(int)
    for page in pages:
        for f in page.get("findings", []):
            lens = f.get("lens", "")
            if lens:
                totals[lens] += f.get("score", 0)
                counts[lens] += 1
    return {lens: round(totals[lens] / counts[lens], 2) if counts[lens] else 0
            for lens in ["clarity", "relevance", "friction", "anxiety", "urgency", "technical"]}


def compute_score_distribution(pages: list) -> dict:
    """Count findings per score value (1-5)."""
    dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for page in pages:
        for f in page.get("findings", []):
            s = int(round(f.get("score", 3)))
            s = max(1, min(5, s))
            dist[s] += 1
    return dist


def compute_priority_distribution(pages: list) -> dict:
    """Count findings per priority level."""
    dist = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for page in pages:
        for f in page.get("findings", []):
            p = f.get("priority", "P2")
            if p in dist:
                dist[p] += 1
    return dist


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS_STYLES = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f9fafb; color: #334155; line-height: 1.65; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }

/* ---------- Header ---------- */
.header-accent { height: 3px; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899); border-radius: 12px 12px 0 0; }
header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a5f 100%); color: white; padding: 2.5rem 2.5rem 2rem; margin-bottom: 2rem; border-radius: 12px; overflow: hidden; position: relative; }
.header-inner { display: flex; align-items: center; gap: 2rem; flex-wrap: wrap; }
.header-gauge { flex-shrink: 0; }
.header-info { flex: 1; min-width: 200px; }
.header-info h1 { font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
.header-meta { opacity: 0.7; font-size: 0.85rem; margin-bottom: 1rem; }
.header-stats { display: flex; gap: 2rem; flex-wrap: wrap; }
.header-stat { text-align: center; }
.header-stat .stat-value { font-size: 1.5rem; font-weight: 700; display: block; }
.header-stat .stat-label { font-size: 0.75rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.05em; }

/* ---------- Gauge animation ---------- */
@keyframes gauge-fill { from { stroke-dashoffset: var(--gauge-circumference); } }
.gauge-arc { animation: gauge-fill 1.2s ease-out forwards; }

/* ---------- Sections ---------- */
.section-card { background: #ffffff; padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04); }
.section-title { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }

/* ---------- Executive Summary ---------- */
.executive-summary { border-left: 4px solid #3b82f6; padding-left: 1.5rem; }
.executive-summary p { font-size: 1rem; color: #475569; }

/* ---------- Analytics Grid ---------- */
.analytics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
.chart-card { background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04); }
.chart-card h3 { font-size: 1rem; font-weight: 600; margin-bottom: 0.25rem; letter-spacing: -0.01em; }
.chart-card .chart-subtitle { font-size: 0.8rem; color: #6b7280; margin-bottom: 1rem; }
.chart-wrapper { position: relative; height: 240px; }
.donut-wrapper { display: flex; align-items: center; justify-content: center; min-height: 180px; }

/* ---------- Top Findings ---------- */
.finding-card { background: #ffffff; padding: 1.25rem 1.25rem 1.25rem 1.5rem; border-radius: 10px; margin-bottom: 0.75rem; border: 1px solid #e5e7eb; border-left: 4px solid #6b7280; transition: transform 0.15s, box-shadow 0.15s; }
.finding-card:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.finding-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
.priority-badge { color: white; padding: 2px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; white-space: nowrap; }
.affected-pages { font-size: 0.8rem; color: #6b7280; margin-left: auto; }

/* ---------- Page Navigation ---------- */
.page-nav { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; position: sticky; top: 0; background: rgba(249,250,251,0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 0.75rem 0; z-index: 10; border-bottom: 1px solid #e5e7eb; }
.page-nav-link { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.4rem 0.9rem; background: #ffffff; border-radius: 8px; text-decoration: none; color: #334155; font-weight: 500; font-size: 0.85rem; border: 1px solid #e5e7eb; transition: all 0.15s; }
.page-nav-link:hover, .page-nav-link.active { border-color: #3b82f6; box-shadow: 0 0 0 1px #3b82f6; }

/* ---------- Page Section ---------- */
.page-section { background: #ffffff; padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.page-header h2 { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.01em; }
.page-url { margin-bottom: 1.5rem; }
.page-url a { color: #3b82f6; text-decoration: none; font-size: 0.85rem; }
.page-url a:hover { text-decoration: underline; }

/* ---------- Screenshot Tabs ---------- */
.screenshot-tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.screenshot-tab { padding: 0.35rem 1rem; border-radius: 6px; border: 1px solid #e5e7eb; background: #fff; cursor: pointer; font-size: 0.8rem; font-weight: 500; color: #6b7280; transition: all 0.15s; }
.screenshot-tab.active { border-color: #3b82f6; color: #3b82f6; background: #eff6ff; }
.screenshot-panel { display: none; }
.screenshot-panel.active { display: block; }
.device-frame { border-radius: 10px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.device-chrome { background: #f3f4f6; padding: 8px 12px; display: flex; align-items: center; gap: 6px; }
.device-dot { width: 8px; height: 8px; border-radius: 50%; }
.device-dot.red { background: #ef4444; }
.device-dot.yellow { background: #f59e0b; }
.device-dot.green { background: #22c55e; }
.device-frame img { width: 100%; display: block; }
.device-frame.mobile { max-width: 280px; margin: 0 auto; border-radius: 20px; border: 3px solid #d1d5db; }
.device-frame.mobile .device-chrome { justify-content: center; padding: 6px; }
.device-frame.mobile .device-chrome::after { content: ''; width: 40px; height: 4px; border-radius: 2px; background: #d1d5db; }
.device-frame.mobile .device-dot { display: none; }

/* ---------- Findings Cards ---------- */
.findings-list { display: flex; flex-direction: column; gap: 0.75rem; }
.finding-item { padding: 1.25rem; border-radius: 10px; border: 1px solid #e5e7eb; border-left: 4px solid #6b7280; transition: transform 0.15s, box-shadow 0.15s; }
.finding-item:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.finding-item-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
.finding-criterion { font-weight: 600; font-size: 0.95rem; }
.finding-lens { font-size: 0.85rem; color: #6b7280; }
.finding-score-wrap { display: inline-flex; align-items: center; gap: 6px; }
.finding-score-num { font-weight: 700; font-size: 0.85rem; min-width: 20px; }
.finding-issue { color: #475569; font-size: 0.9rem; margin-bottom: 0.5rem; }
.finding-rec { background: #f8fafc; border-radius: 6px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #334155; border: 1px solid #f1f5f9; }
.finding-rec strong { color: #1e293b; }

/* ---------- Action Plan ---------- */
.action-list { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.5rem; }
.action-item { padding: 1rem 1.25rem; border-radius: 10px; border: 1px solid #e5e7eb; border-left: 4px solid #6b7280; display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.5rem; }
.action-text { flex: 1; min-width: 200px; font-size: 0.9rem; }
.action-page { font-size: 0.8rem; color: #6b7280; }
.action-tag { padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
.tag-high { background: #dcfce7; color: #166534; }
.tag-medium { background: #fef9c3; color: #854d0e; }
.tag-low { background: #f3f4f6; color: #4b5563; }
.action-section-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }

/* ---------- Footer ---------- */
footer { text-align: center; color: #94a3b8; font-size: 0.8rem; padding: 2rem 0; }
footer p { margin-bottom: 0.25rem; }

/* ---------- Fade-up animation ---------- */
@keyframes fade-up { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-in { animation: fade-up 0.4s ease-out both; }

/* ---------- Responsive ---------- */
@media (max-width: 768px) {
    .container { padding: 1rem; }
    header { padding: 1.5rem; }
    .header-inner { flex-direction: column; text-align: center; }
    .header-stats { justify-content: center; }
    .analytics-grid { grid-template-columns: 1fr; }
    .page-header { flex-direction: column; gap: 0.75rem; align-items: flex-start; }
    .finding-item-header { flex-direction: column; align-items: flex-start; }
}
"""


# ---------------------------------------------------------------------------
# HTML Generation
# ---------------------------------------------------------------------------

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

    total_findings = sum(len(p.get("findings", [])) for p in pages)
    total_pages = len(pages)

    # Compute chart data
    lens_avgs = compute_lens_averages(pages)
    score_dist = compute_score_distribution(pages)
    priority_dist = compute_priority_distribution(pages)

    # ---- Header ----
    gauge_html = svg_score_gauge(overall_score, size=130)
    header_html = f"""
    <div class="header-accent"></div>
    <header>
        <div class="header-inner">
            <div class="header-gauge">{gauge_html}</div>
            <div class="header-info">
                <h1>CRO Audit Report</h1>
                <div class="header-meta">{site_name} &bull; <a href="{site_url}" target="_blank" style="color:rgba(255,255,255,0.8);">{site_url}</a> &bull; {platform} &bull; {audit_date}</div>
                <div class="header-stats">
                    <div class="header-stat"><span class="stat-value">{total_pages}</span><span class="stat-label">Pages</span></div>
                    <div class="header-stat"><span class="stat-value">{total_findings}</span><span class="stat-label">Findings</span></div>
                    <div class="header-stat"><span class="stat-value">{sum(1 for p in pages for f in p.get('findings',[]) if f.get('priority') in ('P0','P1'))}</span><span class="stat-label">Critical/High</span></div>
                </div>
            </div>
        </div>
    </header>"""

    # ---- Executive Summary ----
    exec_html = f"""
    <div class="section-card executive-summary animate-in">
        <div class="section-title">Executive Summary</div>
        <p>{executive_summary}</p>
    </div>""" if executive_summary else ""

    # ---- Analytics Overview ----
    page_labels_json = json.dumps([p.get("page_type", f"Page {i+1}") for i, p in enumerate(pages)])
    page_scores_json = json.dumps([p.get("page_score", 0) for p in pages])
    page_colors_json = json.dumps([score_color(p.get("page_score", 0)) for p in pages])
    lens_labels_json = json.dumps(["Clarity", "Relevance", "Friction", "Anxiety", "Urgency", "Technical"])
    lens_values_json = json.dumps([lens_avgs.get(k, 0) for k in ["clarity", "relevance", "friction", "anxiety", "urgency", "technical"]])
    score_dist_labels_json = json.dumps(["1 - Critical", "2 - Needs Work", "3 - Acceptable", "4 - Good", "5 - Excellent"])
    score_dist_values_json = json.dumps([score_dist.get(i, 0) for i in range(1, 6)])
    score_dist_colors_json = json.dumps([score_color(i) for i in range(1, 6)])

    donut_html = svg_priority_donut(priority_dist, size=120)

    analytics_html = f"""
    <div class="analytics-grid">
        <div class="chart-card animate-in">
            <h3>Page Scores</h3>
            <p class="chart-subtitle">Conversion optimization score per page type</p>
            <div class="chart-wrapper"><canvas id="chartPageScores"></canvas></div>
        </div>
        <div class="chart-card animate-in">
            <h3>LIFT Lens Analysis</h3>
            <p class="chart-subtitle">Average score across the 6 optimization lenses</p>
            <div class="chart-wrapper"><canvas id="chartLensRadar"></canvas></div>
        </div>
        <div class="chart-card animate-in">
            <h3>Score Distribution</h3>
            <p class="chart-subtitle">How findings spread across 1-5 severity levels</p>
            <div class="chart-wrapper"><canvas id="chartScoreDist"></canvas></div>
        </div>
        <div class="chart-card animate-in">
            <h3>Priority Breakdown</h3>
            <p class="chart-subtitle">Findings by priority level (P0-P3)</p>
            <div class="donut-wrapper">{donut_html}</div>
        </div>
    </div>"""

    # ---- Top Findings ----
    top_findings_html = ""
    for f in top_findings[:5]:
        pc = priority_color(f.get("priority", "P2"))
        top_findings_html += f"""
        <div class="finding-card animate-in" style="border-left-color:{pc};">
            <div class="finding-header">
                <span class="priority-badge" style="background:{pc};">{f.get('priority', 'P2')} &middot; {priority_label(f.get('priority', 'P2'))}</span>
                <strong>{f.get('title', '')}</strong>
            </div>
            <p style="color:#475569;font-size:0.9rem;">{f.get('description', '')}</p>
        </div>"""

    top_section = f"""
    <div class="section-card animate-in">
        <div class="section-title">Top Priority Findings</div>
        {top_findings_html}
    </div>""" if top_findings_html else ""

    # ---- Page Navigation ----
    page_nav_items = ""
    for i, page in enumerate(pages):
        page_type = page.get("page_type", f"Page {i+1}")
        page_id = page_type.lower().replace(" ", "-").replace("/", "-")
        page_score = page.get("page_score", 0)
        ring = svg_score_ring(page_score, size=20)
        page_nav_items += f'<a href="#{page_id}" class="page-nav-link" data-target="{page_id}">{ring} {page_type} <span style="font-size:0.8rem;font-weight:700;color:{score_color(page_score)};">{page_score:.1f}</span></a>'

    page_nav_html = f'<nav class="page-nav">{page_nav_items}</nav>' if page_nav_items else ""

    # ---- Page Sections ----
    pages_html = ""
    for i, page in enumerate(pages):
        page_type = page.get("page_type", f"Page {i+1}")
        page_id = page_type.lower().replace(" ", "-").replace("/", "-")
        page_score = page.get("page_score", 0)
        page_gauge = svg_score_gauge(page_score, size=70, light_track=True)

        # Screenshots with device frames
        desktop_img = encode_image(page.get("desktop_screenshot_path", ""))
        mobile_img = encode_image(page.get("mobile_screenshot_path", ""))

        has_desktop = bool(desktop_img)
        has_mobile = bool(mobile_img)

        screenshot_html = ""
        if has_desktop or has_mobile:
            tabs_html = '<div class="screenshot-tabs">'
            panels_html = ""
            if has_desktop:
                tabs_html += f'<button class="screenshot-tab active" onclick="switchScreenshot(this, \'{page_id}-desktop\')">Desktop</button>'
                panels_html += f'''<div id="{page_id}-desktop" class="screenshot-panel active">
                    <div class="device-frame">
                        <div class="device-chrome"><span class="device-dot red"></span><span class="device-dot yellow"></span><span class="device-dot green"></span></div>
                        <img src="{desktop_img}" alt="{page_type} desktop view" loading="lazy">
                    </div>
                </div>'''
            if has_mobile:
                active_cls = "" if has_desktop else " active"
                tab_active = "" if has_desktop else " active"
                tabs_html += f'<button class="screenshot-tab{tab_active}" onclick="switchScreenshot(this, \'{page_id}-mobile\')">Mobile</button>'
                panels_html += f'''<div id="{page_id}-mobile" class="screenshot-panel{active_cls}">
                    <div class="device-frame mobile">
                        <div class="device-chrome"></div>
                        <img src="{mobile_img}" alt="{page_type} mobile view" loading="lazy">
                    </div>
                </div>'''
            tabs_html += "</div>"
            screenshot_html = tabs_html + panels_html

        # Findings as cards
        findings_cards = ""
        for f in page.get("findings", []):
            fs = f.get("score", 0)
            fpc = priority_color(f.get("priority", "P2"))
            bar = svg_score_bar(fs, width=60)
            li = lens_icon(f.get("lens", ""))
            findings_cards += f"""
            <div class="finding-item" style="border-left-color:{fpc};">
                <div class="finding-item-header">
                    <div class="finding-score-wrap">
                        {bar}
                        <span class="finding-score-num" style="color:{score_color(fs)};">{fs}</span>
                    </div>
                    <span class="finding-criterion">{f.get('criterion_id', '')} &mdash; {f.get('criterion_name', '')}</span>
                    <span class="finding-lens">{li}</span>
                    <span class="priority-badge" style="background:{fpc};margin-left:auto;">{f.get('priority', 'P2')}</span>
                </div>
                <div class="finding-issue">{f.get('issue', '')}</div>
                <div class="finding-rec"><strong>Recommendation:</strong> {f.get('recommendation', '')}</div>
            </div>"""

        pages_html += f"""
        <section id="{page_id}" class="page-section animate-in">
            <div class="page-header">
                <h2>{page_type}</h2>
                {page_gauge}
            </div>
            <p class="page-url"><a href="{page.get('url', '')}" target="_blank">{page.get('url', '')}</a></p>
            {screenshot_html}
            <div class="section-title" style="margin-top:1.5rem;">Findings</div>
            <div class="findings-list">
                {findings_cards if findings_cards else '<p style="color:#6b7280;">No findings for this page.</p>'}
            </div>
        </section>"""

    # ---- Cross-Cutting Issues ----
    cross_html = ""
    if cross_cutting:
        cross_cards = ""
        for issue in cross_cutting:
            pc = priority_color(issue.get("priority", "P2"))
            affected = ", ".join(issue.get("affected_pages", []))
            cross_cards += f"""
            <div class="finding-card" style="border-left-color:{pc};">
                <div class="finding-header">
                    <span class="priority-badge" style="background:{pc};">{issue.get('priority', 'P2')}</span>
                    <strong>{issue.get('title', '')}</strong>
                    <span class="affected-pages">Affects: {affected}</span>
                </div>
                <p style="color:#475569;font-size:0.9rem;">{issue.get('description', '')}</p>
            </div>"""
        cross_html = f"""
        <div class="section-card animate-in">
            <div class="section-title">Cross-Cutting Issues</div>
            {cross_cards}
        </div>"""

    # ---- Action Plan ----
    def impact_tag(val):
        v = (val or "").lower()
        cls = "tag-high" if v == "high" else ("tag-medium" if v == "medium" else "tag-low")
        return f'<span class="action-tag {cls}">Impact: {val}</span>'

    def effort_tag(val):
        v = (val or "").lower()
        cls = "tag-low" if v == "low" else ("tag-medium" if v == "medium" else "tag-high")
        return f'<span class="action-tag {cls}">Effort: {val}</span>'

    def action_cards(items, border_color):
        html = '<div class="action-list">'
        for item in items:
            html += f"""
            <div class="action-item" style="border-left-color:{border_color};">
                <div class="action-text">{item.get('action', '')}</div>
                <span class="action-page">{item.get('page', '')}</span>
                {impact_tag(item.get('impact', ''))}
                {effort_tag(item.get('effort', ''))}
            </div>"""
        html += '</div>'
        return html if items else '<p style="color:#6b7280;font-size:0.9rem;">None identified.</p>'

    qw = action_plan.get("quick_wins", [])
    mt = action_plan.get("medium_term", [])
    st = action_plan.get("strategic", [])

    action_html = f"""
    <div class="section-card animate-in">
        <div class="section-title">Prioritized Action Plan</div>

        <div class="action-section-title">&#9889; Quick Wins <span style="font-size:0.8rem;font-weight:400;color:#6b7280;">&mdash; High Impact, Low Effort</span></div>
        {action_cards(qw, '#22c55e')}

        <div class="action-section-title" style="margin-top:1.5rem;">&#128736; Medium-Term Improvements</div>
        {action_cards(mt, '#3b82f6')}

        <div class="action-section-title" style="margin-top:1.5rem;">&#127919; Strategic Initiatives <span style="font-size:0.8rem;font-weight:400;color:#6b7280;">&mdash; High Impact, High Effort</span></div>
        {action_cards(st, '#8b5cf6')}
    </div>"""

    # ---- Footer ----
    footer_html = """
    <footer>
        <p>Generated by <strong>Clips OS</strong> CRO Audit &bull; LIFT Model + Baymard Heuristics &bull; 1-5 Scoring</p>
        <p>Scores reflect UX/CRO analysis at time of audit. Results may vary with traffic source, user segment, and device.</p>
    </footer>"""

    # ---- JavaScript ----
    js_block = f"""
<script>
// Screenshot tab toggle
function switchScreenshot(btn, panelId) {{
    const parent = btn.closest('.page-section');
    parent.querySelectorAll('.screenshot-tab').forEach(t => t.classList.remove('active'));
    parent.querySelectorAll('.screenshot-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(panelId).classList.add('active');
}}

// IntersectionObserver for sticky nav
document.addEventListener('DOMContentLoaded', function() {{
    const nav = document.querySelector('.page-nav');
    if (!nav) return;
    const links = nav.querySelectorAll('.page-nav-link');
    const sections = document.querySelectorAll('.page-section');
    if (!sections.length) return;
    const observer = new IntersectionObserver(entries => {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                links.forEach(l => l.classList.remove('active'));
                const target = entry.target.id;
                const active = nav.querySelector('[data-target="' + target + '"]');
                if (active) active.classList.add('active');
            }}
        }});
    }}, {{ rootMargin: '-20% 0px -70% 0px' }});
    sections.forEach(s => observer.observe(s));

    // Chart.js initialization
    if (typeof Chart === 'undefined') return;

    const pageLabels = {page_labels_json};
    const pageScores = {page_scores_json};
    const pageColors = {page_colors_json};
    const lensLabels = {lens_labels_json};
    const lensValues = {lens_values_json};
    const scoreBins = {score_dist_labels_json};
    const scoreCounts = {score_dist_values_json};
    const scoreBarColors = {score_dist_colors_json};

    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#6b7280';

    // Page Scores — horizontal bar
    new Chart(document.getElementById('chartPageScores'), {{
        type: 'bar',
        data: {{
            labels: pageLabels,
            datasets: [{{ data: pageScores, backgroundColor: pageColors, borderRadius: 6, barThickness: 28 }}]
        }},
        options: {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ctx.raw.toFixed(1) + '/5' }} }} }},
            scales: {{
                x: {{ min: 0, max: 5, grid: {{ color: '#f3f4f6' }}, ticks: {{ stepSize: 1 }} }},
                y: {{ grid: {{ display: false }} }}
            }}
        }}
    }});

    // LIFT Lens — radar
    new Chart(document.getElementById('chartLensRadar'), {{
        type: 'radar',
        data: {{
            labels: lensLabels,
            datasets: [{{
                data: lensValues,
                backgroundColor: 'rgba(59,130,246,0.15)',
                borderColor: '#3b82f6',
                pointBackgroundColor: '#3b82f6',
                pointRadius: 4,
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                r: {{ min: 0, max: 5, ticks: {{ stepSize: 1, backdropColor: 'transparent' }}, grid: {{ color: '#e5e7eb' }}, pointLabels: {{ font: {{ size: 11, weight: '500' }} }} }}
            }}
        }}
    }});

    // Score Distribution — vertical bar
    new Chart(document.getElementById('chartScoreDist'), {{
        type: 'bar',
        data: {{
            labels: scoreBins,
            datasets: [{{ data: scoreCounts, backgroundColor: scoreBarColors, borderRadius: 6, barThickness: 36 }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }}, grid: {{ color: '#f3f4f6' }} }},
                x: {{ grid: {{ display: false }} }}
            }}
        }}
    }});
}});
</script>"""

    # ---- Assemble full HTML ----
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clips OS — CRO Audit — {site_name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>{CSS_STYLES}</style>
</head>
<body>
<div class="container">
    {header_html}
    {exec_html}
    {analytics_html}
    {top_section}
    {page_nav_html}
    {pages_html}
    {cross_html}
    {action_html}
    {footer_html}
</div>
{js_block}
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
