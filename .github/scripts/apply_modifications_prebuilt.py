import os
import sys
import re
import fileinput

# --- 文件路径 ---
repo_root = os.environ.get('GITHUB_WORKSPACE', '.')  # 默认为当前目录
registration_file = os.path.join(repo_root, "system/athena/registration.py")
launch_script = os.path.join(repo_root, "launch_openpilot.sh")
process_config = os.path.join(repo_root, "system/manager/process_config.py")
long_mpc = os.path.join(repo_root, "selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py")
pandad_py = os.path.join(repo_root, "selfdrive/pandad/pandad.py")
hardwared_py = os.path.join(repo_root, "system/hardware/hardwared.py")
selfdrived_py = os.path.join(repo_root, "selfdrive/selfdrived/selfdrived.py")
# 新增：panda/python/__init__.py 的文件路径
panda_init_py = os.path.join(repo_root, "panda/python/__init__.py")


# --- Registration.py 修改 ---
def modify_registration(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    modified_imei1 = False
    modified_imei2 = False
    modified_alert = False

    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        line_out = line
        indent = line[:len(line) - len(line.lstrip())]
        stripped_line = line.strip()

        if stripped_line == "imei1: str | None = None":
            line_out = f"{indent}imei1='865420071781912'\n"
            modified_imei1 = True
        elif stripped_line == "imei2: str | None = None":
            line_out = f"{indent}imei2='865420071781904'\n"
            modified_imei2 = True
        elif 'set_offroad_alert("Offroad_UnofficialHardware"' in line and not line.lstrip().startswith("#"):
            line_out = f"{indent}#{line.lstrip()}"
            if not line_out.endswith('\n') and line.endswith('\n'):
                line_out += '\n'
            modified_alert = True
        
        print(line_out, end='')
    
    if modified_imei1 or modified_imei2 or modified_alert:
        print(f"  IMEI1 changed: {modified_imei1}, IMEI2 changed: {modified_imei2}, Alert changed: {modified_alert}")
        return True
    
    return True # 假设即使没有修改，文件也可能已经是目标状态


# --- launch_openpilot.sh 插入环境变量 ---
def modify_launch_script(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    lines_to_insert = [
        "export API_HOST=https://api.konik.ai\n",
        "export ATHENA_HOST=wss://athena.konik.ai\n",
        "#export MAPS_HOST=https://api.konik.ai/maps\n",
        "export MAPBOX_TOKEN='pk.eyJ1IjoibXJvbmVjYyIsImEiOiJjbHhqbzlkbTYxNXUwMmtzZjdoMGtrZnVvIn0.SC7GNLtMFUGDgC2bAZcKzg'\n"
    ]

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.readlines()

    all_present = all(line_to_check in content for line_to_check in lines_to_insert)
    
    if all_present:
        print("  Environment lines already present, skipping insertion.")
        return True

    content_without_inserts = [l for l in content if l not in lines_to_insert]
    
    idx = 1 if content_without_inserts and content_without_inserts[0].startswith("#!") else 0
    
    new_content = content_without_inserts[:idx] + lines_to_insert + content_without_inserts[idx:]
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    print("  Environment lines inserted/updated.")
    return True

# ✅ 修改 process_config.py 中注释两个进程
def modify_process_config(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        indent = line[:len(line) - len(line.lstrip())]
        content_part = line.lstrip()
        
        if 'PythonProcess("dmonitoringmodeld"' in line and not content_part.startswith("#"):
            print(f"{indent}#{content_part}", end='')
            modified = True
        elif 'PythonProcess("dmonitoringd"' in line and not content_part.startswith("#"):
            print(f"{indent}#{content_part}", end='')
            modified = True
        else:
            print(line, end='')
    if modified:
        print("  dmonitoringmodeld or dmonitoringd commented.")
    return True

# ✅ 修改 long_mpc.py 中 STOP_DISTANCE
def modify_long_mpc(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if 'STOP_DISTANCE' in line and '=' in line and not line.strip().startswith("#"):
            if line.strip() != "STOP_DISTANCE = 4.5":
                indent = line[:len(line) - len(line.lstrip())]
                print(f"{indent}STOP_DISTANCE = 4.5\n", end='')
                modified = True
            else:
                print(line, end='')
        else:
            print(line, end='')
    if modified:
        print("  STOP_DISTANCE changed to 4.5.")
    return True

# 🆕 修改 pandad.py
def modify_pandad_py(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if 'if time.monotonic() < 35.:' in line and 'if time.monotonic() < 45.:' not in line:
            line = line.replace('35.', '45.')
            modified = True
        print(line, end='')
    if modified:
        print("  time.monotonic limit changed from 35 to 45.")
    return True

# 🆕 修改 hardwared.py
def modify_hardwared_py(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        target_str = 'set_offroad_alert_if_changed("Offroad_StorageMissing", True)'
        if target_str in line and not line.lstrip().startswith("#") and not line.lstrip().startswith("pass#"):
            indent = line[:len(line) - len(line.lstrip())]
            original_eol = "\n" if line.endswith("\n") else ""
            line = f"{indent}pass#{target_str}{original_eol}"
            modified = True
        print(line, end='')
    if modified:
        print(f"  '{target_str}' commented with pass#.")
    return True

# 🆕 修改 selfdrived.py 以关闭 DM 相关报错
def modify_selfdrived_py(filename):
    print(f"Modifying {filename} to close DM errors...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        modified = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            indent = line[:len(line) - len(line.lstrip())]
            stripped_line = line.strip()

            # --- 修改点 1: 增加 ignore 列表 ---
            # ignore = self.sensor_packets + self.gps_packets + ['alertDebug']
            target_line_1 = "ignore = self.sensor_packets + self.gps_packets + ['alertDebug']"
            line_to_add_1 = "ignore += ['driverCameraState', 'managerState', 'driverMonitoringState']"
            
            new_lines.append(line) # 先把当前行加进去

            if target_line_1 in stripped_line:
                # 检查下一行是否已经是我们要添加的内容，避免重复添加
                if i + 1 < len(lines) and line_to_add_1 in lines[i+1]:
                    pass # 已经存在，什么都不做
                else:
                    new_lines.append(f"{indent}{line_to_add_1}\n")
                    modified = True
            
            # --- 修改点 2: 注释 commIssue ---
            # if not self.sm.all_alive():
            elif "if not self.sm.all_alive():" in stripped_line:
                # 期望的下一行是 self.events.add(EventName.commIssue)
                if i + 1 < len(lines) and "self.events.add(EventName.commIssue)" in lines[i+1]:
                    next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                    i += 1 # 跳过原始的 self.events.add 行
                    modified = True
            
            # elif not self.sm.all_freq_ok():
            elif "elif not self.sm.all_freq_ok():" in stripped_line:
                if i + 1 < len(lines) and "self.events.add(EventName.commIssueAvgFreq)" in lines[i+1]:
                    next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                    i += 1
                    modified = True

            # else: (针对 commIssue 的 else)
            elif stripped_line == "else:" and i + 1 < len(lines) and "self.events.add(EventName.commIssue)" in lines[i+1]:
                 if i + 1 < len(lines) and "self.events.add(EventName.commIssue)" in lines[i+1]:
                    next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                    i += 1
                    modified = True

            # --- 修改点 3: 注释 cameraMalfunction ---
            # if not self.sm.all_alive(self.camera_packets):
            elif "if not self.sm.all_alive(self.camera_packets):" in stripped_line:
                 if i + 1 < len(lines) and "self.events.add(EventName.cameraMalfunction)" in lines[i+1]:
                    next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                    i += 1
                    modified = True
            
            i += 1

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("  selfdrived.py modified to ignore DM/camera/comm issues.")

        return True

    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False


# 🆕 新增：修改 panda/python/__init__.py (只修改第一次出现的位置)
def modify_panda_init_py(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    modified = False
    found_and_modified_once = False # 标志位：是否已修改第一次出现的位置
    
    # 定义要查找的行和替换后的行
    target_line_content = "if device.getVendorID() in cls.USB_VIDS and device.getProductID() in cls.USB_PIDS:"
    replacement_line_content = "    if device.getVendorID() == 0xbbaa and device.getProductID() in cls.USB_PIDS:"

    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        stripped_line = line.strip()
        
        # 只有当行匹配目标内容且尚未修改过第一次出现的位置时，才进行修改
        if stripped_line == target_line_content and not found_and_modified_once:
            # 保持原始缩进
            indent = line[:len(line) - len(line.lstrip())]
            # 打印替换后的行，并确保保留原始行末的换行符
            print(f"{indent}{replacement_line_content}\n", end='')
            modified = True
            found_and_modified_once = True # 设置标志位，表示已完成第一次修改
        else:
            # 如果不匹配目标行，或者已经修改过第一次出现的位置，则原样打印该行
            print(line, end='')

    if modified:
        print(f"  Changed first occurrence of USB_VIDS check to 0xbbaa in {filename}.")
    else:
        # 如果没有修改，表示文件可能已经处于目标状态，或者目标行从未出现
        print(f"  First occurrence of USB_VIDS check already set to 0xbbaa or target line not found in {filename}.")
    return True

# --- 主入口 ---
print("Running all modifications...")

results = [
    modify_registration(registration_file),
    modify_launch_script(launch_script),
    modify_process_config(process_config),
    modify_long_mpc(long_mpc),
    modify_pandad_py(pandad_py),
    modify_hardwared_py(hardwared_py),
    modify_selfdrived_py(selfdrived_py),
    modify_panda_init_py(panda_init_py), # 调用新增的函数
]

if all(results):
    print("✅ All modifications applied successfully or files were already in the desired state.")
    sys.exit(0)
else:
    print("❌ Some modifications may have failed or were not applicable.", file=sys.stderr)
    failed_mods = [func_name for func_name, res_val in zip(
        ["registration", "launch_script", "process_config", "long_mpc", "pandad_py", "hardwared_py", "selfdrived", "panda_init"], # 增加到错误报告列表
        results
    ) if not res_val]
    if failed_mods:
        print(f"  Potentially failed/unapplied modifications for: {', '.join(failed_mods)}", file=sys.stderr)
    sys.exit(1)
