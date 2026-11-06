"""Wi-Fi, Bluetooth and network address."""

import shutil

from .core import error, run, tool


@tool
def set_wifi(enabled: bool) -> str:
    """Turn Wi-Fi on (true) or off (false)."""
    state = "on" if enabled else "off"
    return run(["networksetup", "-setairportpower", "en0", state]).message(f"Wi-Fi {state}.")


@tool
def set_bluetooth(enabled: bool) -> str:
    """Turn Bluetooth on (true) or off (false). Needs the free 'blueutil' tool (brew install blueutil)."""
    if not shutil.which("blueutil"):
        return error("blueutil is not installed. Install it with: brew install blueutil")
    state = "on" if enabled else "off"
    return run(["blueutil", "--power", "1" if enabled else "0"]).message(f"Bluetooth {state}.")


@tool
def get_ip_address() -> str:
    """Get this Mac's local network IP address."""
    for iface in ("en0", "en1"):
        res = run(["ipconfig", "getifaddr", iface])
        if res.ok and res.output:
            return f"Local IP address is {res.output}."
    return error("not connected to a network.")
