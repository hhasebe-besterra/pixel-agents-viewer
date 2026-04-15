"""Find the OBS windowed projector for scene PixelAgents and persist its rect to geometry.json."""

import ctypes
import io
import json
import os
import subprocess
import sys
from ctypes import wintypes

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCENE_NAME = "PixelAgents"
GEOMETRY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geometry.json")

u = ctypes.windll.user32


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def find_obs_pid() -> int | None:
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", "(Get-Process obs64).Id"],
            text=True,
        ).strip()
        return int(out.splitlines()[0])
    except (subprocess.CalledProcessError, ValueError):
        return None


def find_projector_rect(obs_pid: int) -> dict | None:
    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    hits: list[int] = []

    def cb(hwnd, _lparam):
        n = u.GetWindowTextLengthW(hwnd)
        if n <= 0:
            return True
        buf = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(hwnd, buf, n + 1)
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value != obs_pid:
            return True
        title = buf.value
        # Match the windowed projector across locales: it always contains the scene name
        # and is *not* the OBS main window (which includes the profile/scene collection label).
        if SCENE_NAME in title and "OBS" not in title.split(" - ")[0]:
            hits.append(hwnd)
        return True

    u.EnumWindows(EnumWindowsProc(cb), 0)
    if not hits:
        return None

    rect = RECT()
    if not u.GetWindowRect(hits[0], ctypes.byref(rect)):
        return None
    return {
        "x": rect.left,
        "y": rect.top,
        "w": rect.right - rect.left,
        "h": rect.bottom - rect.top,
    }


def main() -> int:
    pid = find_obs_pid()
    if pid is None:
        print("obs64 not running; geometry not updated.")
        return 0
    rect = find_projector_rect(pid)
    if rect is None:
        print("Projector window not found; geometry not updated.")
        return 0
    with open(GEOMETRY_FILE, "w", encoding="utf-8") as f:
        json.dump(rect, f, indent=2)
    print(f"Saved geometry: x={rect['x']} y={rect['y']} w={rect['w']} h={rect['h']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
