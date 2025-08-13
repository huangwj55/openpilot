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
# 🆕 新增：updated.py 的文件路径
updated_py = os.path.join(repo_root, "system/updated/updated.py")


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
    print(f"Modifying {filename} to close DM errors and other alerts...")
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
            line_modified_in_this_iter = False 

            # --- 修改点 1: 增加 ignore 列表 ---
            target_line_1 = "ignore = self.sensor_packets + self.gps_packets + ['alertDebug']"
            line_to_add_1 = "ignore += ['driverCameraState', 'managerState', 'driverMonitoringState']"
            
            if target_line_1 in stripped_line:
                new_lines.append(line) 
                if i + 1 < len(lines) and line_to_add_1.strip() in lines[i+1].strip():
                    pass 
                else:
                    new_lines.append(f"{indent}{line_to_add_1}\n")
                    modified = True
                line_modified_in_this_iter = True
            
            # --- 修改点 2: 注释 commIssue ---
            elif "if not self.sm.all_alive():" in stripped_line:
                new_lines.append(line)
                if i + 1 < len(lines) and "self.events.add(EventName.commIssue)" in lines[i+1]:
                    next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                    i += 1 
                    modified = True
                line_modified_in_this_iter = True
            
            elif "elif not self.sm.all_freq_ok():" in stripped_line:
                new_lines.append(line)
                if i + 1 < len(lines) and "self.events.add(EventName.commIssueAvgFreq)" in lines[i+1]:
                    next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                    i += 1
                    modified = True
                line_modified_in_this_iter = True

            elif stripped_line == "else:" and i + 1 < len(lines) and "self.events.add(EventName.commIssue)" in lines[i+1]:
                new_lines.append(line)
                next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                i += 1
                modified = True
                line_modified_in_this_iter = True

            # --- 修改点 3: 注释 cameraMalfunction ---
            elif "if not self.sm.all_alive(self.camera_packets):" in stripped_line:
                 new_lines.append(line)
                 if i + 1 < len(lines) and "self.events.add(EventName.cameraMalfunction)" in lines[i+1]:
                    next_line_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                    new_lines.append(f"{next_line_indent}pass # {lines[i+1].strip()}\n")
                    i += 1
                    modified = True
                 line_modified_in_this_iter = True
            
            # --- 新增修改点 ---
            # 1. cloudlog.event("process_not_running", not_running=not_running, error=True)
            elif stripped_line == 'cloudlog.event("process_not_running", not_running=not_running, error=True)':
                if not line.lstrip().startswith("pass#"):
                    new_lines.append(f"{indent}pass#{stripped_line}{original_eol}") # Use original_eol
                    modified = True
                else: 
                    new_lines.append(line)
                line_modified_in_this_iter = True

            # 2. self.events.add(EventName.processNotRunning)
            elif stripped_line == 'self.events.add(EventName.processNotRunning)':
                if not line.lstrip().startswith("pass#"):
                    new_lines.append(f"{indent}pass#{stripped_line}{original_eol}") # Use original_eol
                    modified = True
                else:
                    new_lines.append(line)
                line_modified_in_this_iter = True

            # 3. self.events.add(EventName.sensorDataInvalid)
            elif stripped_line == 'self.events.add(EventName.sensorDataInvalid)':
                if not line.lstrip().startswith("pass#"):
                    new_lines.append(f"{indent}pass#{stripped_line}{original_eol}") # Use original_eol
                    modified = True
                else:
                    new_lines.append(line)
                line_modified_in_this_iter = True

            # 4. self.events.add(EventName.noGps)
            elif stripped_line == 'self.events.add(EventName.noGps)':
                if not line.lstrip().startswith("pass#"):
                    new_lines.append(f"{indent}pass#{stripped_line}{original_eol}") # Use original_eol
                    modified = True
                else:
                    new_lines.append(line)
                line_modified_in_this_iter = True

            # 如果当前行没有被上述任何条件处理过，则直接添加原始行
            if not line_modified_in_this_iter:
                new_lines.append(line)
            
            i += 1

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("  selfdrived.py modified to ignore DM/camera/comm issues and other specified alerts.")
        else:
            print("  selfdrived.py already in desired state for specified alerts.")

        return True

    except Exception as e:
        print(f"  Error modifying {filename}: {e}", file=sys.stderr)
        return False

# 🆕 新增：修改 updated.py 以关闭长时间不联网限制
def modify_updated_py(filename):
    print(f"Modifying {filename} to close long-term no connectivity limit...")
    if not os.path.exists(filename):
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    modified = False
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        target_block_start_str = 'elif failed_count > 0:'
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            indent = line[:len(line) - len(line.lstrip())]
            original_eol = "\n" if line.endswith("\n") else ""

            # Check for the start of the block
            if stripped_line == target_block_start_str:
                # This block consists of 6 lines (including the initial elif)
                # Check if the block is already modified as desired
                # It should have a preceding comment and the first line of the block should be commented.
                is_already_modified = False
                if i > 0 and lines[i-1].strip() == "# 关闭长时间不联网限制" and lines[i].lstrip().startswith("#"):
                    # Further check that the subsequent 5 lines are also commented
                    all_sub_lines_commented = True
                    for k in range(1, 6): # Check lines i+1 to i+5
                        if i + k < len(lines) and not lines[i+k].lstrip().startswith("#"):
                            all_sub_lines_commented = False
                            break
                    if all_sub_lines_commented:
                        is_already_modified = True

                if is_already_modified:
                    # Append the pre-comment and the block as-is
                    new_lines.append(lines[i-1]) # The "# 关闭..." line
                    new_lines.append(line)       # The "# elif failed_count > 0:" line (already commented)
                    for k in range(1, 6): # Append the next 5 already commented lines
                        if i + k < len(lines):
                            new_lines.append(lines[i+k])
                    i += 6 # Skip the entire processed block
                    print("  Connectivity limit block already commented.")
                    continue # Move to the next line after the block
                else:
                    # Block found and needs modification
                    new_lines.append(f"{indent}# 关闭长时间不联网限制\n") # Add the initial comment
                    modified = True # Mark as modified because we added the comment line

                    # Now, comment the 6 lines of the block
                    for k in range(6): 
                        if i + k < len(lines):
                            current_block_line = lines[i+k]
                            current_block_stripped = current_block_line.strip()
                            current_block_indent = current_block_line[:len(current_block_line) - len(current_block_line.lstrip())]
                            current_block_eol = "\n" if current_block_line.endswith("\n") else ""
                            
                            # Only add '#' if it's not already commented
                            if not current_block_stripped.startswith("#"):
                                new_lines.append(f"{current_block_indent}#{current_block_stripped}{current_block_eol}")
                                modified = True # Mark as modified if we actually commented a line
                            else: # Already commented (e.g., from a previous partial run or existing comments)
                                new_lines.append(current_block_line)
                        else:
                            break # Reached end of file
                    i += 6 # Advance index by the number of lines in the block
                    print("  Connectivity limit block commented out.")
                    continue # Move to the next line after the block
            
            # If not the target block start, just append the line
            new_lines.append(line)
            i += 1

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        else:
            print("  updated.py was already in the desired state for connectivity limit.")

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
    modify_updated_py(updated_py), # 🆕 调用新增的函数
]

if all(results):
    print("✅ All modifications applied successfully or files were already in the desired state.")
    sys.exit(0)
else:
    print("❌ Some modifications may have failed or were not applicable.", file=sys.stderr)
    failed_mods = [func_name for func_name, res_val in zip(
        ["registration", "launch_script", "process_config", "long_mpc", "pandad_py", "hardwared_py", "selfdrived", "updated"], # 🆕 增加到错误报告列表
        results
    ) if not res_val]
    if failed_mods:
        print(f"  Potentially failed/unapplied modifications for: {', '.join(failed_mods)}", file=sys.stderr)
    sys.exit(1)
