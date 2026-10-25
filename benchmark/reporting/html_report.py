"""Interactive Standalone HTML Report Generator for Benchmark Runs."""

import html
import json
from pathlib import Path
from typing import Any, Dict, Optional

from benchmark.trust.assessment import TrustAssessmentEngine


class BenchmarkHtmlReportGenerator:
    """Generates a self-contained, interactive HTML benchmark report."""

    @classmethod
    def generate_report(
        cls,
        run_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Renders comprehensive HTML benchmark report with side-by-side document inspection."""
        run_id = run_data.get("run_id", "RUN-UNKNOWN")
        summary = run_data.get("summary", {})
        metadata = run_data.get("metadata", {})
        cases = run_data.get("cases", [])
        trust_report = TrustAssessmentEngine.generate_trust_report(run_data)

        # Build cases table rows
        rows_html = []
        for c in cases:
            case = c.get("case", {})
            verdict = c.get("verdict", {})
            scores = verdict.get("component_scores", {})
            v_val = verdict.get("verdict", "FAIL")
            v_badge_class = "badge-pass" if v_val == "PASS" else ("badge-warn" if v_val == "CONDITIONAL" else "badge-fail")

            rows_html.append(f"""
            <tr class="case-row" data-level="{case.get('level')}" data-verdict="{v_val}" onclick="inspectCase('{case.get('id')}')">
              <td><strong>{html.escape(case.get('id', ''))}</strong></td>
              <td>Level {case.get('level')}</td>
              <td>{html.escape(case.get('domain', ''))}</td>
              <td><span class="badge {v_badge_class}">{v_val}</span></td>
              <td><strong>{verdict.get('composite_score', 0.0)}</strong></td>
              <td>{scores.get('language_quality', 0.0)}</td>
              <td>{scores.get('semantic_preservation', 0.0)}</td>
              <td>{scores.get('factual_integrity', 0.0)}</td>
              <td>{scores.get('academic_quality', 0.0)}</td>
              <td>{c.get('latency_ms', 0.0)} ms</td>
            </tr>
            """)

        cases_json_escaped = json.dumps(cases).replace("</script>", "<\\/script>")
        trust_json_escaped = json.dumps(trust_report).replace("</script>", "<\\/script>")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Turnitout Benchmark & Trust Report — {run_id}</title>
  <style>
    :root {{
      --bg: #0B0F19;
      --card: #111827;
      --card-border: rgba(255, 255, 255, 0.08);
      --text: #F9FAFB;
      --text-muted: #9CA3AF;
      --primary: #3B82F6;
      --success: #10B981;
      --warning: #F59E0B;
      --danger: #EF4444;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: var(--font); background: var(--bg); color: var(--text); padding: 2rem 1.5rem; line-height: 1.5; }}
    .container {{ max-width: 1300px; margin: 0 auto; }}
    
    header {{ border-bottom: 1px solid var(--card-border); padding-bottom: 1.5rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: flex-end; }}
    h1 {{ font-size: 1.8rem; font-weight: 800; }}
    .meta-text {{ color: var(--text-muted); font-size: 0.9rem; }}

    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
    .stat-card {{ background: var(--card); border: 1px solid var(--card-border); padding: 1.25rem; border-radius: 12px; text-align: center; }}
    .stat-val {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 0.25rem; }}
    .stat-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); }}

    .badge {{ padding: 3px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; display: inline-block; }}
    .badge-pass {{ background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid var(--success); }}
    .badge-warn {{ background: rgba(245, 158, 11, 0.15); color: var(--warning); border: 1px solid var(--warning); }}
    .badge-fail {{ background: rgba(239, 68, 68, 0.15); color: var(--danger); border: 1px solid var(--danger); }}

    .section-card {{ background: var(--card); border: 1px solid var(--card-border); border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; }}
    h2 {{ font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }}

    .filter-bar {{ display: flex; gap: 1rem; margin-bottom: 1rem; }}
    select, input {{ background: #1F2937; border: 1px solid var(--card-border); color: var(--text); padding: 0.5rem 0.75rem; border-radius: 6px; }}

    table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
    th, td {{ padding: 0.75rem 0.85rem; border-bottom: 1px solid var(--card-border); text-align: left; }}
    th {{ color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; }}
    tr.case-row:hover {{ background: rgba(255, 255, 255, 0.03); cursor: pointer; }}

    .inspector-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }}
    .text-box {{ background: #1F2937; padding: 1rem; border-radius: 8px; font-size: 0.9rem; white-space: pre-wrap; word-break: break-word; min-height: 200px; max-height: 350px; overflow-y: auto; }}
    
    .trust-q {{ background: rgba(255, 255, 255, 0.02); border-left: 3px solid var(--primary); padding: 1rem; margin-bottom: 1rem; border-radius: 0 8px 8px 0; }}
    .trust-q h3 {{ font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem; }}
    .trust-q p {{ font-size: 0.875rem; color: var(--text-muted); }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>Turnitout Benchmark & Trust Evaluation</h1>
        <div class="meta-text">Run ID: <strong>{run_id}</strong> &bull; Model: <strong>{metadata.get('model_version', 'Core 2.6.0')}</strong> &bull; Total Cases: <strong>{summary.get('total_cases', 0)}</strong></div>
      </div>
      <div>
        <span class="badge {'badge-pass' if summary.get('pass_rate', 0) > 70 else 'badge-warn'}">Pass Rate: {summary.get('pass_rate', 0)}%</span>
      </div>
    </header>

    <!-- Top Metric Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-val" style="color: var(--primary);">{summary.get('total_cases', 0)}</div>
        <div class="stat-label">Total Test Cases</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: var(--success);">{summary.get('passed', 0)}</div>
        <div class="stat-label">Passed</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: var(--warning);">{summary.get('conditional', 0)}</div>
        <div class="stat-label">Conditional (Review)</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: var(--danger);">{summary.get('failed', 0)}</div>
        <div class="stat-label">Failed (Critical Veto)</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: #A78BFA;">{summary.get('avg_composite_score', 0)}</div>
        <div class="stat-label">Avg Composite Score</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: #6EE7B7;">{summary.get('avg_latency_ms', 0)} ms</div>
        <div class="stat-label">Avg Execution Latency</div>
      </div>
    </div>

    <!-- Section 1: Automated Trust Report Summary -->
    <div class="section-card">
      <h2>🛡️ Automated Trust Assessment (Core Findings)</h2>
      <div id="trustQuestionsContainer">
        <!-- Rendered via JS -->
      </div>
    </div>

    <!-- Section 2: Interactive Test Inspector -->
    <div class="section-card" id="inspectorCard" style="display: none;">
      <h2>🔍 Document Inspection: <span id="inspectedCaseId"></span> (<span id="inspectedVerdict"></span>)</h2>
      <div class="meta-text" id="inspectedMeta" style="margin-bottom: 1rem;"></div>
      
      <div class="inspector-grid">
        <div>
          <h4 style="margin-bottom: 0.5rem; color: var(--text-muted);">Original Source Document</h4>
          <div class="text-box" id="origTextBox"></div>
        </div>
        <div>
          <h4 style="margin-bottom: 0.5rem; color: var(--text-muted);">Humanized Output</h4>
          <div class="text-box" id="humanTextBox"></div>
        </div>
      </div>

      <div style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
        <h4 style="margin-bottom: 0.5rem;">Evaluator Findings & Failed Checks:</h4>
        <div id="inspectedFailedChecks" style="font-size: 0.85rem; color: var(--text-muted);"></div>
      </div>
    </div>

    <!-- Section 3: Test Case Explorer Table -->
    <div class="section-card">
      <h2>📊 All Benchmark Test Cases</h2>
      <div class="filter-bar">
        <select id="levelFilter" onchange="filterCases()">
          <option value="ALL">All Levels (1 to 5)</option>
          <option value="1">Level 1 (Everyday)</option>
          <option value="2">Level 2 (Professional)</option>
          <option value="3">Level 3 (Analytical)</option>
          <option value="4">Level 4 (Academic Review)</option>
          <option value="5">Level 5 (Proposal Structure)</option>
        </select>
        <select id="verdictFilter" onchange="filterCases()">
          <option value="ALL">All Verdicts</option>
          <option value="PASS">PASS</option>
          <option value="CONDITIONAL">CONDITIONAL</option>
          <option value="FAIL">FAIL</option>
        </select>
      </div>

      <div style="overflow-x: auto;">
        <table>
          <thead>
            <tr>
              <th>Test ID</th>
              <th>Difficulty</th>
              <th>Domain</th>
              <th>Verdict</th>
              <th>Composite</th>
              <th>Language</th>
              <th>Semantic</th>
              <th>Factual</th>
              <th>Academic</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody id="casesTableBody">
            {"".join(rows_html)}
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <script>
    const casesData = {cases_json_escaped};
    const trustData = {trust_json_escaped};

    // Render Trust Questions
    const tqContainer = document.getElementById("trustQuestionsContainer");
    if (trustData && trustData.questions) {{
      const q = trustData.questions;
      const qList = [
        ["1. Does it improve writing quality?", q.q1_language_quality.summary, q.q1_language_quality.verdict],
        ["2. Does it preserve original meaning?", q.q2_semantic_preservation.summary, q.q2_semantic_preservation.verdict],
        ["3. Does it introduce facts or errors?", q.q3_factual_integrity.summary, q.q3_factual_integrity.verdict],
        ["4. Does it preserve citations and research logic?", q.q4_citation_and_research_logic.summary, q.q4_citation_and_research_logic.verdict],
        ["5. Consistency across difficulty levels?", q.q5_consistency_across_levels.summary, q.q5_consistency_across_levels.verdict],
        ["6. Repeated-run deterministic consistency?", q.q6_repeated_run_consistency.summary, q.q6_repeated_run_consistency.verdict],
        ["7. Where does it fail?", q.q7_failure_patterns.summary, q.q7_failure_patterns.verdict],
        ["8. Safe document types for automatic processing?", q.q8_safe_document_types.summary, q.q8_safe_document_types.verdict],
        ["9. Outputs requiring mandatory human review?", q.q9_human_review_required.summary, q.q9_human_review_required.verdict]
      ];

      qList.forEach(([title, summary, verdict]) => {{
        const div = document.createElement("div");
        div.className = "trust-q";
        div.innerHTML = `<h3>${{title}} <span class="badge badge-pass" style="font-size: 0.65rem; margin-left: 0.5rem;">${{verdict}}</span></h3><p>${{summary}}</p>`;
        tqContainer.appendChild(div);
      }});
    }}

    // Case Inspection Logic
    function inspectCase(id) {{
      const item = casesData.find(c => c.test_id === id);
      if (!item) return;

      const card = document.getElementById("inspectorCard");
      card.style.display = "block";
      document.getElementById("inspectedCaseId").textContent = id;
      document.getElementById("inspectedVerdict").textContent = item.verdict.verdict;
      document.getElementById("inspectedMeta").textContent = `Level ${{item.case.level}}: ${{item.case.level_name}} | Domain: ${{item.case.domain}} | Latency: ${{item.latency_ms}} ms`;
      document.getElementById("origTextBox").textContent = item.original_text;
      document.getElementById("humanTextBox").textContent = item.humanized_text;

      const failedBox = document.getElementById("inspectedFailedChecks");
      const fails = item.verdict.critical_failures.concat(item.verdict.failed_checks);
      if (fails.length === 0) {{
        failedBox.innerHTML = "<span style='color: var(--success);'>✓ Zero critical failures or threshold defects detected.</span>";
      }} else {{
        failedBox.innerHTML = "<ul>" + fails.map(f => `<li style="color: var(--danger);">${{f}}</li>`).join("") + "</ul>";
      }}

      card.scrollIntoView({{ behavior: "smooth" }});
    }}

    // Table Filter Logic
    function filterCases() {{
      const lvl = document.getElementById("levelFilter").value;
      const v = document.getElementById("verdictFilter").value;
      const rows = document.querySelectorAll(".case-row");

      rows.forEach(r => {{
        const rowLvl = r.getAttribute("data-level");
        const rowV = r.getAttribute("data-verdict");
        const matchLvl = (lvl === "ALL" || lvl === rowLvl);
        const matchV = (v === "ALL" || v === rowV);
        r.style.display = (matchLvl && matchV) ? "" : "none";
      }});
    }}
  </script>
</body>
</html>
"""
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(html_content)

        return html_content
