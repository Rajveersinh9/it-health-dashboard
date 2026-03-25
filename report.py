"""
report.py
Generates a clean, self-contained HTML health dashboard from collected metrics.
No external dependencies — pure HTML/CSS/JS embedded in one file.
"""

import json
from pathlib import Path


STATUS_COLOR = {
    "healthy":  ("#EAF3DE", "#27500A", "#639922"),
    "warning":  ("#FAEEDA", "#633806", "#EF9F27"),
    "critical": ("#FCEBEB", "#791F1F", "#E24B4A"),
}


def status_badge(status: str) -> str:
    bg, text, _ = STATUS_COLOR.get(status, STATUS_COLOR["healthy"])
    label = status.upper()
    return (
        f'<span style="background:{bg};color:{text};font-size:11px;font-weight:600;'
        f'padding:2px 8px;border-radius:20px;">{label}</span>'
    )


def gauge_bar(pct: float, status: str) -> str:
    _, _, bar_color = STATUS_COLOR.get(status, STATUS_COLOR["healthy"])
    return (
        f'<div style="background:#E8E8E8;border-radius:4px;height:8px;overflow:hidden;margin-top:4px;">'
        f'<div style="width:{min(pct,100)}%;height:8px;background:{bar_color};border-radius:4px;'
        f'transition:width 0.4s;"></div></div>'
    )


def render_machine_card(data: dict) -> str:
    cpu = data["cpu"]
    mem = data["memory"]
    disks = data["disks"]

    overall = "healthy"
    for check in [cpu["status"], mem["status"]] + [d["status"] for d in disks]:
        if check == "critical":
            overall = "critical"
            break
        if check == "warning":
            overall = "warning"

    bg, text_color, _ = STATUS_COLOR.get(overall, STATUS_COLOR["healthy"])

    disk_rows = ""
    for d in disks:
        disk_rows += f"""
        <tr>
          <td style="padding:4px 8px;font-size:12px;color:#444;">{d['mount']}</td>
          <td style="padding:4px 8px;font-size:12px;text-align:right;">{d['used_gb']} / {d['total_gb']} GB</td>
          <td style="padding:4px 8px;min-width:120px;">
            {gauge_bar(d['percent'], d['status'])}
            <span style="font-size:11px;color:#666;">{d['percent']}%</span>
          </td>
          <td style="padding:4px 8px;">{status_badge(d['status'])}</td>
        </tr>"""

    proc_rows = ""
    for p in data.get("top_processes", []):
        proc_rows += (
            f'<tr><td style="padding:3px 8px;font-size:11px;color:#444;">{p.get("name","?")}</td>'
            f'<td style="padding:3px 8px;font-size:11px;text-align:right;">{round(p.get("memory_percent",0),1)}%</td>'
            f'<td style="padding:3px 8px;font-size:11px;text-align:right;">{round(p.get("cpu_percent",0),1)}%</td></tr>'
        )

    return f"""
    <div style="background:#fff;border:0.5px solid #ddd;border-radius:12px;margin-bottom:20px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06);">

      <!-- Card header -->
      <div style="background:{bg};padding:14px 18px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:16px;font-weight:600;color:{text_color};">{data['hostname']}</div>
          <div style="font-size:12px;color:{text_color};opacity:0.8;">{data['ip']} &nbsp;|&nbsp; {data['os']}</div>
        </div>
        <div style="text-align:right;">
          {status_badge(overall)}
          <div style="font-size:11px;color:{text_color};margin-top:4px;">Collected: {data['collected_at']}</div>
        </div>
      </div>

      <div style="padding:16px 18px;">

        <!-- Uptime + patch -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
          <div style="background:#F8F8F8;border-radius:8px;padding:10px 14px;">
            <div style="font-size:11px;color:#888;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;">Uptime</div>
            <div style="font-size:18px;font-weight:600;color:#222;margin-top:2px;">{data['uptime_display']}</div>
          </div>
          <div style="background:#F8F8F8;border-radius:8px;padding:10px 14px;">
            <div style="font-size:11px;color:#888;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;">Last Patched</div>
            <div style="font-size:13px;font-weight:500;color:#222;margin-top:4px;">{data['last_patch']}</div>
          </div>
        </div>

        <!-- CPU + Memory -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
          <div style="background:#F8F8F8;border-radius:8px;padding:10px 14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:11px;color:#888;font-weight:500;text-transform:uppercase;">CPU</span>
              {status_badge(cpu['status'])}
            </div>
            <div style="font-size:22px;font-weight:600;color:#222;margin:4px 0 2px;">{cpu['percent']}%</div>
            {gauge_bar(cpu['percent'], cpu['status'])}
            <div style="font-size:11px;color:#888;margin-top:4px;">{cpu['cores']} logical cores</div>
          </div>
          <div style="background:#F8F8F8;border-radius:8px;padding:10px 14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:11px;color:#888;font-weight:500;text-transform:uppercase;">Memory</span>
              {status_badge(mem['status'])}
            </div>
            <div style="font-size:22px;font-weight:600;color:#222;margin:4px 0 2px;">{mem['percent']}%</div>
            {gauge_bar(mem['percent'], mem['status'])}
            <div style="font-size:11px;color:#888;margin-top:4px;">{mem['used_gb']} GB used of {mem['total_gb']} GB</div>
          </div>
        </div>

        <!-- Disk -->
        <div style="margin-bottom:16px;">
          <div style="font-size:11px;color:#888;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Disk Usage</div>
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid #eee;">
                <th style="padding:4px 8px;font-size:11px;color:#888;text-align:left;font-weight:500;">Mount</th>
                <th style="padding:4px 8px;font-size:11px;color:#888;text-align:right;font-weight:500;">Used</th>
                <th style="padding:4px 8px;font-size:11px;color:#888;font-weight:500;">Usage</th>
                <th style="padding:4px 8px;font-size:11px;color:#888;font-weight:500;">Status</th>
              </tr>
            </thead>
            <tbody>{disk_rows}</tbody>
          </table>
        </div>

        <!-- Top processes -->
        <div>
          <div style="font-size:11px;color:#888;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Top Processes (by memory)</div>
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid #eee;">
                <th style="padding:3px 8px;font-size:11px;color:#888;text-align:left;font-weight:500;">Process</th>
                <th style="padding:3px 8px;font-size:11px;color:#888;text-align:right;font-weight:500;">Mem %</th>
                <th style="padding:3px 8px;font-size:11px;color:#888;text-align:right;font-weight:500;">CPU %</th>
              </tr>
            </thead>
            <tbody>{proc_rows}</tbody>
          </table>
        </div>

      </div>
    </div>"""


def generate_html(machines: list, output_path: str = "output/dashboard.html"):
    cards = "".join(render_machine_card(m) for m in machines)
    total = len(machines)
    critical = sum(1 for m in machines if any(
        x == "critical" for x in [m["cpu"]["status"], m["memory"]["status"]] + [d["status"] for d in m["disks"]]
    ))
    warnings = sum(1 for m in machines if any(
        x == "warning" for x in [m["cpu"]["status"], m["memory"]["status"]] + [d["status"] for d in m["disks"]]
    ) and m not in [])
    healthy = total - critical - warnings

    summary_cards = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:28px;">
      <div style="background:#EAF3DE;border-radius:8px;padding:14px;">
        <div style="font-size:11px;color:#27500A;font-weight:500;text-transform:uppercase;">Healthy</div>
        <div style="font-size:32px;font-weight:700;color:#27500A;">{healthy}</div>
      </div>
      <div style="background:#FAEEDA;border-radius:8px;padding:14px;">
        <div style="font-size:11px;color:#633806;font-weight:500;text-transform:uppercase;">Warning</div>
        <div style="font-size:32px;font-weight:700;color:#633806;">{warnings}</div>
      </div>
      <div style="background:#FCEBEB;border-radius:8px;padding:14px;">
        <div style="font-size:11px;color:#791F1F;font-weight:500;text-transform:uppercase;">Critical</div>
        <div style="font-size:32px;font-weight:700;color:#791F1F;">{critical}</div>
      </div>
    </div>"""

    generated_at = machines[0]["collected_at"] if machines else "N/A"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IT Health Dashboard</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #F4F4F4; color: #222; padding: 24px; }}
    .container {{ max-width: 960px; margin: 0 auto; }}
  </style>
</head>
<body>
<div class="container">

  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:20px;">
    <div>
      <h1 style="font-size:24px;font-weight:700;color:#1A3C6E;">IT Health Dashboard</h1>
      <p style="font-size:13px;color:#888;margin-top:2px;">Generated: {generated_at} &nbsp;|&nbsp; {total} machine(s) monitored</p>
    </div>
    <div style="font-size:12px;color:#888;">Auto-generated by it-health-dashboard</div>
  </div>

  {summary_cards}
  {cards}

</div>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
    print(f"Dashboard saved to: {output_path}")
    return output_path
