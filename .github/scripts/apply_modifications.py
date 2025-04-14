# 文件名: .github/scripts/apply_modifications.py
# 功能: 修改 registration.py 和 launch_openpilot.sh 文件

import sys
import re
import os
import fileinput # 使用 fileinput 方便原地修改

# --- Configuration ---
# 获取脚本所在的目录，用于构建绝对路径（更健壮）
# GITHUB_WORKSPACE 是 GitHub Actions 设置的环境变量，指向仓库根目录
repo_root = os.environ.get('GITHUB_WORKSPACE', '.') # 默认为当前目录
registration_file = os.path.join(repo_root, "system/athena/registration.py")
launch_script = os.path.join(repo_root, "launch_openpilot.sh")

# 定义目标行和替换行 (包括精确的前导空格)
imei1_target_line = "    imei1: str | None = None"
imei1_replacement_line = "    imei1='865420071781912'" # 注意：这里不需要额外的 Python 转义了
imei2_target_line = "    imei2: str | None = None"
imei2_replacement_line = "    imei2='865420071781904'"

# 定义要插入 launch_openpilot.sh 的行
lines_to_insert_in_launch = [
    "export API_HOST=https://api.konik.ai",
    "export ATHENA_HOST=wss://athena.konik.ai",
    "export MAPS_HOST=https://api.konik.ai/maps"
]

# --- Function to modify registration.py ---
def modify_registration(filename):
    print(f"Attempting to modify {filename}...")
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!", file=sys.stderr)
        return False

    modified = False
    # 使用 fileinput 实现原地修改，更安全
    try:
        # inplace=True 表示原地修改，backup='.bak' 可以创建备份（可选）
        for line in fileinput.input(filename, inplace=True, encoding="utf-8"):
            original_line_stripped = line.rstrip()
            processed = False

            # 1. Replace imei1 line
            if original_line_stripped == imei1_target_line:
                if imei1_replacement_line != original_line_stripped:
                    print(imei1_replacement_line) # fileinput 会将 print 的内容写入文件
                    modified = True
                    processed = True
                # else: 内容已匹配，直接打印原行（下面会处理）

            # 2. Replace imei2 line
            elif original_line_stripped == imei2_target_line:
                if imei2_replacement_line != original_line_stripped:
                    print(imei2_replacement_line)
                    modified = True
                    processed = True
                # else: 内容已匹配

            # 3. Comment out set_offroad_alert line
            elif re.match(r"^\s*set_offroad_alert\(\"Offroad_UnofficialHardware\",", line.lstrip()):
                if not line.lstrip().startswith("#"):
                    print("#" + line.rstrip()) # 加注释并移除可能的多余换行，print 会加回来
                    modified = True
                    processed = True
                # else: 已注释

            # 如果没有被以上规则处理，则打印原始行
            if not processed:
                print(line, end='') # 使用 end='' 避免 print 添加额外的换行符

        if modified:
            print(f"Modifications applied to {filename}.")
        else:
            print(f"No modifications needed for {filename}.")
        return True

    except Exception as e:
        print(f"Error processing {filename} with fileinput: {e}", file=sys.stderr)
        # 如果 fileinput 出错，可能需要手动恢复文件（如果有备份）
        # 或者在 Action 中处理错误
        return False
    finally:
        # 确保 fileinput 关闭文件句柄
        if fileinput.isstdin():
           pass # Nothing to close for stdin simulation by inplace=True
        # else: No explicit close needed for fileinput context


# --- Function to modify launch_openpilot.sh ---
def modify_launch_script(filename):
    print(f"Attempting to modify {filename}...")
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!", file=sys.stderr)
        return False

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content_lines = f.readlines()

        # 检查需要插入的行是否已存在
        lines_exist_status = {line_to_insert: False for line_to_insert in lines_to_insert_in_launch}
        current_content_stripped = {line.strip() for line in content_lines} # 优化查找

        for line_to_insert in lines_to_insert_in_launch:
            if line_to_insert in current_content_stripped:
                lines_exist_status[line_to_insert] = True

        if all(lines_exist_status.values()):
            print(f"All required export lines already exist in {filename}. No insertion needed.")
            return True # 无需修改

        # 寻找插入点：shebang '#!/bin/bash' 所在的行索引
        insertion_index = -1
        for i, line in enumerate(content_lines):
            if line.strip() == "#!/bin/bash":
                insertion_index = i
                break

        if insertion_index == -1:
            print(f"Error: Shebang '#!/bin/bash' not found in {filename}. Cannot insert lines.", file=sys.stderr)
            return False

        # 准备要插入的内容（只包括尚未存在的行, 确保有换行）
        lines_to_insert_now = []
        for line_to_insert in lines_to_insert_in_launch:
             if not lines_exist_status[line_to_insert]:
                 print(f"  Will insert: {line_to_insert}")
                 lines_to_insert_now.append(line_to_insert + "\n") # 确保加换行符

        # 如果确实有需要插入的行
        if lines_to_insert_now:
            print(f"Inserting lines after line {insertion_index + 1}")
            # 在 shebang 行之后插入所有需要添加的行
            new_content = content_lines[:insertion_index + 1] + lines_to_insert_now + content_lines[insertion_index + 1:]

            print(f"Writing changes back to {filename}")
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(new_content)
        else:
            print("No new lines needed to be inserted.")

        return True # 操作成功

    except Exception as e:
        print(f"Error processing {filename}: {e}", file=sys.stderr)
        return False # 操作失败

# --- Main execution ---
print("Running modification script...")
success1 = modify_registration(registration_file)
success2 = modify_launch_script(launch_script)

if success1 and success2:
    print("Modification script finished successfully.")
    sys.exit(0) # 成功退出
else:
    print("One or more file modifications failed.", file=sys.stderr)
    sys.exit(1) # 失败退出，使 Action 步骤失败
