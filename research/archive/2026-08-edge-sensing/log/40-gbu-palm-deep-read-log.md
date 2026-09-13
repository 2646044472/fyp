# GBU-Palm 深读：它如何改变掌纹方向

日期：2026-08-27。资料为 [GBU-Palm arXiv HTML](https://arxiv.org/html/2608.14389)，2026-08-14 v1。此记录专门处理一个会推翻我们掌纹候选的最新近邻，不把预印本写成已获同行评审事实。

## 读取范围

已读 abstract、introduction、data construction、metadata、protocol、all result tables、error decomposition、spectral/temporal intervention、conclusion 和 references。未拿到数据文件、许可、代码、hardware BOM 或作者回复，因此这些仍为 `Q`。

## 其已解决的内容

- 21,326 原生 16 秒掌纹 PAD 视频，105 subjects、210 palms，Print/Replay 和六种 illumination environments。
- 6,310 对同步 RGB-NIR 观察；metadata 包含 print material（A4/photo/matte/pearl/coated）、spectrum、crop、replay interface 和 attack lineage。
- P1 identity/palm/lineage disjoint 的 In-Env；P2 held-out environment 的 Cross-Env。
- RGB、NIR、RGB-NIR 的视频 backbone 对照，验证了融合的收益随 architecture 改变，且通过 temporal order shuffle/reverse 和 NIR probing 分析证据使用。
- 将 binary PAD 的错误拆成 TA/TR/FA/FR，表明 cross-environment 下 false accept 可以显著上升。

## 它没有回答的内容

- 全文没有 `IAPMR`、identity matcher 或 target match：它评估的是 binary PAD，FA 不是系统级 target impersonation success。
- 文中未提供 Raspberry Pi capture-to-decision、RAM、thermal、energy，或 sensor-on-time 成本。
- acquisition 一段提到 consumer phones/tablets/laptops 与同步 RGB-NIR system，但 protocol 是 environment holdout，不是明确的 capture-device leave-one-out；须等原始 metadata 核实。
- 数据写为 “will be released soon”，所以暂不能依赖它作为可运行 baseline。

## 对 P 的结论

原题中“多环境、RGB-NIR、视频、attack lineage、环境留出、时序/光谱分析”已经被直接覆盖，必须删除。唯一可讨论的窄问题是：在攻击 lineage/material 和 capture chain 留出时，PAD gate 与**预冻结的 1:1 verifier**共同作用能否控制 IAPMR，并在边缘设备的 latency/energy 预算下保留足够 bona-fide coverage。

这仍不是已证实的新方向，只是 GBU-Palm 正文中未覆盖的一种系统协议。若数据的 target identity/attack source 不能支持 matcher，或 GBU 后续版本已加 IAPMR，掌纹方向应停止，不再用“新 multi-modal palm PAD”包装。
