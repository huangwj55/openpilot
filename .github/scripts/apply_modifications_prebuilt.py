import os
import sys
import fileinput

# --- 文件路径 ---
repo_root = os.environ.get('GITHUB_WORKSPACE', '.')  # 默认为当前目录
registration_file = os.path.join(repo_root, "system/athena/registration.py")
launch_script = os.path.join(repo_root, "launch_openpilot.sh")
process_config = os.path.join(repo_root, "system/manager/process_config.py")
long_mpc = os.path.join(repo_root, "selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py")
pandad_py = os.path.join(repo_root, "selfdrive/pandad/pandad.py")
pandad_cc = os.path.join(repo_root, "selfdrive/pandad/pandad.cc")
hardwared_py = os.path.join(repo_root, "system/hardware/hardwared.py")
hardware_h = os.path.join(repo_root, "system/hardware/tici/hardware.h")
selfdrived_py = os.path.join(repo_root, "selfdrive/selfdrived/selfdrived.py")
updated_py = os.path.join(repo_root, "system/updated/updated.py")
# 🆕 新增：panda __init__.py 的文件路径
panda_init_py = os.path.join(repo_root, "panda/python/__init__.py")


# --- Helper for status printing ---
def print_status(filename, modified, message_if_modified, message_if_not_modified="already in desired state"):
    if modified:
        print(f"  {message_if_modified}")
    else:
        print(f"  {os.path.basename(filename)} {message_if_not_modified}.")


# --- 修改函数 (fileinput 适用于简单的单行替换) ---

def modify_registration(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        stripped_line = line.strip()
        if stripped_line == "imei1: str | None = None":
            print(line.replace(stripped_line, "imei1='865420071781912'"), end='')
            modified = True
        elif stripped_line == "imei2: str | None = None":
            print(line.replace(stripped_line, "imei2='865420071781904'"), end='')
            modified = True
        elif 'set_offroad_alert("Offroad_UnofficialHardware"' in line and not stripped_line.startswith("#"):
            print("#" + line, end='')
            modified = True
        else:
            print(line, end='')
    print_status(filename, modified, "IMEI and/or alert modified.")
    return True

def modify_process_config(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if ('PythonProcess("dmonitoringmodeld"' in line or 'PythonProcess("dmonitoringd"' in line) and not line.strip().startswith("#"):
            print("#" + line, end='')
            modified = True
        else:
            print(line, end='')
    print_status(filename, modified, "dmonitoring processes commented.")
    return True

def modify_long_mpc(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if 'STOP_DISTANCE' in line and '=' in line and not line.strip().startswith("#"):
            if line.strip() != "STOP_DISTANCE = 4.5":
                print(line.split('=')[0] + "= 4.5\n", end='')
                modified = True
            else:
                print(line, end='')
        else:
            print(line, end='')
    print_status(filename, modified, "STOP_DISTANCE changed to 4.5.")
    return True

def modify_pandad_py(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if 'if time.monotonic() < 35.:' in line and 'if time.monotonic() < 45.:' not in line:
            print(line.replace('35.', '45.'), end='')
            modified = True
        else:
            print(line, end='')
    print_status(filename, modified, "time.monotonic limit changed from 35 to 45.")
    return True

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
    print_status(filename, modified, "MAX_IR_PANDA_VAL changed to 0.")
    return True

def modify_hardwared_py(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        target_str = 'set_offroad_alert_if_changed("Offroad_StorageMissing", True)'
        if target_str in line and not line.strip().startswith(("#", "pass#")):
            print(line.replace(target_str, "pass#" + target_str), end='')
            modified = True
        else:
            print(line, end='')
    print_status(filename, modified, "Offroad_StorageMissing alert commented with pass#.")
    return True

# 🆕 新增：修改 panda __init__.py
def modify_panda_init_py(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    modified = False
    original_part = "in cls.USB_VIDS"
    new_part = "== 0xbbaa"
    
    for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
        if "if device.getVendorID() in cls.USB_VIDS" in line:
            print(line.replace(original_part, new_part), end='')
            modified = True
        else:
            print(line, end='')
            
    print_status(filename, modified, "Panda USB VID check modified.")
    return True

# --- 修改函数 (read/write 适用于多行、复杂或上下文相关的修改) ---

def modify_launch_script(filename):
    print(f"Modifying {filename}...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        lines_to_insert = [
            "export API_HOST=https://api.konik.ai\n",
            "export ATHENA_HOST=wss://athena.konik.ai\n",
            "#export MAPS_HOST=https://api.konik.ai/maps\n",
            "export MAPBOX_TOKEN='pk.eyJ1IjoibXJvbmVjYyIsImEiOiJjbHhqbzlkbTYxNXUwMmtzZjdoMGtrZnVvIn0.SC7GNLtMFUGDgC2bAZcKzg'\n"
        ]

        if all(l in lines for l in lines_to_insert):
            print_status(filename, False, "")
            return True

        content_without_inserts = [l for l in lines if l not in lines_to_insert]
        idx = 1 if content_without_inserts and content_without_inserts[0].startswith("#!") else 0
        new_content = content_without_inserts[:idx] + lines_to_insert + content_without_inserts[idx:]

        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        
        print_status(filename, True, "Environment lines inserted/updated.")
        return True
    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False

def modify_selfdrived_py(filename):
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
            stripped_line = line.strip()

            if "ignore = self.sensor_packets + self.gps_packets + ['alertDebug']" in stripped_line:
                new_lines.append(line)
                if not (i + 1 < len(lines) and "ignore +=" in lines[i+1]):
                    indent = line[:len(line) - len(line.lstrip())]
                    new_lines.append(f"{indent}    ignore += ['driverCameraState', 'managerState', 'driverMonitoringState']\n")
                    modified = True
                i += 1
                continue

            lines_to_comment = [
                "self.events.add(EventName.commIssue)", "self.events.add(EventName.commIssueAvgFreq)",
                "self.events.add(EventName.cameraMalfunction)", 'cloudlog.event("process_not_running"',
                'self.events.add(EventName.processNotRunning)', 'self.events.add(EventName.sensorDataInvalid)',
                'self.events.add(EventName.noGps)',
            ]
            
            if any(s in stripped_line for s in lines_to_comment) and not stripped_line.startswith(("pass", "#")):
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}pass  # {stripped_line}\n")
                modified = True
            else:
                new_lines.append(line)
            
            i += 1
            
        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        print_status(filename, modified, "DM/camera/comm issues and other alerts commented.")
        return True
    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False

def modify_updated_py(filename):
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
            stripped_line = line.strip()

            if stripped_line == 'elif failed_count > 0:':
                if not (i > 0 and lines[i-1].strip() == "# 关闭长时间不联网限制"):
                    indent = line[:len(line) - len(line.lstrip())]
                    new_lines.append(f"{indent}# 关闭长时间不联网限制\n")
                    for j in range(6):
                        if i + j < len(lines):
                            block_line = lines[i+j]
                            block_indent = block_line[:len(block_line) - len(block_line.lstrip())]
                            new_lines.append(f"{block_indent}# {block_line.lstrip()}")
                    modified = True
                    i += 6
                    continue
            
            new_lines.append(line)
            i += 1

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        print_status(filename, modified, "Connectivity limit block commented out.")
        return True
    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False

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

            if "static void set_ir_power(int percent) {" in line:
                new_lines.append(line)
                if not (i + 1 < len(lines) and "(void)percent;" in lines[i+1]):
                    indent = "    " if not lines[i+1].startswith(" ") else lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{indent}(void)percent; // 忽略传入参数，避免编译器警告\n")
                    modified = True
                i += 1
                continue

            elif "int value = util::map_val" in line:
                if not (len(new_lines) > 0 and "// 强制设为 0" in new_lines[-1]):
                    indent = line[:len(line) - len(line.lstrip())]
                    new_lines.append(f"{indent}// 强制设为 0\n")
                    new_lines.append(f'{indent}std::ofstream("/sys/class/leds/led:switch_2/brightness") << 0 << "\\n";\n')
                    new_lines.append(f'{indent}std::ofstream("/sys/class/leds/led:torch_2/brightness") << 0 << "\\n";\n')
                    new_lines.append(f'{indent}std::ofstream("/sys/class/leds/led:switch_2/brightness") << 0 << "\\n";\n')
                    modified = True
                i += 4 
                continue

            new_lines.append(line)
            i += 1
        
        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        print_status(filename, modified, "IR power logic has been modified.")
        return True

    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False

# --- 主入口 ---
if __name__ == "__main__":
    print("Running all modifications...")

    modifications = {
        "registration": (modify_registration, registration_file),
        "launch_script": (modify_launch_script, launch_script),
        "process_config": (modify_process_config, process_config),
        "long_mpc": (modify_long_mpc, long_mpc),
        "pandad_py": (modify_pandad_py, pandad_py),
        "pandad_cc": (modify_pandad_cc, pandad_cc),
        "hardwared_py": (modify_hardwared_py, hardwared_py),
        "selfdrived": (modify_selfdrived_py, selfdrived_py),
        "updated": (modify_updated_py, updated_py),
        "hardware_h": (modify_hardware_h, hardware_h),
        "panda_init": (modify_panda_init_py, panda_init_py), # 🆕 调用新增的函数
    }

    results = {}
    for name, (func, path) in modifications.items():
        results[name] = func(path)

    if all(results.values()):
        print("\n✅ All modifications applied successfully or files were already in the desired state.")
        sys.exit(0)
    else:
        print("\n❌ Some modifications may have failed or were not applicable.", file=sys.stderr)
        failed_mods = [name for name, success in results.items() if not success]
        if failed_mods:
            print(f"  Potentially failed/unapplied modifications for: {', '.join(failed_mods)}", file=sys.stderr)
        sys.exit(1)
