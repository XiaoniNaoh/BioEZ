# Git 历史清理手册

> [!WARNING]
> 历史重写会更改所有受影响提交的 SHA，并需要强制更新远程分支和标签。不要在日常工作副本中执行，也不要在未通知协作者时执行。

## 前置条件

1. 先合并当前树的教材删除 PR，并暂停其他 PR 合并。
2. 通知所有协作者：维护结束后需要重新 clone，不应将旧分支直接 push 回仓库。
3. 保留一份访问受控的 mirror 备份，确认有权保留后再存档。
4. 安装 `git-filter-repo`，确认 GitHub 分支保护与强制推送策略。

## 在全新 mirror 中执行

```bash
git clone --mirror git@github.com:XiaoniNaoh/BioEZ.git BioEZ-purge.git
cd BioEZ-purge.git
git filter-repo --path '00 参考资料/' --invert-paths --force
```

`git-filter-repo` 通常会移除 `origin`。推送前先审查新历史、路径和对象体积，再恢复远程：

```bash
git remote add origin git@github.com:XiaoniNaoh/BioEZ.git
git push --force --mirror origin
```

## 验证

```bash
git log --all -- '00 参考资料/'
git rev-list --objects --all | rg '00 参考资料/'
git count-objects -vH
```

前两条命令应无输出，pack 体积应从约 1.6 GiB 显著下降。再从远程做一次全新 clone，检查默认分支、标签、Actions 和站点构建。

## 远程清理

历史重写后，GitHub 的 PR refs、fork 或缓存仍可能暂时引用旧 blob。如果目标包括撤回未授权公开分发，应检查所有远程分支和标签，并按 GitHub 指引联系 Support 清除无法由仓库管理者删除的缓存引用。
