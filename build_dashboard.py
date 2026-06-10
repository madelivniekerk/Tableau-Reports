import json, csv

rows = []
with open(r'C:\Users\madel\Tableau-Reports\jira_mock_data.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append({
            'key':     r['Issue Key'],
            'project': r['Project'],
            'type':    r['Issue Type'],
            'summary': r['Summary'],
            'status':  r['Status'],
            'priority':r['Priority'],
            'assignee':r['Assignee'],
            'team':    r['Team'],
            'sprint':  r['Sprint'],
            'epic':    r['Epic'],
            'sp':      int(r['Story Points']) if r['Story Points'] else 0,
            'est':     int(r['Original Estimate (hrs)']) if r['Original Estimate (hrs)'] else 0,
            'spent':   int(r['Time Spent (hrs)']) if r['Time Spent (hrs)'] else 0,
            'cycle':   int(r['Cycle Time (days)']) if r['Cycle Time (days)'] else 0,
            'component':r['Component'],
            'label':   r['Labels'],
        })

js_data = json.dumps(rows, separators=(',', ':'))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jira Process Engineering &middot; Resource Planning Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
:root{
  --bg1:#061933;--bg2:#0a2140;--bg3:#0d2850;
  --blue:#2684ff;--blue2:#4d9fff;
  --cyan:#00c7e6;--cyan2:#6be0f5;
  --green:#22c55e;--amber:#f59e0b;--red:#ef4444;--purple:#a855f7;
  --text:#e6f0ff;--muted:#5e82b0;--faint:#0e2a4a;
  --card-border:rgba(38,132,255,0.20);
  --grid:rgba(38,132,255,0.10);
}
body{min-height:100vh;color:var(--text);font-family:'Inter',system-ui,sans-serif;
  background-color:var(--bg1);
  background-image:
    radial-gradient(ellipse 80% 50% at 10% 20%,rgba(38,132,255,0.22) 0%,transparent 60%),
    radial-gradient(ellipse 60% 70% at 90% 80%,rgba(0,82,204,0.18) 0%,transparent 60%),
    linear-gradient(180deg,#061933 0%,#082040 40%,#061933 100%);
  animation:bgDrift 24s ease-in-out infinite alternate;position:relative;overflow-x:hidden;}
@keyframes bgDrift{0%{background-position:0% 50%,100% 50%,0% 0%;}100%{background-position:100% 0%,0% 100%,0% 0%;}}
body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 30% 20% at 20% 30%,rgba(38,132,255,0.08) 0%,transparent 70%);}

/* Header */
.header{position:relative;z-index:2;background:rgba(4,18,42,0.92);backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(38,132,255,0.22);padding:24px 48px 20px;}
.header-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:20px;gap:20px;}
.logo-group{display:flex;align-items:center;gap:14px;}
.logo-icon{width:48px;height:48px;border-radius:14px;flex-shrink:0;
  background:linear-gradient(135deg,#0047b3,#2684ff,#4d9fff);
  display:flex;align-items:center;justify-content:center;font-size:24px;
  box-shadow:0 0 24px rgba(38,132,255,0.45);}
.logo-title{font-family:'Space Grotesk',sans-serif;font-size:19px;font-weight:700;color:#d6e8ff;letter-spacing:-0.01em;}
.logo-sub{font-size:11px;color:var(--blue2);margin-top:3px;letter-spacing:0.07em;font-weight:500;}
.live-counter{text-align:right;background:rgba(38,132,255,0.10);
  border:1px solid rgba(38,132,255,0.30);border-radius:12px;padding:10px 16px;}
.counter-label{font-size:10px;color:#a5c8ff;font-weight:600;letter-spacing:0.08em;margin-bottom:4px;}
.counter-value{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700;color:var(--blue2);}
.counter-sub{font-size:9px;color:var(--muted);margin-top:2px;}
.kpi-row{display:grid;grid-template-columns:repeat(5,1fr);gap:0;
  border:1px solid rgba(38,132,255,0.20);border-radius:12px;overflow:hidden;}
.kpi{padding:14px 18px;border-right:1px solid rgba(38,132,255,0.12);background:rgba(6,25,51,0.65);}
.kpi:last-child{border-right:none;}
.kpi-val{font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:700;line-height:1;margin-bottom:4px;}
.kpi-lbl{font-size:10px;color:var(--muted);font-weight:500;letter-spacing:0.03em;}
.kpi-note{font-size:9px;color:var(--muted);opacity:0.65;margin-top:2px;}
.kpi.c1 .kpi-val{color:var(--blue2);}
.kpi.c2 .kpi-val{color:var(--green);}
.kpi.c3 .kpi-val{color:var(--amber);}
.kpi.c4 .kpi-val{color:var(--cyan2);}
.kpi.c5 .kpi-val{color:var(--red);}

/* Filter bar */
.filter-bar{position:relative;z-index:2;background:rgba(4,18,42,0.80);
  border-bottom:1px solid rgba(38,132,255,0.14);padding:0 48px;
  display:flex;flex-direction:column;gap:0;}
.filter-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:12px 0;border-bottom:1px solid rgba(38,132,255,0.08);}
.filter-row:last-child{border-bottom:none;}
.filter-row.hierarchy-row{background:rgba(38,132,255,0.04);padding:14px 0;border-bottom:1px solid rgba(38,132,255,0.14);}
.filter-label{font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:600;
  letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);white-space:nowrap;min-width:90px;}
.filter-sep{width:1px;height:28px;background:rgba(38,132,255,0.15);margin:0 4px;}
.filter-group{display:flex;align-items:center;gap:5px;flex-wrap:wrap;}
.pill{display:inline-flex;align-items:center;gap:5px;padding:5px 11px;border-radius:20px;
  font-size:11px;font-weight:500;cursor:pointer;border:1px solid rgba(38,132,255,0.20);
  background:rgba(38,132,255,0.06);color:var(--muted);transition:all .15s;white-space:nowrap;}
.pill:hover{border-color:rgba(38,132,255,0.50);color:var(--text);background:rgba(38,132,255,0.12);}
.pill.active{background:var(--blue);border-color:var(--blue);color:#fff;
  box-shadow:0 2px 10px rgba(38,132,255,0.35);}
.pill-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.hierarchy-pill{padding:7px 14px;font-size:12px;font-weight:600;}
.hierarchy-pill.active{box-shadow:0 3px 14px rgba(38,132,255,0.45);}

/* Story panel */
.story-panel{position:relative;z-index:2;background:rgba(38,132,255,0.07);
  border-bottom:1px solid rgba(38,132,255,0.14);padding:14px 48px;
  display:flex;align-items:flex-start;gap:14px;}
.story-icon{font-size:22px;flex-shrink:0;margin-top:1px;}
.story-title{font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:600;color:var(--blue2);margin-bottom:4px;}
.story-text{font-size:12px;color:var(--muted);line-height:1.65;max-width:1100px;}
.story-text strong{color:var(--text);}

/* Page */
.page{max-width:1280px;margin:0 auto;padding:20px 24px 60px;position:relative;z-index:2;}
.sec{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:600;letter-spacing:0.14em;
  color:var(--blue2);text-transform:uppercase;margin-bottom:14px;padding-bottom:8px;
  border-bottom:1px solid var(--faint);}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px;}
.mb{margin-bottom:18px;}
.card{background:rgba(6,25,51,0.80);backdrop-filter:blur(14px);
  border:1px solid var(--card-border);border-radius:16px;padding:22px;
  box-shadow:0 8px 32px rgba(0,0,0,0.40),inset 0 1px 0 rgba(38,132,255,0.08);}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:600;color:#d6e8ff;margin-bottom:3px;}
.card-sub{font-size:11px;color:var(--muted);margin-bottom:16px;line-height:1.5;}
.ch220{position:relative;height:220px;}
.ch260{position:relative;height:260px;}
.ch300{position:relative;height:300px;}

/* Kanban */
.kanban-wrap{position:relative;margin-bottom:18px;background:rgba(4,18,42,0.92);
  backdrop-filter:blur(10px);border:1px solid rgba(38,132,255,0.20);border-radius:16px;overflow:hidden;
  box-shadow:0 8px 40px rgba(0,0,0,0.5);}
.kanban-header{padding:18px 22px 0;display:flex;align-items:center;justify-content:space-between;}
.kanban-legend{display:flex;gap:20px;padding:12px 22px 16px;flex-wrap:wrap;
  border-top:1px solid var(--faint);margin-top:10px;}
.kl-item{display:flex;align-items:center;gap:7px;font-size:11px;color:var(--muted);}
.kl-dot{width:10px;height:10px;border-radius:3px;flex-shrink:0;}

/* Stat blocks */
.stat-blocks{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}
.stat-block{background:rgba(6,25,51,0.80);backdrop-filter:blur(14px);
  border:1px solid var(--card-border);border-radius:14px;padding:18px 20px;text-align:center;}
.sb-val{font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:700;margin-bottom:4px;}
.sb-lbl{font-size:10px;color:var(--muted);font-weight:500;letter-spacing:0.05em;}
.sb-sub{font-size:9px;color:var(--muted);margin-top:2px;opacity:0.7;}

/* Tableau guide */
.t-guide{background:rgba(6,25,51,0.65);border:1px solid var(--card-border);border-radius:14px;
  padding:18px 20px;display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:18px;}
.tg-item{text-align:center;}
.tg-icon{font-size:16px;margin-bottom:4px;}
.tg-name{font-size:10px;font-weight:600;color:var(--blue2);margin-bottom:2px;}
.tg-how{font-size:9px;color:var(--muted);line-height:1.4;}
.footer{text-align:center;padding:16px;font-size:10px;color:var(--muted);position:relative;z-index:2;}

/* Kanban tooltip */
#kanban-tip{display:none;position:fixed;z-index:999;pointer-events:none;
  background:rgba(4,14,36,0.97);border:1px solid rgba(38,132,255,0.45);
  border-radius:10px;padding:10px 14px;max-width:300px;
  box-shadow:0 8px 32px rgba(0,0,0,0.6);}
#kt-key{font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;
  color:var(--blue2);margin-bottom:5px;}
#kt-summary{font-size:11px;color:var(--text);line-height:1.5;margin-bottom:7px;}
#kt-sp{font-size:11px;font-weight:600;margin-bottom:3px;}
#kt-meta{font-size:10px;color:var(--muted);line-height:1.6;}
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    <div class="logo-group">
      <div class="logo-icon">&#9881;&#65039;</div>
      <div>
        <div class="logo-title">Process Engineering &middot; Resource Planning</div>
        <div class="logo-sub">Jira Sprint Analytics &middot; 6 Sprints &middot; 200 Issues &middot; 4 Teams &middot; 6 Epics</div>
      </div>
    </div>
    <div class="live-counter">
      <div class="counter-label">&#11044; HOURS LOGGED &mdash; ACTIVE ISSUES</div>
      <div class="counter-value" id="liveCounter">3,366.0</div>
      <div class="counter-sub">&uarr; 10 engineers &middot; 4 teams &middot; live tracking</div>
    </div>
  </div>
  <div class="kpi-row">
    <div class="kpi c1"><div class="kpi-val" id="kpi-total">200</div><div class="kpi-lbl">Total Issues</div><div class="kpi-note" id="kpi-total-note">4 projects &middot; 6 sprints</div></div>
    <div class="kpi c2"><div class="kpi-val" id="kpi-done">29</div><div class="kpi-lbl">Done</div><div class="kpi-note" id="kpi-done-note">14.5% completion rate</div></div>
    <div class="kpi c3"><div class="kpi-val" id="kpi-blocked">40</div><div class="kpi-lbl">Blocked</div><div class="kpi-note" id="kpi-blocked-note">20% &mdash; exceeds Done</div></div>
    <div class="kpi c4"><div class="kpi-val" id="kpi-sp">109</div><div class="kpi-lbl">Story Points Done</div><div class="kpi-note">Completed issues only</div></div>
    <div class="kpi c5"><div class="kpi-val" id="kpi-ct">9.5d</div><div class="kpi-lbl">Avg Cycle Time</div><div class="kpi-note">Created &rarr; resolved</div></div>
  </div>
</div>

<!-- Filter bar -->
<div class="filter-bar">

  <!-- Row 1: Issue Hierarchy (most prominent) -->
  <div class="filter-row hierarchy-row">
    <span class="filter-label" style="color:var(--blue2);">&#128204; Hierarchy</span>
    <span class="pill hierarchy-pill active" data-group="type" data-val="">ALL TYPES</span>
    <span class="pill hierarchy-pill" data-group="type" data-val="Epic"><span class="pill-dot" style="background:#a855f7"></span>&#9889; Epic</span>
    <span class="pill hierarchy-pill" data-group="type" data-val="Story"><span class="pill-dot" style="background:#22c55e"></span>&#128214; Story</span>
    <span class="pill hierarchy-pill" data-group="type" data-val="Task"><span class="pill-dot" style="background:#2684ff"></span>&#9989; Task</span>
    <span class="pill hierarchy-pill" data-group="type" data-val="Sub-task"><span class="pill-dot" style="background:#00c7e6"></span>&#128279; Sub-task</span>
    <span class="pill hierarchy-pill" data-group="type" data-val="Bug"><span class="pill-dot" style="background:#ef4444"></span>&#128027; Bug</span>
  </div>

  <!-- Row 2: Project + Sprint -->
  <div class="filter-row">
    <span class="filter-label">Project</span>
    <span class="pill active" data-group="project" data-val="">ALL</span>
    <span class="pill" data-group="project" data-val="INFRA"><span class="pill-dot" style="background:#2684ff"></span>INFRA</span>
    <span class="pill" data-group="project" data-val="CRM"><span class="pill-dot" style="background:#00c7e6"></span>CRM</span>
    <span class="pill" data-group="project" data-val="DATA"><span class="pill-dot" style="background:#a855f7"></span>DATA</span>
    <span class="pill" data-group="project" data-val="OPS"><span class="pill-dot" style="background:#f59e0b"></span>OPS</span>
    <div class="filter-sep"></div>
    <span class="filter-label">Sprint</span>
    <span class="pill active" data-group="sprint" data-val="">ALL</span>
    <span class="pill" data-group="sprint" data-val="Sprint 1">S1</span>
    <span class="pill" data-group="sprint" data-val="Sprint 2">S2</span>
    <span class="pill" data-group="sprint" data-val="Sprint 3">S3</span>
    <span class="pill" data-group="sprint" data-val="Sprint 4">S4</span>
    <span class="pill" data-group="sprint" data-val="Sprint 5">S5</span>
    <span class="pill" data-group="sprint" data-val="Sprint 6">S6</span>
  </div>

  <!-- Row 3: Epic (own row so all 6 names are always visible) -->
  <div class="filter-row">
    <span class="filter-label" style="color:var(--purple, #a855f7);">&#9889; Epic</span>
    <span class="pill active" data-group="epic" data-val="">ALL EPICS</span>
    <span class="pill" data-group="epic" data-val="API v2 Migration"><span class="pill-dot" style="background:#2684ff"></span>API v2 Migration</span>
    <span class="pill" data-group="epic" data-val="Ops Automation"><span class="pill-dot" style="background:#00c7e6"></span>Ops Automation</span>
    <span class="pill" data-group="epic" data-val="Platform Stability"><span class="pill-dot" style="background:#a855f7"></span>Platform Stability</span>
    <span class="pill" data-group="epic" data-val="Reporting Suite"><span class="pill-dot" style="background:#22c55e"></span>Reporting Suite</span>
    <span class="pill" data-group="epic" data-val="Auth Overhaul"><span class="pill-dot" style="background:#f59e0b"></span>Auth Overhaul</span>
    <span class="pill" data-group="epic" data-val="Customer Data Pipeline"><span class="pill-dot" style="background:#ef4444"></span>Customer Data Pipeline</span>
  </div>

</div>

<!-- Story panel -->
<div class="story-panel">
  <div class="story-icon" id="story-icon">&#128218;</div>
  <div>
    <div class="story-title" id="story-title">Portfolio Overview &mdash; All Projects &middot; All Sprints</div>
    <div class="story-text" id="story-text"><strong>200 issues</strong> across 4 projects (INFRA, CRM, DATA, OPS) and 6 epics over 6 sprints. Completion rate is <strong>14.5%</strong> with <strong>40 blocked issues</strong> exceeding the 29 done &mdash; a key process risk. Click any filter above to drill in and reveal the story behind the numbers.</div>
  </div>
</div>

<div id="kanban-tip">
  <div id="kt-key"></div>
  <div id="kt-summary"></div>
  <div id="kt-sp"></div>
  <div id="kt-meta"></div>
</div>

<div class="page">

  <div class="sec">Kanban Flow &middot; Live Issue Movement Simulation</div>
  <div class="kanban-wrap">
    <div class="kanban-header">
      <div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:600;color:#d6e8ff;">Issue Flow Across Workflow Stages &middot; Process Visibility</div>
        <div style="font-size:11px;color:var(--muted);margin-top:2px;">Each block = one issue. Amber = Blocked. Column height = congestion level. A growing Blocked column is the key bottleneck signal.</div>
      </div>
      <div style="font-size:10px;color:var(--muted);font-style:italic;">Simulated &middot; based on sprint data distribution</div>
    </div>
    <canvas id="kanbanCanvas" style="display:block;width:100%;"></canvas>
    <div class="kanban-legend">
      <div class="kl-item"><div class="kl-dot" style="background:rgba(148,163,184,0.8);"></div><span id="kl-todo">To Do (44)</span></div>
      <div class="kl-item"><div class="kl-dot" style="background:rgba(38,132,255,0.9);"></div><span id="kl-inprog">In Progress (35)</span></div>
      <div class="kl-item"><div class="kl-dot" style="background:rgba(0,199,230,0.9);"></div><span id="kl-inrev">In Review (52)</span></div>
      <div class="kl-item"><div class="kl-dot" style="background:rgba(245,158,11,0.95);"></div><span id="kl-blocked">Blocked (40) &larr; bottleneck</span></div>
      <div class="kl-item"><div class="kl-dot" style="background:rgba(34,197,94,0.9);"></div><span id="kl-done">Done (29)</span></div>
    </div>
  </div>

  <div class="sec">Sprint Velocity &middot; Resource Workload</div>
  <div class="grid2">
    <div class="card">
      <div class="card-title">Sprint Velocity &mdash; Story Points Completed</div>
      <div class="card-sub">Points delivered per sprint (Done issues only). Sprint 4&ndash;5 peak. Red bars = zero or near-zero delivery &mdash; flag for retrospective.</div>
      <div class="ch260"><canvas id="velocityChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Resource Workload &mdash; Estimated Hours per Engineer</div>
      <div class="card-sub">Red = over-allocation risk (&gt;400 hrs). Use Sprint filter to see per-sprint load. Frank Osei and Emma Wilson carry heaviest load.</div>
      <div class="ch260"><canvas id="workloadChart"></canvas></div>
    </div>
  </div>

  <div class="sec">Status Distribution &middot; Priority Breakdown</div>
  <div class="grid2">
    <div class="card">
      <div class="card-title">Issues by Status</div>
      <div class="card-sub">Distribution across workflow stages for the current filter selection.</div>
      <div class="ch260"><canvas id="statusChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Issues by Priority</div>
      <div class="card-sub">Priority spread of filtered issues. Highest + High items need immediate resourcing attention.</div>
      <div class="ch260"><canvas id="priorityChart"></canvas></div>
    </div>
  </div>

  <div class="sec">Cumulative Flow &middot; Sprint-by-Sprint Status Distribution</div>
  <div class="card mb">
    <div class="card-title">Issues by Status per Sprint (Stacked)</div>
    <div class="card-sub">Growing Blocked and In Review bands reveal downstream congestion &mdash; the core process engineering visibility insight. Filter by Epic or Project to see how individual workstreams flow.</div>
    <div class="ch220"><canvas id="flowChart"></canvas></div>
  </div>

  <div class="sec">Cycle Time &middot; Epic Breakdown</div>
  <div class="grid2">
    <div class="card">
      <div class="card-title">Average Cycle Time by Issue Type (days)</div>
      <div class="card-sub">Time from creation to resolution, Done issues only. Sub-tasks take longest at 11.3d &mdash; worth investigating parent-task dependencies.</div>
      <div class="ch260"><canvas id="cycleChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Issue Volume by Epic</div>
      <div class="card-sub">Issues per epic in filtered view. Click an Epic pill above to isolate one workstream across all charts simultaneously.</div>
      <div class="ch260"><canvas id="epicChart"></canvas></div>
    </div>
  </div>

  <div class="sec">Team Performance &middot; Done vs Blocked</div>
  <div class="card mb">
    <div class="card-title">Done vs Blocked per Team</div>
    <div class="card-sub">A Blocked count exceeding Done is a process health warning. Product leads on completion (14). Data Engineering and Operations need intervention.</div>
    <div class="ch220"><canvas id="teamChart"></canvas></div>
  </div>

  <div class="sec">Summary Stats</div>
  <div class="stat-blocks">
    <div class="stat-block"><div class="sb-val" id="sb-sp" style="color:var(--blue2);">109</div><div class="sb-lbl">Story Points Delivered</div><div class="sb-sub">Done issues only</div></div>
    <div class="stat-block"><div class="sb-val" id="sb-blocked" style="color:var(--amber);">40</div><div class="sb-lbl">Issues Blocked</div><div class="sb-sub">Needs intervention</div></div>
    <div class="stat-block"><div class="sb-val" id="sb-est" style="color:var(--green);">3,366</div><div class="sb-lbl">Hours Estimated</div><div class="sb-sub">Filtered issues</div></div>
    <div class="stat-block"><div class="sb-val" id="sb-comp" style="color:var(--cyan2);">14.5%</div><div class="sb-lbl">Completion Rate</div><div class="sb-sub">Done / Total</div></div>
  </div>

  <div class="sec">Tableau Build Guide</div>
  <div class="t-guide">
    <div class="tg-item"><div class="tg-icon">&#128202;</div><div class="tg-name">Velocity Bar</div><div class="tg-how">Bar. Sprint on columns, SUM(Story Points) rows. Filter Status=Done. Average reference line.</div></div>
    <div class="tg-item"><div class="tg-icon">&#127754;</div><div class="tg-name">Cumulative Flow</div><div class="tg-how">Area chart. Sprint columns, CNT(Issues) rows. Colour by Status. Stack marks. Sort workflow order.</div></div>
    <div class="tg-item"><div class="tg-icon">&#128100;</div><div class="tg-name">Workload Heat</div><div class="tg-how">Highlight table. Assignee rows, Sprint cols. SUM(Estimate hrs) colour. Overload threshold.</div></div>
    <div class="tg-item"><div class="tg-icon">&#9203;</div><div class="tg-name">Cycle Time</div><div class="tg-how">Box plot. Issue Type columns, Cycle Time rows. Filter Status=Done. Distribution spread.</div></div>
    <div class="tg-item"><div class="tg-icon">&#128308;</div><div class="tg-name">Blocked Tracker</div><div class="tg-how">Bar or heatmap. Filter Status=Blocked. By Team + Priority. Red above threshold.</div></div>
  </div>
</div>

<div class="footer">Jira Process Engineering Dashboard &middot; Mock data for portfolio demonstration &middot; visualizepro.com.au &middot; 2026</div>

<script>
const RAW_DATA=REPLACE_DATA;

const filters={project:'',type:'',epic:'',sprint:''};
const SPRINTS=['Sprint 1','Sprint 2','Sprint 3','Sprint 4','Sprint 5','Sprint 6'];
const STATUSES=['To Do','In Progress','In Review','Blocked','Done'];
const STATUS_COLORS=['rgba(148,163,184,0.75)','rgba(38,132,255,0.85)','rgba(0,199,230,0.85)','rgba(245,158,11,0.90)','rgba(34,197,94,0.85)'];
const PRIORITY_ORDER=['Highest','High','Medium','Low','Lowest'];
const PRIORITY_COLORS=['rgba(239,68,68,0.85)','rgba(245,158,11,0.80)','rgba(38,132,255,0.75)','rgba(0,199,230,0.65)','rgba(148,163,184,0.55)'];
const TYPES=['Story','Bug','Epic','Task','Sub-task'];
const TYPE_COLORS=['rgba(34,197,94,0.80)','rgba(239,68,68,0.80)','rgba(168,85,247,0.80)','rgba(38,132,255,0.80)','rgba(0,199,230,0.80)'];
const EPICS=['API v2 Migration','Ops Automation','Platform Stability','Reporting Suite','Auth Overhaul','Customer Data Pipeline'];
const TEAMS=['Product','Data Engineering','Operations','Platform'];
const GRID='rgba(38,132,255,0.09)';

function getFiltered(){
  return RAW_DATA.filter(r=>
    (!filters.project||r.project===filters.project)&&
    (!filters.type||r.type===filters.type)&&
    (!filters.epic||r.epic===filters.epic)&&
    (!filters.sprint||r.sprint===filters.sprint));
}

function computeStats(d){
  const byStatus={},byPriority={},byType={},byAssignee={},byTeam={},byEpic={},bySprint={};
  SPRINTS.forEach(s=>{bySprint[s]={};STATUSES.forEach(st=>bySprint[s][st]=0);});
  STATUSES.forEach(s=>byStatus[s]=0);
  const ctByType={};
  let ctSum=0,ctCount=0;
  d.forEach(r=>{
    byStatus[r.status]=(byStatus[r.status]||0)+1;
    byPriority[r.priority]=(byPriority[r.priority]||0)+1;
    byType[r.type]=(byType[r.type]||0)+1;
    byEpic[r.epic]=(byEpic[r.epic]||0)+1;
    if(!byAssignee[r.assignee])byAssignee[r.assignee]={sp:0,est:0,count:0};
    byAssignee[r.assignee].sp+=r.sp;byAssignee[r.assignee].est+=r.est;byAssignee[r.assignee].count++;
    if(!byTeam[r.team])byTeam[r.team]={done:0,blocked:0};
    if(r.status==='Done')byTeam[r.team].done++;
    if(r.status==='Blocked')byTeam[r.team].blocked++;
    if(bySprint[r.sprint])bySprint[r.sprint][r.status]=(bySprint[r.sprint][r.status]||0)+1;
    if(r.status==='Done'&&r.cycle>0){ctSum+=r.cycle;ctCount++;if(!ctByType[r.type])ctByType[r.type]={sum:0,n:0};ctByType[r.type].sum+=r.cycle;ctByType[r.type].n++;}
  });
  const velocity={};SPRINTS.forEach(s=>velocity[s]=0);
  d.filter(r=>r.status==='Done').forEach(r=>{if(velocity[r.sprint]!==undefined)velocity[r.sprint]+=r.sp;});
  const spDone=d.filter(r=>r.status==='Done').reduce((a,r)=>a+r.sp,0);
  const totalEst=d.reduce((a,r)=>a+r.est,0);
  return{byStatus,byPriority,byType,byEpic,byAssignee,byTeam,bySprint,velocity,
    total:d.length,doneCount:byStatus['Done']||0,blockedCount:byStatus['Blocked']||0,
    totalEst,spDone,avgCT:ctCount>0?ctSum/ctCount:0,ctByType};
}

function updateKPIs(s){
  document.getElementById('kpi-total').textContent=s.total;
  document.getElementById('kpi-total-note').textContent='Filtered: '+s.total+' issues';
  document.getElementById('kpi-done').textContent=s.doneCount;
  document.getElementById('kpi-done-note').textContent=s.total>0?(s.doneCount/s.total*100).toFixed(1)+'% completion':'-';
  document.getElementById('kpi-blocked').textContent=s.blockedCount;
  document.getElementById('kpi-blocked-note').textContent=s.total>0?(s.blockedCount/s.total*100).toFixed(1)+'% of filtered':'-';
  document.getElementById('kpi-sp').textContent=s.spDone;
  document.getElementById('kpi-ct').textContent=s.avgCT>0?s.avgCT.toFixed(1)+'d':'-';
  document.getElementById('sb-sp').textContent=s.spDone;
  document.getElementById('sb-blocked').textContent=s.blockedCount;
  document.getElementById('sb-est').textContent=s.totalEst.toLocaleString();
  document.getElementById('sb-comp').textContent=s.total>0?(s.doneCount/s.total*100).toFixed(1)+'%':'-';
}

const STORIES={
  default:{icon:'&#128218;',title:'Portfolio Overview &mdash; All Projects &middot; All Sprints',
    text:'<strong>200 issues</strong> across 4 projects (INFRA, CRM, DATA, OPS) and 6 epics over 6 sprints. Completion rate is <strong>14.5%</strong> with <strong>40 blocked issues</strong> exceeding the 29 done &mdash; a key process risk. Click any filter above to drill in.'},
  project:{
    INFRA:{icon:'&#128421;&#65039;',title:'Project: INFRA &mdash; Infrastructure Team',text:'INFRA covers core platform infrastructure. Cross with Epic filter to see which epics carry most risk. Filter by Bug to identify infrastructure defects driving cycle time up.'},
    CRM:{icon:'&#128101;',title:'Project: CRM &mdash; Customer Relationship Management',text:'CRM spans customer-facing features and integrations. CRM dependencies on external teams often cause workflow stalls. Combine with Epic filter to isolate highest-risk workstreams.'},
    DATA:{icon:'&#128202;',title:'Project: DATA &mdash; Data Engineering',text:'<strong>Data Engineering carries a disproportionate Blocked load.</strong> Data pipelines are dependency-heavy &mdash; upstream teams not delivering data contracts causes downstream blocked issues. Recommend a dependency review session.'},
    OPS:{icon:'&#9881;&#65039;',title:'Project: OPS &mdash; Operations',text:'OPS has the largest In Review pool, suggesting <strong>approval bottlenecks</strong>. Operational changes often require sign-off from multiple stakeholders, inflating review time and overall cycle time.'}
  },
  type:{
    Epic:{icon:'&#9889;',title:'Issue Type: Epics &mdash; Strategic Workstreams',text:'Epics are the highest-level planning unit in Jira, grouping related stories and tasks. Average cycle time for epics is <strong>9.4 days</strong>. Click an Epic pill in the filter to isolate individual workstreams across all charts.'},
    Story:{icon:'&#128214;',title:'Issue Type: Stories &mdash; User Value Delivery',text:'42 stories with the <strong>fastest cycle time at 6.5 days</strong> &mdash; well-scoped and efficiently delivered. Check the workload chart to confirm story assignments are balanced. Stories are where actual user value is shipped.'},
    Task:{icon:'&#9989;',title:'Issue Type: Tasks &mdash; Technical Work Items',text:'39 technical tasks averaging <strong>10.8 days cycle time</strong>. Tasks often sit in In Review longer than stories because they require peer review. High task count in a sprint can signal under-estimation.'},
    'Sub-task':{icon:'&#128279;',title:'Issue Type: Sub-tasks &mdash; Granular Work Breakdown',text:'Sub-tasks show the <strong>longest cycle time at 11.3 days</strong> &mdash; surprising for the smallest unit of work. This often signals sub-tasks blocked by parent task dependencies, or being created but not actively tracked to completion.'},
    Bug:{icon:'&#128027;',title:'Issue Type: Bugs &mdash; Defect Analysis',text:'<strong>40 bugs &mdash; nearly equal to Story count (42).</strong> This ratio is a warning signal: the team is spending as much time fixing as building. Average bug cycle time is 9.6 days. Cross-filter with Project to identify the most defect-prone codebase area.'}
  },
  epic:{
    'API v2 Migration':{icon:'&#128268;',title:'Epic: API v2 Migration &mdash; Largest Workstream (43 issues)',text:'The <strong>largest epic at 43 issues</strong>. API migrations carry high coordination risk &mdash; multiple teams depend on the same endpoints. High Blocked count expected. Filter by Team to identify which team is the bottleneck on this migration.'},
    'Ops Automation':{icon:'&#129302;',title:'Epic: Ops Automation &mdash; Efficiency Initiative (34 issues)',text:'34 issues targeting operational automation. Automation epics often start well then stall when integration complexity surfaces. Check the cumulative flow chart for a growing Blocked band across sprints.'},
    'Platform Stability':{icon:'&#127963;&#65039;',title:'Epic: Platform Stability &mdash; Foundation Work (34 issues)',text:'34 issues focused on reliability. Stability work is often deprioritised in favour of features, leading to issues sitting in To Do. High story point concentration here suggests this epic needs dedicated sprint capacity allocation.'},
    'Reporting Suite':{icon:'&#128200;',title:'Epic: Reporting Suite &mdash; Data Visibility (30 issues)',text:'30 issues delivering dashboards and reports. Reporting work is often <strong>blocked on data availability</strong> from the DATA project. Cross-filter with Project=DATA to reveal the dependency chain between these workstreams.'},
    'Auth Overhaul':{icon:'&#128274;',title:'Epic: Auth Overhaul &mdash; Security Initiative (29 issues)',text:'Smallest epic at 29 issues &mdash; but security work carries <strong>disproportionate risk</strong>. Auth issues require thorough In Review cycles. Any Blocked auth issues should be treated as highest priority regardless of sprint plan.'},
    'Customer Data Pipeline':{icon:'&#128257;',title:'Epic: Customer Data Pipeline &mdash; Core Integration (30 issues)',text:'30 issues connecting customer data across systems. Pipeline epics are dependency-heavy &mdash; a blocked issue early in the pipeline <strong>cascades downstream</strong>. Filter by Sprint to track pipeline progress sprint-by-sprint.'}
  },
  sprint:{
    'Sprint 1':{icon:'&#127937;',title:'Sprint 1 &mdash; Project Kickoff',text:'Delivered <strong>5 story points</strong> &mdash; low velocity typical of a kickoff sprint where setup and backlog grooming dominate. <strong>7 issues already Blocked by Sprint 1</strong> is an early warning &mdash; these dependency issues compounded in later sprints.'},
    'Sprint 2':{icon:'&#9888;&#65039;',title:'Sprint 2 &mdash; Zero Velocity Sprint',text:'<strong>Zero story points delivered.</strong> A critical warning signal indicating planning gaps, sprint overcommitment, or unresolved blockers cascading from Sprint 1. A retrospective should have identified root cause &mdash; did it?'},
    'Sprint 3':{icon:'&#128200;',title:'Sprint 3 &mdash; Recovery Sprint',text:'Recovered to <strong>13 story points</strong> after the Sprint 2 stall. Blockers partially resolved. In Progress issues highest here (10), showing the team actively working through backlog debt accumulated in Sprint 2.'},
    'Sprint 4':{icon:'&#127942;',title:'Sprint 4 &mdash; Peak Performance Sprint',text:'<strong>Peak velocity at 41 story points.</strong> The team reached full stride &mdash; low Blocked count, high throughput. This sprint sets the benchmark for team capacity. Analyse what conditions enabled this performance for process replication.'},
    'Sprint 5':{icon:'&#9889;',title:'Sprint 5 &mdash; Sustained High Performance',text:'Sustained near-peak at <strong>42 story points</strong> &mdash; the team\'s best. However, 7 new Blocked issues emerged, suggesting new dependencies as the project scales toward completion. Monitor carefully.'},
    'Sprint 6':{icon:'&#128197;',title:'Sprint 6 &mdash; End-of-Project Slowdown',text:'Velocity dropped to <strong>8 story points</strong> despite high In Review (11) and In Progress (8) counts. Classic end-of-project pattern: work is nearly done but stuck in review and sign-off queues. Recommend a dedicated review sprint.'}
  }
};

function updateStory(){
  let s=STORIES.default;
  if(filters.sprint&&STORIES.sprint[filters.sprint])s=STORIES.sprint[filters.sprint];
  else if(filters.epic&&STORIES.epic[filters.epic])s=STORIES.epic[filters.epic];
  else if(filters.type&&STORIES.type[filters.type])s=STORIES.type[filters.type];
  else if(filters.project&&STORIES.project[filters.project])s=STORIES.project[filters.project];
  document.getElementById('story-icon').innerHTML=s.icon;
  document.getElementById('story-title').innerHTML=s.title;
  document.getElementById('story-text').innerHTML=s.text;
}

Chart.defaults.color='#5e82b0';
Chart.defaults.font.family="'Inter',system-ui,sans-serif";
Chart.defaults.font.size=11;
Chart.defaults.plugins.legend.labels.boxWidth=10;
Chart.defaults.plugins.legend.labels.padding=12;

const velChart=new Chart(document.getElementById('velocityChart'),{type:'bar',
  data:{labels:SPRINTS,datasets:[{label:'Story Points Done',data:[5,0,13,41,42,8],
    backgroundColor:SPRINTS.map((_,i)=>i===1?'rgba(239,68,68,0.60)':'rgba(38,132,255,0.80)'),
    borderRadius:6,borderSkipped:false}]},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.parsed.y+' story points'}}},
    scales:{y:{beginAtZero:true,grid:{color:GRID},ticks:{color:'#5e82b0'},title:{display:true,text:'Story Points',color:'#5e82b0',font:{size:10}}},x:{grid:{display:false},ticks:{color:'#7aafdd'}}}}});

const wlChart=new Chart(document.getElementById('workloadChart'),{type:'bar',
  data:{labels:['Frank Osei','Emma Wilson','James Mwangi','Hiro Tanaka','Grace Liu','David Park','Isabelle Dupont','Carla Ramos','Alice Chen','Bob Nkosi'],
    datasets:[{label:'Est. Hours',data:[499,498,413,400,282,272,268,255,244,235],
      backgroundColor:[499,498,413,400,282,272,268,255,244,235].map(v=>v>=400?'rgba(239,68,68,0.80)':v>=300?'rgba(245,158,11,0.75)':'rgba(38,132,255,0.70)'),
      borderRadius:4,borderSkipped:false}]},
  options:{indexAxis:'y',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.parsed.x+' hrs estimated'}}},
    scales:{x:{grid:{color:GRID},ticks:{color:'#5e82b0'},title:{display:true,text:'Hours',color:'#5e82b0',font:{size:10}}},y:{grid:{display:false},ticks:{color:'#7aafdd',font:{size:10}}}}}});

const stChart=new Chart(document.getElementById('statusChart'),{type:'doughnut',
  data:{labels:STATUSES,datasets:[{data:[44,35,52,40,29],backgroundColor:STATUS_COLORS,borderColor:'rgba(6,25,51,0.5)',borderWidth:2,hoverOffset:8}]},
  options:{cutout:'60%',plugins:{legend:{position:'right',labels:{color:'#7aafdd',font:{size:10},boxWidth:9}},tooltip:{callbacks:{label:c=>c.label+': '+c.parsed+' issues'}}}}});

const prChart=new Chart(document.getElementById('priorityChart'),{type:'doughnut',
  data:{labels:PRIORITY_ORDER,datasets:[{data:[8,40,91,44,17],backgroundColor:PRIORITY_COLORS,borderColor:'rgba(6,25,51,0.5)',borderWidth:2,hoverOffset:8}]},
  options:{cutout:'60%',plugins:{legend:{position:'right',labels:{color:'#7aafdd',font:{size:10},boxWidth:9}},tooltip:{callbacks:{label:c=>c.label+': '+c.parsed+' issues'}}}}});

const FLOW_BASE={'To Do':[6,6,5,6,12,9],'In Progress':[5,5,10,4,3,8],'In Review':[11,8,6,5,11,11],'Blocked':[7,6,8,6,7,6],'Done':[4,3,3,6,7,6]};
const flowChart=new Chart(document.getElementById('flowChart'),{type:'bar',
  data:{labels:SPRINTS,datasets:STATUSES.map((st,i)=>({label:st,data:FLOW_BASE[st],backgroundColor:STATUS_COLORS[i],borderRadius:0,borderSkipped:false}))},
  options:{plugins:{legend:{position:'top',labels:{color:'#7aafdd'}},tooltip:{mode:'index',intersect:false}},
    scales:{x:{stacked:true,grid:{display:false},ticks:{color:'#7aafdd'}},y:{stacked:true,grid:{color:GRID},ticks:{color:'#5e82b0'},title:{display:true,text:'Issue Count',color:'#5e82b0',font:{size:10}}}}}});

const cyChart=new Chart(document.getElementById('cycleChart'),{type:'bar',
  data:{labels:TYPES,datasets:[{label:'Avg Cycle Time',data:[6.5,9.6,9.4,10.8,11.3],backgroundColor:TYPE_COLORS,borderRadius:6,borderSkipped:false}]},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.parsed.y+' days avg cycle time'}}},
    scales:{y:{beginAtZero:true,grid:{color:GRID},ticks:{color:'#5e82b0'},title:{display:true,text:'Days',color:'#5e82b0',font:{size:10}}},x:{grid:{display:false},ticks:{color:'#7aafdd'}}}}});

const epChart=new Chart(document.getElementById('epicChart'),{type:'bar',
  data:{labels:EPICS,datasets:[{label:'Issues',data:[43,34,34,30,30,29],backgroundColor:['rgba(38,132,255,0.88)','rgba(0,199,230,0.78)','rgba(0,199,230,0.65)','rgba(38,132,255,0.60)','rgba(38,132,255,0.50)','rgba(38,132,255,0.42)'],borderRadius:4,borderSkipped:false}]},
  options:{indexAxis:'y',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.parsed.x+' issues'}}},
    scales:{x:{grid:{color:GRID},ticks:{color:'#5e82b0'}},y:{grid:{display:false},ticks:{color:'#7aafdd',font:{size:10}}}}}});

const tmChart=new Chart(document.getElementById('teamChart'),{type:'bar',
  data:{labels:TEAMS,datasets:[
    {label:'Done',data:[14,5,6,4],backgroundColor:'rgba(34,197,94,0.80)',borderRadius:4,borderSkipped:false},
    {label:'Blocked',data:[11,11,10,8],backgroundColor:'rgba(245,158,11,0.80)',borderRadius:4,borderSkipped:false}]},
  options:{plugins:{legend:{position:'top',labels:{color:'#7aafdd'}},tooltip:{mode:'index',intersect:false}},
    scales:{x:{grid:{display:false},ticks:{color:'#7aafdd'}},y:{grid:{color:GRID},ticks:{color:'#5e82b0'},title:{display:true,text:'Issues',color:'#5e82b0',font:{size:10}}}}}});

function applyFilters(){
  const d=getFiltered(), s=computeStats(d);
  updateKPIs(s); updateStory();
  stChart.data.datasets[0].data=STATUSES.map(st=>s.byStatus[st]||0); stChart.update();
  prChart.data.datasets[0].data=PRIORITY_ORDER.map(p=>s.byPriority[p]||0); prChart.update();
  velChart.data.datasets[0].data=SPRINTS.map(sp=>s.velocity[sp]||0);
  velChart.data.datasets[0].backgroundColor=SPRINTS.map(sp=>(s.velocity[sp]||0)===0&&d.length>0?'rgba(239,68,68,0.55)':'rgba(38,132,255,0.80)');
  velChart.update();
  const assignees=['Frank Osei','Emma Wilson','James Mwangi','Hiro Tanaka','Grace Liu','David Park','Isabelle Dupont','Carla Ramos','Alice Chen','Bob Nkosi'];
  const wlData=assignees.map(a=>(s.byAssignee[a]||{est:0}).est);
  wlChart.data.datasets[0].data=wlData;
  wlChart.data.datasets[0].backgroundColor=wlData.map(v=>v>=400?'rgba(239,68,68,0.80)':v>=300?'rgba(245,158,11,0.75)':'rgba(38,132,255,0.70)');
  wlChart.update();
  const anyFilter=filters.project||filters.type||filters.epic||filters.sprint;
  STATUSES.forEach((st,i)=>{flowChart.data.datasets[i].data=SPRINTS.map(sp=>anyFilter?s.bySprint[sp]?s.bySprint[sp][st]||0:0:FLOW_BASE[st][SPRINTS.indexOf(sp)]);});
  flowChart.update();
  const filtTypes=filters.type?[filters.type]:TYPES;
  cyChart.data.labels=filtTypes;
  cyChart.data.datasets[0].data=filtTypes.map(t=>s.ctByType[t]?+(s.ctByType[t].sum/s.ctByType[t].n).toFixed(1):0);
  cyChart.data.datasets[0].backgroundColor=filtTypes.map(t=>TYPE_COLORS[TYPES.indexOf(t)]||'rgba(38,132,255,0.75)');
  cyChart.update();
  const filtEpics=filters.epic?[filters.epic]:EPICS;
  epChart.data.labels=filtEpics;
  epChart.data.datasets[0].data=filtEpics.map(e=>s.byEpic[e]||0);
  epChart.update();
  tmChart.data.datasets[0].data=TEAMS.map(t=>(s.byTeam[t]||{done:0}).done);
  tmChart.data.datasets[1].data=TEAMS.map(t=>(s.byTeam[t]||{blocked:0}).blocked);
  tmChart.update();
  kanban.init(d);
}

document.querySelectorAll('.pill').forEach(pill=>{
  pill.addEventListener('click',()=>{
    const g=pill.dataset.group,v=pill.dataset.val;
    document.querySelectorAll('.pill[data-group="'+g+'"]').forEach(p=>p.classList.remove('active'));
    pill.classList.add('active'); filters[g]=v; applyFilters();
  });
});

(function(){
  const base=3366,rate=0.002,start=Date.now();
  function tick(){const v=base+(Date.now()-start)/1000*rate;document.getElementById('liveCounter').textContent=v.toLocaleString('en-AU',{minimumFractionDigits:1,maximumFractionDigits:1});}
  tick();setInterval(tick,300);
})();

/* ── Kanban – driven by actual issue data, with hover tooltip ── */
const kanban=(function(){
  const canvas=document.getElementById('kanbanCanvas'),dpr=window.devicePixelRatio||1;
  const tip=document.getElementById('kanban-tip');
  const ktKey=document.getElementById('kt-key');
  const ktSum=document.getElementById('kt-summary');
  const ktSp=document.getElementById('kt-sp');
  const ktMeta=document.getElementById('kt-meta');
  function resize(){const w=canvas.parentElement.clientWidth,h=Math.round(w*0.30);canvas.width=w*dpr;canvas.height=h*dpr;canvas.style.height=h+'px';}
  resize();window.addEventListener('resize',()=>{resize();rebuild();});
  const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);
  const CC=['rgba(148,163,184,0.85)','rgba(38,132,255,0.90)','rgba(0,199,230,0.90)','rgba(245,158,11,0.95)','rgba(34,197,94,0.90)'];
  const PRIORITY_COLORS_TIP={Highest:'#ef4444',High:'#f59e0b',Medium:'#2684ff',Low:'#00c7e6',Lowest:'#94a3b8'};
  let CNT=[44,35,52,40,29];
  let blocks=[];
  let currentData=RAW_DATA;
  const W=()=>canvas.width/dpr,H=()=>canvas.height/dpr,cW=()=>W()/5,cX=i=>cW()*i;

  function rebuild(){
    blocks=[];
    const grouped={};
    STATUSES.forEach(st=>{grouped[st]=[];});
    currentData.forEach(r=>{if(grouped[r.status])grouped[r.status].push(r);});
    const bw=Math.max(7,cW()*0.055),pad=Math.max(2,bw*0.45);
    STATUSES.forEach((st,ci)=>{
      const list=grouped[st];
      CNT[ci]=list.length;
      const count=list.length;
      if(!count)return;
      const maxR=Math.max(1,Math.floor((cW()-pad*2)/(bw+pad)));
      const cx=cX(ci)+cW()/2;
      list.forEach((issue,i)=>{
        const row=Math.floor(i/maxR),col=i%maxR;
        const sx=cx-((Math.min(count,maxR)*(bw+pad))/2)+col*(bw+pad)+bw/2;
        const sy=46+row*(bw+pad)+Math.random()*2;
        blocks.push({x:sx-bw/2,y:sy,ty:sy,col:ci,color:CC[ci],w:bw,h:bw,
          blocked:ci===3,wobble:Math.random()*Math.PI*2,wS:0.008+Math.random()*0.01,
          pulse:0,pDir:1,issue});
      });
    });
    updateLegend();
  }

  function updateLegend(){
    document.getElementById('kl-todo').textContent='To Do ('+CNT[0]+')';
    document.getElementById('kl-inprog').textContent='In Progress ('+CNT[1]+')';
    document.getElementById('kl-inrev').textContent='In Review ('+CNT[2]+')';
    document.getElementById('kl-blocked').innerHTML='Blocked ('+CNT[3]+')'+(CNT[3]>CNT[4]?' ← bottleneck':'');
    document.getElementById('kl-done').textContent='Done ('+CNT[4]+')';
  }

  let frame=0,hoveredBlock=null;
  function draw(){
    const w=W(),h=H();ctx.clearRect(0,0,w,h);
    ctx.fillStyle='rgba(4,18,42,0.94)';ctx.fillRect(0,0,w,h);
    const t=frame*0.016;frame++;
    const cols=['To Do','In Progress','In Review','Blocked','Done'];
    cols.forEach((name,i)=>{
      const x=cX(i),cw=cW();
      ctx.fillStyle=i===3?'rgba(245,158,11,0.04)':'rgba(38,132,255,0.03)';ctx.fillRect(x+2,0,cw-4,h);
      if(i>0){ctx.strokeStyle='rgba(38,132,255,0.10)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();}
      ctx.font="600 10px 'Space Grotesk',sans-serif";ctx.textAlign='center';
      ctx.fillStyle=i===3?'rgba(245,158,11,0.75)':'rgba(38,132,255,0.65)';ctx.fillText(name.toUpperCase(),x+cw/2,14);
      ctx.font="700 11px 'Space Grotesk',sans-serif";ctx.fillStyle=CC[i].replace(/[\d.]+\)$/,'0.9)');ctx.fillText(CNT[i],x+cw/2,27);
    });
    blocks.forEach(p=>{
      const isHovered=(p===hoveredBlock);
      if(p.blocked){p.pulse+=0.04*p.pDir;if(p.pulse>1||p.pulse<0)p.pDir*=-1;ctx.fillStyle='rgba(245,158,11,'+(0.55+p.pulse*0.4)+')';}
      else{p.y=p.ty+Math.sin(t*p.wS*60+p.wobble)*1.2;ctx.fillStyle=isHovered?'#fff':p.color;}
      if(isHovered){ctx.shadowColor='rgba(255,255,255,0.6)';ctx.shadowBlur=8;}
      const r=3,bx=p.x,by=p.y,bw=p.w,bh=p.h;
      ctx.beginPath();ctx.moveTo(bx+r,by);ctx.lineTo(bx+bw-r,by);ctx.quadraticCurveTo(bx+bw,by,bx+bw,by+r);
      ctx.lineTo(bx+bw,by+bh-r);ctx.quadraticCurveTo(bx+bw,by+bh,bx+bw-r,by+bh);
      ctx.lineTo(bx+r,by+bh);ctx.quadraticCurveTo(bx,by+bh,bx,by+bh-r);
      ctx.lineTo(bx,by+r);ctx.quadraticCurveTo(bx,by,bx+r,by);ctx.closePath();ctx.fill();
      if(isHovered){ctx.shadowBlur=0;}
      /* show issue key text on block if wide enough */
      if(p.w>=22&&p.issue){
        ctx.font="500 "+(Math.min(p.w*0.38,9))+"px 'Inter',sans-serif";
        ctx.textAlign='center';ctx.fillStyle='rgba(255,255,255,0.75)';
        ctx.fillText(p.issue.key,p.x+p.w/2,p.y+p.h/2+3);
      }
    });
    requestAnimationFrame(draw);
  }

  /* Mouse tracking for tooltip */
  canvas.addEventListener('mousemove',e=>{
    const rect=canvas.getBoundingClientRect();
    const mx=e.clientX-rect.left,my=e.clientY-rect.top;
    let found=null;
    for(let i=blocks.length-1;i>=0;i--){
      const b=blocks[i];
      if(mx>=b.x&&mx<=b.x+b.w&&my>=b.y&&my<=b.y+b.h){found=b;break;}
    }
    hoveredBlock=found;
    if(found&&found.issue){
      const iss=found.issue;
      ktKey.textContent=iss.key+' · '+iss.type;
      ktSum.textContent=iss.summary;
      ktSp.innerHTML=iss.sp>0
        ?'<span style="color:#4d9fff">&#9733; '+iss.sp+' story point'+(iss.sp!==1?'s':'')+'</span>'
        :'<span style="color:#5e82b0">No story points ('+iss.est+'h estimated)</span>';
      ktMeta.innerHTML='Priority: <span style="color:'+(PRIORITY_COLORS_TIP[iss.priority]||'#aaa')+'">'+iss.priority+'</span> &middot; Assignee: '+iss.assignee+' &middot; Epic: '+iss.epic;
      tip.style.display='block';
      const tx=Math.min(e.clientX+14,window.innerWidth-320);
      const ty=Math.min(e.clientY+14,window.innerHeight-140);
      tip.style.left=tx+'px';tip.style.top=ty+'px';
      canvas.style.cursor='pointer';
    } else {
      tip.style.display='none';canvas.style.cursor='default';hoveredBlock=null;
    }
  });
  canvas.addEventListener('mouseleave',()=>{tip.style.display='none';hoveredBlock=null;});

  rebuild();draw();
  return{
    init(data){currentData=data||RAW_DATA;resize();rebuild();}
  };
})();
</script>
</body>
</html>"""

html = html.replace('REPLACE_DATA', js_data)

with open(r'C:\Users\madel\Tableau-Reports\jira_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done:', len(html), 'chars')
