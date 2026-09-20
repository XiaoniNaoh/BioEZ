#!/bin/bash
# 双击本文件即可启用「提交前检查」：
#   以后每次 Commit，都会先检查这次提交里的课程正文和课程目录 / 导航 / 清单是否对得上，
#   对不上就拦下提交，并告诉你该跑哪条命令修。检查只读，不改你的文件。
#
# 关掉：终端里运行 git config --unset core.hooksPath

cd "$(dirname "$0")" || exit 1

echo "=============================================="
echo "  BioEZ —— 启用提交前检查"
echo "=============================================="
echo

if [ ! -f .githooks/pre-commit ]; then
  echo "❌ 没找到 .githooks/pre-commit，仓库内容可能不完整。"
  echo
  read -r -n 1 -s -p "按任意键关闭这个窗口……"
  exit 1
fi

chmod +x .githooks/pre-commit 2>/dev/null
git config core.hooksPath .githooks

if [ "$(git config core.hooksPath)" = ".githooks" ]; then
  echo "✅ 已启用。以后在 GitHub Desktop 里点 Commit 时会自动检查。"
  echo
  echo "   • 检查不通过：会拦下提交，并提示先跑「准备提交.command」"
  echo "   • 跳过某一次：git commit --no-verify"
  echo "   • 彻底关掉：  git config --unset core.hooksPath"
else
  echo "❌ 设置失败，请改用终端运行：git config core.hooksPath .githooks"
fi
echo
read -r -n 1 -s -p "按任意键关闭这个窗口……"
echo
