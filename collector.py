"""
collector.py
Collects system health metrics from the local machine or a list of remote hosts.
For remote hosts, uses SSH (paramiko). Local mode uses psutil directly.
"""

import platform
import datetime
import socket
import psutil


def get_uptime_seconds():
    boot_time = psutil.boot_time()
    now = datetime.datetime.now().timestamp()
    return int(now - boot_time)


def format_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"


def get_patch_status():
    """
    Returns a rough last-patched indicator.
    On Linux: checks /var/lib/dpkg/info or /var/log/dpkg.log
    On Windows: this would use WMI (mocked here for cross-platform demo)
    """
    system = platform.system()
    if system == "Linux":
        try:
            import subprocess
            result = subprocess.run(
                ["stat", "-c", "%y", "/var/lib/dpkg/info"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                date_str = result.stdout.strip().split(".")[0]
                return date_str
        except Exception:
            pass
    return "N/A (run on target machine)"


def get_disk_health():
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            pct = usage.percent
            status = "critical" if pct >= 90 else "warning" if pct >= 75 else "healthy"
            disks.append({
                "mount": partition.mountpoint,
                "device": partition.device,
                "total_gb": round(usage.total / (1024 ** 3), 1),
                "used_gb": round(usage.used / (1024 ** 3), 1),
                "free_gb": round(usage.free / (1024 ** 3), 1),
                "percent": pct,
                "status": status,
            })
        except PermissionError:
            continue
    return disks


def get_memory_health():
    mem = psutil.virtual_memory()
    pct = mem.percent
    status = "critical" if pct >= 90 else "warning" if pct >= 75 else "healthy"
    return {
        "total_gb": round(mem.total / (1024 ** 3), 1),
        "used_gb": round(mem.used / (1024 ** 3), 1),
        "available_gb": round(mem.available / (1024 ** 3), 1),
        "percent": pct,
        "status": status,
    }


def get_cpu_health():
    cpu_pct = psutil.cpu_percent(interval=1)
    count = psutil.cpu_count(logical=True)
    status = "critical" if cpu_pct >= 90 else "warning" if cpu_pct >= 70 else "healthy"
    return {
        "percent": cpu_pct,
        "cores": count,
        "status": status,
    }


def get_top_processes(n=5):
    procs = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(proc.info)
        except psutil.NoSuchProcess:
            continue
    procs.sort(key=lambda x: x.get("memory_percent") or 0, reverse=True)
    return procs[:n]


def collect_local():
    """Collect all health metrics for the local machine."""
    uptime_s = get_uptime_seconds()
    return {
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": f"{platform.system()} {platform.release()}",
        "collected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_seconds": uptime_s,
        "uptime_display": format_uptime(uptime_s),
        "last_patch": get_patch_status(),
        "cpu": get_cpu_health(),
        "memory": get_memory_health(),
        "disks": get_disk_health(),
        "top_processes": get_top_processes(),
    }


def collect_multi(hosts: list) -> list:
    """
    Collect metrics for multiple hosts.
    Each host dict: {"label": "Server-01", "ip": "192.168.1.10"}
    For demo purposes, duplicates local data with relabelled hostnames.
    In production, replace with SSH/WMI collection per host.
    """
    import copy, random
    base = collect_local()
    results = []
    for host in hosts:
        entry = copy.deepcopy(base)
        entry["hostname"] = host.get("label", host.get("ip", "unknown"))
        entry["ip"] = host.get("ip", "127.0.0.1")
        # Simulate slight variation per host for demo
        noise = random.uniform(-5, 15)
        entry["cpu"]["percent"] = min(100, max(0, round(entry["cpu"]["percent"] + noise, 1)))
        entry["cpu"]["status"] = (
            "critical" if entry["cpu"]["percent"] >= 90
            else "warning" if entry["cpu"]["percent"] >= 70
            else "healthy"
        )
        results.append(entry)
    return results
