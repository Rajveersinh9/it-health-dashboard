"""
main.py
IT Health Dashboard — entry point.

Usage:
  # Local machine only
  python main.py

  # Multiple hosts (demo mode — simulates remote hosts)
  python main.py --hosts hosts.json

  # Custom output path
  python main.py --output reports/my_report.html
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from collector import collect_local, collect_multi
from report import generate_html


def load_hosts(path: str) -> list:
    with open(path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="IT Health Dashboard — collect system metrics and generate HTML report."
    )
    parser.add_argument(
        "--hosts", type=str, default=None,
        help="Path to a JSON file listing remote hosts. If omitted, runs on local machine only."
    )
    parser.add_argument(
        "--output", type=str, default="output/dashboard.html",
        help="Output path for the HTML report (default: output/dashboard.html)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Also save raw metrics as JSON alongside the HTML report."
    )
    args = parser.parse_args()

    print("Collecting metrics...")

    if args.hosts:
        hosts = load_hosts(args.hosts)
        print(f"  Running in multi-host mode ({len(hosts)} hosts defined)")
        machines = collect_multi(hosts)
    else:
        print("  Running in local mode")
        machines = [collect_local()]

    print(f"  Collected data for {len(machines)} machine(s)")

    if args.json:
        json_path = args.output.replace(".html", ".json")
        with open(json_path, "w") as f:
            json.dump(machines, f, indent=2)
        print(f"  JSON saved to: {json_path}")

    output = generate_html(machines, args.output)
    print(f"\nDone. Open in browser: {output}")


if __name__ == "__main__":
    main()
