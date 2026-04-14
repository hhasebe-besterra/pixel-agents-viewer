"""Connect to OBS WebSocket, ensure a scene + window capture source exist, open a windowed projector."""

import sys
import time

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
        window_list = client.get_input_properties_list_property_items(
            None, "window", input_kind="window_capture"
        ).property_items if False else None

        input_settings = {
            "method": 2,
            "priority": 2,
            "cursor": True,
            "client_area": True,
        }

        try:
            props = client.get_input_properties_list_property_items(
                SOURCE_NAME, "window"
            )
            items = getattr(props, "property_items", [])
        except Exception:
            items = []

        vscode_window = None
        for item in items:
            val = item.get("itemValue", "")
            if "Visual Studio Code" in val or "Code.exe" in val:
                vscode_window = val
                break

        if vscode_window:
            input_settings["window"] = vscode_window

        client.create_input(
            scene_name=SCENE_NAME,
            input_name=SOURCE_NAME,
            input_kind="window_capture",
            input_settings=input_settings,
            scene_item_enabled=True,
        )

        time.sleep(1)

        try:
            props = client.get_input_properties_list_property_items(
                SOURCE_NAME, "window"
            )
            items = getattr(props, "property_items", [])
            for item in items:
                val = item.get("itemValue", "")
                if "Visual Studio Code" in val:
                    client.set_input_settings(
                        SOURCE_NAME, {"window": val}, overlay=True
                    )
                    print(f"Targeted VS Code window: {val}")
                    break
        except Exception as exc:
            print(f"Could not auto-target VS Code window: {exc}")
            print("Open OBS and set the window manually in the source properties.")

    print("Opening windowed projector...")
    try:
        client.open_source_projector(
            source_name=SCENE_NAME, monitor_index=-1, projector_geometry=""
        )
    except TypeError:
        client.open_source_projector(SCENE_NAME, -1, "")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
