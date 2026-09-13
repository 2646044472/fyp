# 主目标 Prompt

在项目根目录打开一个 Codex CLI，然后直接粘贴以下内容：

~~~text
设定以下为当前主目标：

找到并锁定一个适合计算机科学本科 FYP 的、可防守的 edge 研究方向。方向只需属于 edge 领域，不限于掌纹、RGB/NIR/ToF、多传感器融合或安全监测；可以是 edge AI、edge sensing、edge systems、edge reliability、edge privacy、edge resource management 等，但必须有明确的计算机科学研究问题。

该方向必须同时满足：

1. 有真实且范围受控的故事：明确谁在什么场景下作什么决定、错误会造成什么具体伤害，以及为什么 edge 约束是问题的一部分；
2. 有精确且可证伪的研究主张，而不只是新模型、部署到树莓派、换一个数据集或单纯压缩/加速；
3. 与最接近的已有工作存在可审计、可逐项比较的区别；
4. 能在实际可获得的数据、硬件、伦理、时间和算力条件下完成最小实验；
5. 即使正向假设失败，也有诚实且有价值的负结果或 pivot 路径。
6. 核心贡献应主要来自算法、系统、数据协议、评估协议、可靠性/隐私/资源机制或可验证的理论边界；不能把购买硬件、搭建盒子或普通应用界面误写成 CS 创新。

可与 Bob Zhang 教授的公开研究方向保持适度相邻，例如 hand biometrics、multimodal/incomplete view、image restoration、anomaly detection、uncertainty 或可信 edge vision；但这只是导师匹配和可获得建议的加分项，不是选题前提。先检查其最近和最接近的论文，避免重复其已完成的任务；只有在问题、假设、评估终点或资源约束上有清楚差异时才保留。

先阅读 AGENTS.md，再使用 research-direction-discovery 和 research skills。开始前先读取 research/active/ 下的当前 canonical state；只有候选与历史主题重叠时，才读取 research/archive/2026-08-edge-sensing/，以避免重新包装已被淘汰的想法。

你是 coordinator。立刻并行启动两个独立 subagent：

- 发散 subagent：严格执行 research/ops/agent-divergence.md。优先阅读近期、高相关性的原始论文，特别关注 limitations、assumptions、failure cases 和 future work；必要时回溯经典论文以确认概念来源和已知边界。提出真正不同、可证伪、以 CS 贡献为核心的 edge 候选。对每个候选同时写清故事与创新：故事解释真实决策和伤害，创新解释相对 direct neighbor 的精确可证伪差异。不要默认维护已有想法。
- 验证 subagent：严格执行 research/ops/agent-validation.md。主动尝试杀死当前候选：寻找 direct neighbor、后续引用链、精确主张重叠、不可识别/不可能性结果、硬件和数据不可行性，以及能消除贡献的简单 baseline。

给两个 subagent 足够独立完成工作的上下文。它们只能写入各自在 research/ops/ 下的目录，禁止修改 research/active/、research/archive/ 或 .research/。

等两个 subagent 返回后，你自己读取并比较它们的输出，直接向我汇报：

- 每个候选的状态：PROMOTE、HOLD、KILL 或 PIVOT；
- 哪些是有来源支持的证据，哪些只是猜想；
- 两个 subagent 的具体冲突；
- 当前最强的 direct neighbor 或 kill risk；
- 唯一最有价值的下一步。只有真的卡住时，才问我那个会改变下一道研究 gate 的问题。

禁止宣称某个方向“全球首创”或“没有人做过”。任何创新主张在通过三轮审计前都只能标为 Amber：
1. component collision；
2. exact-claim collision；
3. boundary / impossibility。

每个关键结论必须给出原始论文或官方来源 URL、版本或日期、精确 section/page；无法核实的内容必须明确标成未验证。

持续自主推进研究轮次。我随时可能中断你、改变范围、补充约束、回答问题或要求解释。我的最新消息优先级最高：立刻停止或重定向未完成工作，保留有用证据，并从修改后的目标继续。
~~~
