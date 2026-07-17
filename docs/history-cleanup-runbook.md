# Git 历史清理手册

> [!WARNING]
> 历史重写会更改所有受影响提交的 SHA，并需要强制更新远程分支和标签。不要在日常工作副本中执行，也不要在未通知协作者时执行。

## 前置条件

1. 先合并当前树的教材删除 PR，并暂停其他 PR 合并。
2. 通知所有协作者：维护结束后需要重新 clone，不应将旧分支直接 push 回仓库。
3. 保留一份访问受控的 mirror 备份，确认有权保留后再存档。
4. 安装 `git-filter-repo`，确认 GitHub 分支保护与强制推送策略。

## 清理范围

不能只过滤 `00 参考资料/`。PBMC3k 曾使用过两个目录名，3 份项目 PDF 也已迁移到 Release；正式重写必须同时清理以下 8 个历史路径：

```text
00 参考资料/
.obsidian/plugins/
.obsidian/workspace.json
07 LLM 时代的生信入门/会用到的妙妙数据/
07 LLM 时代的生信入门/scRNAseq 入门-数据/
07 LLM 时代的生信入门/BIF B-1 scRNAseq 入门.pdf
07 LLM 时代的生信入门/BIF B-2 scRNAseq入门到UMAP注释.pdf
99 期末抱佛脚专刊（临时）/TEM 01 食品工艺学 一口气看爽.pdf
```

`MMB 99 分子生物学｜一本全.md` 是手工重复聚合页，不是大型二进制或第三方教材；在当前树删除即可，无需额外抹除历史。

## 在全新 mirror 中执行

```bash
git clone --mirror git@github.com:XiaoniNaoh/BioEZ.git BioEZ-purge.git
cd BioEZ-purge.git
git fetch --force --prune --prune-tags origin '+refs/*:refs/*'

git filter-repo \
  --sensitive-data-removal \
  --no-fetch \
  --force \
  --invert-paths \
  --path '00 参考资料/' \
  --path '.obsidian/plugins/' \
  --path '.obsidian/workspace.json' \
  --path '07 LLM 时代的生信入门/会用到的妙妙数据/' \
  --path '07 LLM 时代的生信入门/scRNAseq 入门-数据/' \
  --path '07 LLM 时代的生信入门/BIF B-1 scRNAseq 入门.pdf' \
  --path '07 LLM 时代的生信入门/BIF B-2 scRNAseq入门到UMAP注释.pdf' \
  --path '99 期末抱佛脚专刊（临时）/TEM 01 食品工艺学 一口气看爽.pdf'
```

`git-filter-repo` 通常会移除 `origin`。推送前先审查 `filter-repo/changed-refs`、新历史、路径和对象体积，再恢复远程。只强制更新可写的 heads 和 tags；GitHub 的 `refs/pull/*` 是只读隐藏引用，`--mirror` 会因尝试更新它们而被拒绝。

```bash
git remote add origin git@github.com:XiaoniNaoh/BioEZ.git
git push --force --all origin
git push --force --tags origin
```

## 验证

```bash
git log --all -- \
  '00 参考资料/' \
  '.obsidian/plugins/' \
  '.obsidian/workspace.json' \
  '07 LLM 时代的生信入门/会用到的妙妙数据/' \
  '07 LLM 时代的生信入门/scRNAseq 入门-数据/' \
  '07 LLM 时代的生信入门/BIF B-1 scRNAseq 入门.pdf' \
  '07 LLM 时代的生信入门/BIF B-2 scRNAseq入门到UMAP注释.pdf' \
  '99 期末抱佛脚专刊（临时）/TEM 01 食品工艺学 一口气看爽.pdf'
git rev-list --objects --all | rg '00 参考资料|\.obsidian/plugins|workspace\.json|会用到的妙妙数据|scRNAseq 入门-数据|\.pdf$'
git count-objects -vH
git fsck --full --no-reflogs
```

前两条命令应无输出，pack 体积应从约 1.6 GiB 降到数 MiB。再从远程做一次全新 clone，检查默认分支、标签、Actions 和站点构建。重新下载 `content-assets-v1` 的 3 份 Release 资产，与 `data/assets.json` 中的大小和 SHA-256 逐一核对。

## 远程清理

历史重写后，GitHub 的 PR refs、fork 或缓存仍可能引用旧 blob。记录 `git-filter-repo` 输出的 First Changed Commit，并从 `filter-repo/changed-refs` 统计受影响的 `refs/pull/*/head`。如果目标包括撤回未授权公开分发，仓库所有者还需按 GitHub 指引联系 Support，请求解除受影响的 PR refs、清理缓存视图并运行服务器端垃圾回收。

GitHub 的公开文档同时说明，常规 Support 只保证协助移除符合其定义的敏感数据；版权材料的 PR 引用是否受理需由 GitHub 判定。强推 heads/tags 成功不应被表述为已完成服务器端物理删除。
