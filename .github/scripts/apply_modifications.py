# 文件名: .github/scripts/apply_modifications.py
# 功能: 修改多个关键配置文件

import sys
import re
import os
import fileinput
from pathlib import Path

# --- Configuration ---
repo_root = os.environ.get('GITHUB_WORKSPACE', '.')
registration_file = os.path.join(repo_root, "system/athena/registration.py")
launch_script = os.path.join(repo_root, "launch_openpilot.sh")
process_config_file = os.path.join(repo_root, "system/manager/process_config.py")
planner_file = os.path.join(repo_root, "selfdrive/controls/lib/longitudinal_planner.py")
mpc_file = os.path.join(repo_root, "selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py")

# 修改 registration.py
def modify_registration(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    modified = False
    try:
        for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
            original_line = line.rstrip()
            processed = False

            if original_line == "    imei1: str | None = None":
                print("    imei1='865420071781912'")
                modified = True
                processed = True
            elif original_line == "    imei2: str | None = None":
                print("    imei2='865420071781904'")
                modified = True
                processed = True
            elif re.match(r"^\s*set_offroad_alert\(\"Offroad_UnofficialHardware\",", line.lstrip()):
                print("#" + line.rstrip())
                modified = True
                processed = True

            if not processed:
                print(line, end='')

        return True
    except Exception as e:
        print(f"Error modifying {filename}: {e}", file=sys.stderr)
        return False

# 修改 launch_openpilot.sh
def modify_launch_script(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    insert_lines = [
        "export API_HOST=https://api.konik.ai\n",
        "export ATHENA_HOST=wss://athena.konik.ai\n",
        "export MAPS_HOST=https://api.konik.ai/maps\n"
    ]

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            print(f"{filename} is empty.", file=sys.stderr)
            return False

        new_content = lines[:1] + insert_lines + lines[1:]
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(new_content)

        return True
    except Exception as e:
        print(f"Error modifying {filename}: {e}", file=sys.stderr)
        return False

# 修改 process_config.py：注释 dmonitoringmodeld 和 dmonitoringd
def modify_process_config():
    print(f"Modifying {process_config_file}...")
    path = Path(process_config_file)
    if not path.exists():
        print(f"File not found: {process_config_file}", file=sys.stderr)
        return False

    try:
        text = path.read_text()
        text = re.sub(
            r'^(\s*)PythonProcess\("dmonitoringmodeld", "selfdrive\.modeld\.dmonitoringmodeld", driverview, enabled=\(WEBCAM or not PC\)\)',
            r'\1#PythonProcess("dmonitoringmodeld", "selfdrive.modeld.dmonitoringmodeld", driverview, enabled=(WEBCAM or not PC))',
            text, flags=re.MULTILINE
        )
        text = re.sub(
            r'^(\s*)PythonProcess\("dmonitoringd", "selfdrive\.monitoring\.dmonitoringd", driverview, enabled=\(WEBCAM or not PC\)\)',
            r'\1#PythonProcess("dmonitoringd", "selfdrive.monitoring.dmonitoringd", driverview, enabled=(WEBCAM or not PC))',
            text, flags=re.MULTILINE
        )
        path.write_text(text)
        return True
    except Exception as e:
        print(f"Error modifying {process_config_file}: {e}", file=sys.stderr)
        return False

# 修改 longitudinal_planner.py
def modify_longitudinal_planner():
    print(f"Modifying {planner_file}...")
    path = Path(planner_file)
    if not path.exists():
        print(f"File not found: {planner_file}", file=sys.stderr)
        return False

    try:
        text = path.read_text()
        text = re.sub(r'A_CRUISE_MAX_VALS\s*=\s*\[.*?\]', 'A_CRUISE_MAX_VALS = [1.4, 0.8, 0.4, 0.2]', text)
        text = re.sub(r'_A_TOTAL_MAX_V\s*=\s*\[.*?\]', '_A_TOTAL_MAX_V = [1.3, 2.7]', text)
        path.write_text(text)
        return True
    except Exception as e:
        print(f"Error modifying {planner_file}: {e}", file=sys.stderr)
        return False

# 修改 long_mpc.py
def modify_long_mpc():
    print(f"Modifying {mpc_file}...")
    path = Path(mpc_file)
    if not path.exists():
        print(f"File not found: {mpc_file}", file=sys.stderr)
        return False

    try:
        text = path.read_text()
        text = re.sub(r'STOP_DISTANCE\s*=\s*6\.0', 'STOP_DISTANCE = 4.5', text)
        path.write_text(text)
        return True
    except Exception as e:
        print(f"Error modifying {mpc_file}: {e}", file=sys.stderr)
        return False

# --- Run all modifications ---
print("Running all modification steps...")

results = [
    modify_registration(registration_file),
    modify_launch_script(launch_script),
    modify_process_config(),
    modify_longitudinal_planner(),
    modify_long_mpc()
]

if all(results):
    print("✅ All modifications applied successfully.")
    sys.exit(0)
else:
    print("❌ One or more modifications failed.", file=sys.stderr)
    sys.exit(1)
