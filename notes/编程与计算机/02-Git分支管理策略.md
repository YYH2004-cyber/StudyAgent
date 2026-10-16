# Git 分支管理策略

> 分类：编程 | 日期：2026-10-12 | 标签：git, 工程实践

## 两种主流策略对比

| 维度 | Git Flow | Trunk-Based |
|------|----------|-------------|
| 常驻分支 | main + develop（另有 feature/release/hotfix） | 只有 main |
| 集成频率 | feature 完成后合入 develop，周期较长 | 每天多次小步合入 main |
| 适用场景 | 版本发布周期长的客户端软件、App | 持续交付的 Web 服务、小团队 |
| 优点 | 流程清晰、版本隔离性好 | 集成冲突小、问题暴露早 |
| 缺点 | 分支长期存活，合并冲突地狱 | 依赖 feature flag 和高测试覆盖 |

## 常用分支操作

```bash
git switch -c feat/login             # 创建并切换到新分支
git switch main                      # 切回主干
git merge --no-ff feat/login         # 合并（保留合并节点）
git rebase main                      # 变基：把本分支提交挪到 main 顶端
git branch -d feat/login             # 删除已合并分支
git push origin --delete feat/login  # 删除远程分支
git log --oneline --graph --all      # 图形化查看分支拓扑
```

## 我的理解

- GitHub Flow ≈ 简化版 trunk-based：main 永远可发布 + Pull Request + CI 门禁。
- rebase 适合整理本地未推送的提交，merge 适合合入公共分支；**已推送到公共分支的提交严禁 rebase**。
- 分支策略没有银弹，核心只有一句：小步集成 + 自动化验证。分支活得越久，合并越痛苦。
