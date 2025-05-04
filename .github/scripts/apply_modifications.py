import os
import sys
import re
import fileinput

# --- 文件路径 ---
repo_root = os.environ.get('GITHUB_WORKSPACE', '.')  # 默认为当前目录
registration_file = os.path.join(repo_root, "system/athena/registration.py")
launch_script = os.path.join(repo_root, "launch_openpilot.sh")

# ✅ 新增文件路径
process_config = os.path.join(repo_root, "system/manager/process_config.py")
longitudinal_planner = os.path.join(repo_root, "selfdrive/controls/lib/longitudinal_planner.py")
long_mpc = os.path.join(repo_root, "selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py")

# --- Registration.py 修改 ---
def modify_registration(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        line_out = line
        if 'imei1' in line and '=' in line:
            line_out = "    imei1='865420071781912'\n"
            modified = True
        elif 'imei2' in line and '=' in line:
            line_out = "    imei2='865420071781904'\n"
            modified = True
        elif 'set_offroad_alert("Offroad_UnofficialHardware"' in line and not line.lstrip().startswith("#"):
            line_out = "#" + line
            modified = True
        print(line_out, end='')
    return modified

# --- launch_openpilot.sh 插入环境变量 ---
def modify_launch_script(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    lines_to_insert = [
        "export API_HOST=https://api.konik.ai\n",
        "export ATHENA_HOST=wss://athena.konik.ai\n",
        "export MAPS_HOST=https://api.konik.ai/maps\n"
    ]

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.readlines()

    if any(line in content for line in lines_to_insert):
        print("Environment lines already present, skipping insertion.")
        return True

    new_content = content[:1] + lines_to_insert + content[1:]
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    return True

# ✅ 修改 process_config.py 中注释两个进程
def modify_process_config(filename):
    print(f"Modifying {filename}...")
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if 'PythonProcess("dmonitoringmodeld"' in line and not line.lstrip().startswith("#"):
            print("#" + line, end='')
            modified = True
        elif 'PythonProcess("dmonitoringd"' in line and not line.lstrip().startswith("#"):
            print("#" + line, end='')
            modified = True
        else:
            print(line, end='')
    return modified

# ✅ 修改 longitudinal_planner.py 中 A_CRUISE_MAX_VALS 和 _A_TOTAL_MAX_V
def modify_longitudinal_planner(filename):
    print(f"Modifying {filename}...")
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if 'A_CRUISE_MAX_VALS' in line:
            print("A_CRUISE_MAX_VALS = [1.4, 0.8, 0.4, 0.2]\n", end='')
            modified = True
        elif '_A_TOTAL_MAX_V' in line:
            print("_A_TOTAL_MAX_V = [1.3, 2.7]\n", end='')
            modified = True
        else:
            print(line, end='')
    return modified

# ✅ 修改 long_mpc.py 中 STOP_DISTANCE
def modify_long_mpc(filename):
    print(f"Modifying {filename}...")
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if 'STOP_DISTANCE' in line and '=' in line:
            print("STOP_DISTANCE = 4.5\n", end='')
            modified = True
        else:
            print(line, end='')
    return modified

# --- 主入口 ---
print("Running all modifications...")

results = [
    modify_registration(registration_file),
    modify_launch_script(launch_script),
    modify_process_config(process_config),
    modify_longitudinal_planner(longitudinal_planner),
    modify_long_mpc(long_mpc)
]

if all(results):
    print("✅ All modifications applied successfully.")
    sys.exit(0)
else:
    print("❌ Some modifications failed.", file=sys.stderr)
    sys.exit(1)
