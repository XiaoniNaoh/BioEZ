#!/bin/bash
# 双击本文件即可「准备提交」：
#   自动补齐文章元数据 → 写入「课程导航」→ 更新课程目录与清单 → 跑一遍检查
# 跑完之后回到 GitHub Desktop：填一句提交说明 → Commit → Push 即可。

cd "$(dirname "$0")" || exit 1

# 找一个可用的 python3（双击运行时 PATH 可能不全）
PY=""
for candidate in "$(command -v python3 2>/dev/null)" /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then PY="$candidate"; break; fi
done

echo "=============================================="
echo "  BioEZ —— 准备提交"
echo "=============================================="
echo

if [ -z "$PY" ]; then
  echo "❌ 没有找到 python3。"
  echo "   请先安装 Python 3（https://www.python.org/downloads/），或改用终端运行："
  echo "   python3 scripts/prepare_contribution.py"
  echo
  read -r -n 1 -s -p "按任意键关闭这个窗口……"
  exit 1
fi

"$PY" scripts/prepare_contribution.py
status=$?

echo
if [ "$status" -eq 0 ]; then
  echo "✅ 完成。回到 GitHub Desktop：填提交说明 → Commit → Push。"
else
  echo "❌ 有步骤没通过，请看上面的提示；修好后再次双击本文件。"
fi
echo
read -r -n 1 -s -p "按任意键关闭这个窗口……"
echo
