# FYP 开发与实验交接

新电脑先进入 [`code/rasp/`](rasp/README.md)，不要维护第二份学校快照。仓库只包含可分享的源码、合成测试和汇总说明；模型、真实原图及 ROI、模板、受试者清单和逐样本结果均由授权人员在设备本地管理。

## 先选入口

| 工作 | 入口 | 边界 |
| --- | --- | --- |
| 新识别基线和相机演示 | [FPN + C E10 独立站](rasp/fpn-c-e10-station.md) · [CPU 预检与单次评分](rasp/fpn-c-e10-shadow.md) | 原生 PyTorch，不需要 ONNX。需要两份可信本机模型和仓库外清单；当前仓库版本尚未在 Pi 5 上由本次交接验收。 |
| 旧 Pi 服务更新与回退 | [PKLNet + FastCC v6](rasp/README.md#部署到-pi-5) · [旧引擎和原始采集](rasp/ENGINE-README.md) | 旧 Pi 服务仍是 8088，不用新站覆盖旧环境、模板或数据。 |
| 复现研究机制或统计程序 | [可移植研究代码](../gitea-um/research_code/README.md) · [协议与汇总目录](rasp/docs/protocols/README.md) | 不是全量冻结实验运行包；训练数据、冻结权重与逐样本证据不附。 |
| 审查实验依赖或离线裁掌几何 | [实验登记](experiment_registry/README.md) · [ROI 几何检查](offline_roi_audit/README.md) | 合成测试和离线工具；未提升为实时裁掌策略。 |
| 找授权数据和历史读数 | [数据集出处](../dataset/README.md) · [学校交接与报告](../gitea-um/README.md) | 历史报告和学校快照不作为第二个部署目标。 |

## 树莓派和 Yesand

- 新站按[启动说明](rasp/fpn-c-e10-station.md)创建独立 Python 环境和私有运行目录。先按[模型清单说明](rasp/fpn-c-e10-shadow.md#仅在已授权设备装入冻结模型)核对可信 SHA-256，再跑 `preflight`。CPU 依赖须适用于本机；Pi 5 ARM64 的安装、延时和实拍须另验。
- 当前新站是 **Pi 回环 8080**。从 Yesand 用空闲本地端口转发，例如 `ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8080:127.0.0.1:8080 PI_SSH_ALIAS`。将别名换成自己的；如本机 8080 已占用，可改左侧端口。先在本机访问 `/station-health`，确认 `backend: fpn-c-e10-frozen`；`ready` 不表示任意当前帧合格。旧 Pi 8088 的文档示例是 Yesand 8089→Pi 8088，不能用原书签验证新引擎。旧阶段提交曾用 Pi 8089；以当前检出的版本为准。两个站不要同时占用相机，也不要暴露到公网。
- **当前新站**至少有效采集 60 秒（暂停时不计时），候选够 10 组后手动挑选；计时后可继续采集，不是整个流程最多 60 秒。首轮按排名前 5 组建模板。确认前检查同一曝光的原图、高清 ROI 与 128×128 模型 ROI，支持删除补拍；确认后去新站 `/collect` 核对照片库和尺寸。用旧引擎做独立全分辨率原始采集则走旧站自己的 `/collect`，切换前先释放相机。目录、模板和参与者信息不混用。
- 新站 `/gate` 可用默认 0.80 给出演示匹配，**不等于拒识已校准，不用于通行**。需在获得许可的实拍中另测同掌、陌生掌、端到端时延和采集兼容性，不能把合成回归当成板端结果。

## 现有实验能从哪接手

| 已有实验代码 | 公开复现入口 | 未随仓库分发 |
| --- | --- | --- |
| 几何／增强、MPD 标点裁图、20 epoch 历史训练与评分口径 | [研究代码](../gitea-um/research_code/README.md) 中的 `geometry.py`、`intake.py`、`augment.py`、`train.py`、`protocol.py`；CPU 合成训练仅跑一步 | 历史训练用私有加载脚本、个体级划分、实拍与权重 |
| 冻结 FPN + C E10、固定五图注册与单图查询 | [独立原生推理](rasp/fpn-c-e10-shadow.md)：`preflight` 或指定本机输入运行 `shadow-score`；[协议目录](rasp/docs/protocols/README.md) 说明口径 | X 上逐库批运行、私有角色清单和冻结模型；单次入口不等于批量论文复现 |
| MPD 配对的 C／PalmBridge、Tongji 跨访次配对、非 MPD 多库、MPD 全图与手视野诊断 | X 本地实验已有成套运行脚本；公开侧从[计数协议](../gitea-um/research_code/README.md)、[分析报告](../gitea-um/README.md)和[数据来源](../dataset/README.md)核对条件 | 经过路径和依赖审查，原脚本仍绑定本机实验、数据适配器或授权工件；当前公共检出不能重跑这些冻结读数。未把它们混入应用目录或包装成可移植 CLI |
| ROI 缺失、方向、可见覆盖和规则切换 | [离线几何](offline_roi_audit/README.md)及 [覆盖计数示例](../gitea-um/research_code/README.md#replay-the-crop-fallback-without-biometric-data) | 原图和诊断样本，尚未推广的留出验证、现场替换和新优化均不在此交接中 |

若已在本机取得两个方法的逐查询结果，使用 [配对结果计数器](experiment_registry/paired_outcomes.py) 把它们放在一份固定查询计划里，只输出汇总（`python code/experiment_registry/paired_outcomes.py --self-test` 无外部依赖）。它不执行模型、不拟合阈值、不复跑历史实验。

按固定协议统计时保留全部计划查询，包括未登记、缺图和未裁出 ROI 的查询；识别名次与接受／拒绝单独报，不用测试集调阈值。配对比较使用同一独立名单、固定注册张数和相同查询。

## 改代码先跑合成检查

```sh
cd code/rasp
python3 verify_best_frame.py
python3 verify_review.py
python3 verify_ranked_window.py
python3 verify_adapter.py
python3 verify_fpn_c_e10_shadow.py
python3 verify_fpn_c_e10_native.py   # 安装了原生依赖
python3 verify_fpn_c_e10_station.py # 安装了所需图像／服务依赖；模拟相机
```

离线诊断用各自 README 的单元测试。普通改动说明改了哪一条路径、命令和结果、哪些还要 Pi 实机复核。按 [仓库数据规则](../AGENTS.md) 只提交复核过的文件；不要提交本机清单、权重、真实原图或 ROI、身份信息、运行日志和凭据。
