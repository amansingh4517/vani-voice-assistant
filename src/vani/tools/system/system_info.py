"""Read-only facts about this Mac."""

import datetime
import platform
import re
import shutil

from vani.tools.core import error, human_size, run, tool


@tool
def get_battery_status() -> str:
    """Get battery percentage and whether the Mac is charging."""
    res = run(["pmset", "-g", "batt"])
    if not res.ok:
        return res.message()
    pct = re.search(r"(\d+)%", res.output)
    if not pct:
        return "No battery found. This Mac may be a desktop."
    text = res.output
    if "discharging" in text:
        state = "on battery"
    elif "charging" in text:
        state = "charging"
    else:
        state = "plugged in"
    left = re.search(r"(\d+:\d+) remaining", text)
    extra = f", {left.group(1)} remaining" if left else ""
    return f"Battery at {pct.group(1)}%, {state}{extra}."


@tool
def get_system_info() -> str:
    """Get basic info about this Mac: macOS version, chip, memory, uptime."""
    chip = run(["sysctl", "-n", "machdep.cpu.brand_string"]).output
    mem = run(["sysctl", "-n", "hw.memsize"]).output
    up = run(["uptime"]).output
    mem_gb = f"{int(mem) / 1024 ** 3:.0f} GB" if mem.isdigit() else "unknown"
    up_text = up.split("up", 1)[1].split(",  ")[0].strip(" ,") if "up" in up else up
    return f"macOS {platform.mac_ver()[0]}, chip: {chip}, memory: {mem_gb}, uptime: {up_text}."


@tool
def get_disk_usage() -> str:
    """Get free and used space on the main disk."""
    total, used, free = shutil.disk_usage("/")
    return f"{human_size(free)} free of {human_size(total)} ({used / total * 100:.0f}% used)."


@tool
def get_current_datetime() -> str:
    """Get the current date, day of the week and time."""
    return datetime.datetime.now().strftime("It is %A, %d %B %Y, %I:%M %p.")
