"""Connect to OBS WebSocket, ensure a scene + window capture source exist, open a windowed projector."""

import base64
import io
import json
import os
import struct
import sys
import time

GEOMETRY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geometry.json")


def load_geometry() -> tuple[int, int, int, int]:
    """Return (x, y, w, h). Falls back to defaults if geometry.json is absent or malformed."""
    default = (100, 100, 960, 720)
    try:
        with open(GEOMETRY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (int(data["x"]), int(data["y"]), int(data["w"]), int(data["h"]))
    except (FileNotFoundError, KeyError, ValueError, OSError):
        return default

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def build_qt_geometry(x: int, y: int, w: int, h: int) -> str:
    """Build a Qt QWidget.saveGeometry() QByteArray, base64-encoded.

    Format (Qt 6, version 3):
      magic u32, major u16, minor u16,
      frame QRect, normal QRect, screen qi32,
      maximized u8, fullscreen u8,
      restored screen width qi32, cursor QPoint, screenName QString.
    Qt tolerates a malformed tail by returning false from restoreGeometry(),
    but the projector window still opens at default size when that happens.
    """
    magic = 0x1D9D0CB
    buf = struct.pack(">I", magic)
    buf += struct.pack(">HH", 3, 0)  # majorVersion=3, minorVersion=0
    # frame geometry
    buf += struct.pack(">iiii", x, y, x + w, y + h)
    # normal geometry
    buf += struct.pack(">iiii", x, y, x + w, y + h)
    # screen number
    buf += struct.pack(">i", 0)
    # maximized / fullscreen flags
    buf += struct.pack(">BB", 0, 0)
    # restored screen width
    buf += struct.pack(">i", 0)
    # cursor position (QPoint: two qi32)
    buf += struct.pack(">ii", 0, 0)
    # screen name: QString = qi32 length in bytes (-1 = null)
    buf += struct.pack(">i", -1)
    return base64.b64encode(buf).decode()

try:
    import obsws_python as obs
except ImportError:
    print("obsws-python is not installed. Run setup.ps1 first.", file=sys.stderr)
    sys.exit(1)

HOST = "127.0.0.1"
PORT = 4455
PASSWORD = "pixelagents"
SCENE_NAME = "PixelAgents"
SOURCE_NAME = "VSCode Window"


def main() -> int:
    client = obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=10)

    scenes = client.get_scene_list().scenes
    scene_names = [s["sceneName"] for s in scenes]

    if SCENE_NAME not in scene_names:
        print(f"Creating scene '{SCENE_NAME}'...")
        client.create_scene(SCENE_NAME)

    client.set_current_program_scene(SCENE_NAME)

    inputs = client.get_input_list().inputs
    input_names = [i["inputName"] for i in inputs]

    if SOURCE_NAME not in input_names:
        print(f"Creating window capture source '{SOURCE_NAME}'...")
        client.create_input(
            SCENE_NAME,
            SOURCE_NAME,
            "window_capture",
            {"method": 2, "priority": 2, "cursor": True, "client_area": True},
            True,
        )
        time.sleep(1)

    try:
        props = client.get_input_properties_list_property_items(
            SOURCE_NAME, "window"
        )
        items = getattr(props, "property_items", [])
        print(f"[debug] found {len(items)} windows")
        vscode_val = None
        for item in items:
            val = item.get("itemValue", "") if isinstance(item, dict) else getattr(item, "itemValue", "")
            name = item.get("itemName", "") if isinstance(item, dict) else getattr(item, "itemName", "")
            print(f"  - {name} | {val}")
            if ("Visual Studio Code" in val or "Code.exe" in val
                    or "Visual Studio Code" in name or "Code.exe" in name):
                vscode_val = val
                break
        if vscode_val:
            client.set_input_settings(SOURCE_NAME, {"window": vscode_val}, True)
            print(f"Targeted VS Code window: {vscode_val}")
        else:
            print("VS Code window not found. Start VS Code (with Pixel Agents panel) and re-run.")
    except Exception as exc:
        print(f"Could not auto-target VS Code window: {exc}")
        print("Open OBS and set the window manually in the source properties.")

    print("Opening windowed projector...")
    gx, gy, gw, gh = load_geometry()
    print(f"[geometry] x={gx} y={gy} w={gw} h={gh}")
    geometry = build_qt_geometry(x=gx, y=gy, w=gw, h=gh)
    try:
        client.open_source_projector(SCENE_NAME, -1, geometry)
    except Exception as exc:
        print(f"Windowed projector failed ({exc}); falling back to monitor 0 fullscreen.")
        client.open_source_projector(SCENE_NAME, 0, None)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
