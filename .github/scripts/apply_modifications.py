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
updated_py = os.path.join(repo_root, "system/updated/updated.py")
pandad_cc = os.path.join(repo_root, "selfdrive/pandad/pandad.cc")
# 🆕 新增：hardware.h 的文件路径
hardware_h = os.path.join(repo_root, "system/hardware/tici/hardware.h")


# --- Registration.py 修改 ---
def modify_registration(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        line_out = line
        indent = line[:len(line) - len(line.lstrip())]
        stripped_line = line.strip()
        if stripped_line == "imei1: str | None = None":
            line_out = f"{indent}imei1='865420071781912'\n"
            modified = True
        elif stripped_line == "imei2: str | None = None":
            line_out = f"{indent}imei2='865420071781904'\n"
            modified = True
        elif 'set_offroad_alert("Offroad_UnofficialHardware"' in line and not line.lstrip().startswith("#"):
            line_out = f"{indent}#{line.lstrip()}"
            if not line_out.endswith('\n') and line.endswith('\n'):
                line_out += '\n'
            modified = True
        print(line_out, end='')
    if modified:
        print(f"  Modifications applied to {os.path.basename(filename)}.")
    return True

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
    if all(line_to_check in content for line_to_check in lines_to_insert):
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
        if ('PythonProcess("dmonitoringmodeld"' in line or 'PythonProcess("dmonitoringd"' in line) and not content_part.startswith("#"):
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
        if target_str in line and not line.lstrip().startswith(("#", "pass#")):
            indent = line[:len(line) - len(line.lstrip())]
            line = f"{indent}pass#{line.lstrip()}"
            modified = True
        print(line, end='')
    if modified:
        print(f"  '{target_str}' commented with pass#.")
    return True

# 🆕 修改 selfdrived.py
def modify_selfdrived_py(filename):
    # This function is complex, so read/write is safer
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Simple idempotency check
        content = "".join(lines)
        if "ignore += ['driverCameraState', 'managerState', 'driverMonitoringState']" in content and \
           "pass # self.events.add(EventName.commIssue)" in content:
            print("  selfdrived.py already appears to be modified.")
            return True

        new_lines = []
        modified = False
        i = 0
        while i < len(lines):
            line = lines[i]
            # Process lines here... this logic can be complex.
            # For simplicity, let's use a simpler but effective string replacement method
            # This is less robust to formatting changes but sufficient for this script's purpose.
            pass
        
        # A simpler, more direct approach using string replacement
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        replacements = {
            # Add to ignore list
            "ignore = self.sensor_packets + self.gps_packets + ['alertDebug']":
                "ignore = self.sensor_packets + self.gps_packets + ['alertDebug']\n"
                "    ignore += ['driverCameraState', 'managerState', 'driverMonitoringState']",
            # Pass on various events
            "self.events.add(EventName.commIssue)": "pass # self.events.add(EventName.commIssue)",
            "self.events.add(EventName.commIssueAvgFreq)": "pass # self.events.add(EventName.commIssueAvgFreq)",
            "self.events.add(EventName.cameraMalfunction)": "pass # self.events.add(EventName.cameraMalfunction)",
            'cloudlog.event("process_not_running", not_running=not_running, error=True)': 'pass#cloudlog.event("process_not_running", not_running=not_running, error=True)',
            'self.events.add(EventName.processNotRunning)': 'pass#self.events.add(EventName.processNotRunning)',
            'self.events.add(EventName.sensorDataInvalid)': 'pass#self.events.add(EventName.sensorDataInvalid)',
            'self.events.add(EventName.noGps)': 'pass#self.events.add(EventName.noGps)',
        }
        
        original_content = content
        for find, replace in replacements.items():
            content = content.replace(find, replace)
        
        if content != original_content:
            modified = True
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print("  selfdrived.py modified to ignore DM/camera/comm issues and other specified alerts.")
        else:
            print("  selfdrived.py already in desired state.")
        return True

    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False


# 🆕 修改 updated.py
def modify_updated_py(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_block = """elif failed_count > 0:
      if dt_uptime_onroad > HOURS_NO_CONNECTIVITY_MAX and dt_route_count > ROUTES_NO_CONNECTIVITY_MAX:
        set_offroad_alert("Offroad_ConnectivityNeeded", True)
      elif dt_uptime_onroad > HOURS_NO_CONNECTIVITY_PROMPT and dt_route_count > ROUTES_NO_CONNECTIVITY_PROMPT:
        remaining = max(HOURS_NO_CONNECTIVITY_MAX - dt_uptime_onroad, 1)
        set_offroad_alert("Offroad_ConnectivityNeededPrompt", True, extra_text=f"{remaining} hour{'' if remaining == 1 else 's'}.")"""

        replacement_block = """# 关闭长时间不联网限制
    # elif failed_count > 0:
    #   if dt_uptime_onroad > HOURS_NO_CONNECTIVITY_MAX and dt_route_count > ROUTES_NO_CONNECTIVITY_MAX:
    #     set_offroad_alert("Offroad_ConnectivityNeeded", True)
    #   elif dt_uptime_onroad > HOURS_NO_CONNECTIVITY_PROMPT and dt_route_count > ROUTES_NO_CONNECTIVITY_PROMPT:
    #     remaining = max(HOURS_NO_CONNECTIVITY_MAX - dt_uptime_onroad, 1)
    #     set_offroad_alert("Offroad_ConnectivityNeededPrompt", True, extra_text=f"{remaining} hour{'' if remaining == 1 else 's'}.")"""
        
        if replacement_block in content:
            print("  Connectivity limit block already commented.")
            return True
        
        new_content = content.replace(original_block, replacement_block)

        if new_content != content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("  Connectivity limit block commented out.")
        return True

    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False

# 🆕 修改 pandad.cc
def modify_pandad_cc(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if line.strip() == '#define MAX_IR_PANDA_VAL 50':
            print("#define MAX_IR_PANDA_VAL 0\n", end='')
            modified = True
        else:
            print(line, end='')
    if modified:
        print("  MAX_IR_PANDA_VAL changed to 0.")
    return True

# 🆕 新增：修改 hardware.h 以禁用 IR Power
def modify_hardware_h(filename):
    print(f"Modifying {filename}...")
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

            # 修改点 1: 插入 (void)percent;
            if "static void set_ir_power(int percent) {" in line:
                new_lines.append(line)
                # 幂等性检查: 如果下一行不是我们要添加的内容，则添加它
                if not (i + 1 < len(lines) and "(void)percent;" in lines[i+1]):
                    indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())] if i + 1 < len(lines) else "    "
                    new_lines.append(f"{indent}(void)percent; // 忽略传入参数，避免编译器警告\n")
                    modified = True
                i += 1
                continue

            # 修改点 2: 替换 brightness 设置逻辑
            elif "int value = util::map_val" in line:
                # 幂等性检查: 如果前一行是我们的注释，说明已经修改过了
                if not (len(new_lines) > 0 and "// 强制设为 0" in new_lines[-1]):
                    indent = line[:len(line) - len(line.lstrip())]
                    new_lines.append(f"{indent}// 强制设为 0\n")
                    new_lines.append(f'{indent}std::ofstream("/sys/class/leds/led:switch_2/brightness") << 0 << "\\n";\n')
                    new_lines.append(f'{indent}std::ofstream("/sys/class/leds/led:torch_2/brightness") << 0 << "\\n";\n')
                    new_lines.append(f'{indent}std::ofstream("/sys/class/leds/led:switch_2/brightness") << 0 << "\\n";\n')
                    modified = True
                
                # 跳过原始的4行代码
                i += 4
                continue

            # 默认情况: 直接添加原始行
            new_lines.append(line)
            i += 1
        
        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("  IR power logic in hardware.h has been modified.")
        else:
            print("  hardware.h already in the desired state.")
        
        return True

    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False

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
    modify_updated_py(updated_py),
    modify_pandad_cc(pandad_cc),
    modify_hardware_h(hardware_h), # 🆕 调用新增的函数
]

if all(results):
    print("✅ All modifications applied successfully or files were already in the desired state.")
    sys.exit(0)
else:
    print("❌ Some modifications may have failed or were not applicable.", file=sys.stderr)
    failed_mods = [func_name for func_name, res_val in zip(
        ["registration", "launch_script", "process_config", "long_mpc", "pandad_py", 
         "hardwared_py", "selfdrived", "updated", "pandad_cc", "hardware_h"], # 🆕 增加到错误报告列表
        results
    ) if not res_val]
    if failed_mods:
        print(f"  Potentially failed/unapplied modifications for: {', '.join(failed_mods)}", file=sys.stderr)
    sys.exit(1)
