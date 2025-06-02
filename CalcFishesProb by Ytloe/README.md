需要 pip install numpy

主方法在 CalcFishesProb，主要难点攻克：计算优先级排序同优先级随机排序的方法 calc_fishing_prob

test 中的方法仅用于比较原始方案和新方案的差别以及验证新方案的可靠性

需要额外安装 pip install psutil

另外学习了一下 commit message 应该怎么写

用 git 推送代码到 github 需要填写 commit 信息

commit message 规范：

类型(作用域)：主题

正文

类型：

- feat：新增功能
- fix：修正错误/bug
- refactor：代码重构
- docs：改文档
- style：改风格
- test：测试相关的修改
- chore：杂项
- perf：优化性能
- ci：CI/CD 相关改动
- build：改构建系统或依赖
- revert：回滚提交

作用域：具体改了什么地方

主题：概括这次推送做了什么

正文：推送修改的细节详情
