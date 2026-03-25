# IT Health Dashboard

A lightweight Python tool that collects real-time system health metrics and generates a clean, self-contained HTML dashboard — no server required, no external dependencies beyond `psutil`.

Built to solve a real IT operations problem: **proactive monitoring instead of reactive firefighting.**

---

## What it does

- Collects CPU usage, memory usage, disk space, system uptime, and top processes
- Classifies each metric as **Healthy / Warning / Critical** automatically
- Generates a single self-contained HTML report you can open in any browser, email to a manager, or save as a record
- Supports **multi-host mode** for monitoring multiple machines in one report (demo/simulation included)
- Optionally exports raw data as JSON for integration with other tools (Power BI, ServiceNow, etc.)

---

## Why this matters in IT operations

Most helpdesk teams respond to issues *after* users report them. This tool enables a shift to **proactive monitoring** — catching a disk at 88% before it hits 100% and causes downtime, or flagging a server with 94% memory usage before it crashes overnight.

A 5-minute scheduled run of this script (via Task Scheduler on Windows or cron on Linux) replaces manual spot-checks and gives IT teams an auditable daily health record.

---

## Quick start

```bash
# Clone the repo
git clone https://github.com/Rajveersinh9/it-health-dashboard.git
cd it-health-dashboard

# Install dependencies (only psutil required)
pip install -r requirements.txt

# Run on local machine
python main.py

# Open the report
open output/dashboard.html   # macOS
start output/dashboard.html  # Windows
```

---

## Multi-host mode (demo)

```bash
# Edit sample_data/hosts.json with your host list
python main.py --hosts sample_data/hosts.json
```

In demo mode, the tool simulates metric variation across hosts so you can see the full dashboard without needing SSH access. In a production environment, replace `collect_multi()` in `src/collector.py` with your SSH/WMI collection method.

---

## Options

| Flag | Description | Default |
|---|---|---|
| `--hosts` | Path to JSON file with host list | Local machine only |
| `--output` | Output path for HTML report | `output/dashboard.html` |
| `--json` | Also save raw metrics as JSON | Off |

---

## Sample output

```
Collecting metrics...
  Running in local mode
  Collected data for 1 machine(s)
Dashboard saved to: output/dashboard.html

Done. Open in browser: output/dashboard.html
```

The generated dashboard shows:
- Summary counts (Healthy / Warning / Critical) across all monitored machines
- Per-machine cards with visual gauge bars for CPU, memory, and each disk partition
- Uptime and last-patch indicators
- Top 5 processes by memory consumption

---

## Status thresholds

| Metric | Healthy | Warning | Critical |
|---|---|---|---|
| CPU | < 70% | 70–89% | ≥ 90% |
| Memory | < 75% | 75–89% | ≥ 90% |
| Disk | < 75% | 75–89% | ≥ 90% |

Thresholds are configurable in `src/collector.py`.

---

## Project structure

```
it-health-dashboard/
├── main.py                  # Entry point
├── requirements.txt
├── src/
│   ├── collector.py         # Metric collection logic
│   └── report.py            # HTML dashboard generator
├── sample_data/
│   └── hosts.json           # Sample multi-host config
└── output/                  # Generated reports go here
```

---

## Extending this project

This tool is intentionally minimal — here are natural next steps:

- **Add email alerting:** Send an alert when any metric hits Critical (SMTP or SendGrid)
- **Schedule it:** Windows Task Scheduler or Linux cron for daily/hourly runs
- **Push to Power BI:** Use the `--json` flag and load into a Power BI dashboard
- **SSH-based remote collection:** Replace demo simulation with `paramiko` for real remote hosts
- **ServiceNow integration:** Auto-create a ticket when a Critical threshold is detected

---

## Tech stack

- **Python 3.8+**
- **psutil** — cross-platform system metrics
- Pure HTML/CSS dashboard — no frontend framework required

---

## Author

**Rajveersinh Vaghela** — [github.com/Rajveersinh9](https://github.com/Rajveersinh9)

Built as part of a portfolio of real-world IT automation tools. See also:
- [IT Onboarding Automation (PowerShell)](https://github.com/Rajveersinh9)
- [Ticket Analytics Dashboard (ServiceNow + Power BI)](https://github.com/Rajveersinh9)
