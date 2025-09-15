# GitHub 标签颜色标准化文档
## 1. 文档说明
本文档定义「team-project-management」仓库的标签体系，包含标签名称、十六进制颜色、分类及使用场景，确保团队标签统一。

## 2. 标签标准列表
| Label Name | Color Hex | Category | 适用场景说明 |
|------------|-----------|----------|--------------|
| bug        | #d73a4a   | Bug      | 功能异常或错误 |
| bug-critical | #b60205 | Bug      | 严重bug（阻断业务） |
| bug-major  | #d73a4a   | Bug      | 重要bug（影响核心功能） |
| bug-minor  | #fbca04   | Bug      | 轻微bug（不影响核心功能） |
| enhancement | #a2eeef | Enhancement | 功能优化（非全新功能） |
| feature    | #0e8a16   | Feature  | 全新功能开发 |
| documentation | #0075ca | Documentation | 文档编写/更新 |
| task       | #d4c5f9   | Task     | 日常任务（如配置调整） |
| question   | #d876e3   | Support  | 疑问咨询（非bug/功能） |
| help-wanted | #008672 | Support  | 需要外部协助 |
| good-first-issue | #7057ff | Support | 新手友好型任务 |
| priority-high | #ff4400 | Priority | 高优先级（需紧急处理） |
| priority-medium | #ffaa00 | Priority | 中优先级（常规处理） |
| priority-low | #cccccc | Priority | 低优先级（可延后处理） |
| status-in-progress | #009800 | Status  | 任务处理中 |
| status-review | #0366d6 | Status  | 等待代码审查 |
| status-done | #6a737d | Status  | 任务已完成 |
| status-blocked | #d73a4a | Status  | 任务被阻断（需解决依赖） |
| component-frontend | #2088ff | Component | 前端模块相关 |
| component-backend | #00dfb6 | Component | 后端模块相关 |
| component-db | #ff7700 | Component | 数据库相关 |
| wontfix    | #ffffff   | Resolution | 确认不修复（如设计如此） |

## 3. 颜色标准规则
1. Bug类标签：红色系（#d73a4a 及衍生色），严重程度越高颜色越深；
2. 功能类标签：绿色/蓝色系（#0e8a16、#a2eeef），区分全新功能与优化；
3. 优先级标签：橙-黄-灰渐变（#ff4400→#cccccc），优先级递减；
4. 所有标签颜色需符合 GitHub 视觉规范，避免过于鲜艳或相近难以区分。