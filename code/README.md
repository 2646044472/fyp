# 组员协作：从这里开始

**日常开发树莓派用 [`rasp/`](rasp/README.md)**。这是原 `palm_demo` 的后续位置，不要在旧目录或学校快照里另改一份。目录同时有登记、验证、采集管理页面和底层识别引擎，Pi 借此运行。页面或选帧调整先在电脑以合成数据测试，再到 Pi 接相机验收。

| 要做的事 | 直接入口 |
| --- | --- |
| 换电脑、修改登记／选帧／验证界面 | [Pi 采集站 README](rasp/README.md)，从 `rasp/` 跑合成回归 |
| Pi 部署、验收、手动回退 | [Pi 部署说明](rasp/README.md#部署到-pi-5)，设备配置、模型和记录保留在 Pi |
| 看引擎实现及历史行为 | [底层引擎](rasp/ENGINE-README.md) · [评测协议](rasp/docs/protocols/README.md) |
| 准备有授权的评测数据 | [数据集来源、条件和本机布局](../dataset/README.md) |
| 改离线裁掌诊断或依赖登记 | [offline_roi_audit](offline_roi_audit/README.md) · [experiment_registry](experiment_registry/README.md)，不影响 Pi 采集 |
| 查历史 KEYPOINT 模型、复现旧结果 | [PKLNet 上游组件](pklnet/README.md) · [学校进展记录](../gitea-um/README.md)，不是日常 UI 改动入口 |

## 换机后先跑四条

在新电脑从 [Pi README](rasp/README.md#换一台电脑开发) 克隆，只要 Python 3，不用复制有生物数据的旧工作目录：

```sh
cd code/rasp
python3 verify_best_frame.py
python3 verify_review.py
python3 verify_ranked_window.py
python3 verify_adapter.py
```

进 Pi 前先确认是否正在采集，不在进行中的登记期间重启。把更新的代码带过去，不带第三方训练数据和临时运行目录。一条合并请求只放一个功能，描述影响登记／验证哪一步、如何测试、是否还要实机验证。不要因为合成测试通过就宣称识别准确率或响应速度变好。

`code/pklnet/` 是另存的老版源码和复现材料，不是新工作入口。已部署的 Pi 兼容基线仍以 PKLNet 裁掌和 FastCC v6 识别，运行依赖应由目标机提供和核对，不要删近用依赖，也不要把研究机的 FPN 结果当成 Pi 已运行版本。组员只需要修改 `rasp/` 时不必先复制另一个实验目录。
