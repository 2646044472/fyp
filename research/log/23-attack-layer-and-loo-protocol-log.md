# 攻击层级与 LOO 协议日志：未知攻击不能靠随机切分

最后更新：2026-08-21。本日志将掌纹的 image-level attack 与采集端 physical presentation attack 分开，并审计一个可取得数据/分区工件的无接触**指纹**近邻。目的不是把指纹数据迁移为掌纹 benchmark，而是让本项目的自采攻击设计可以被复查和推翻。

## 1. 两个不能混写的攻击面

[Zhang et al., *A Review on Palmprint Image-Level Attacks*](https://doi.org/10.1007/978-981-95-6123-0_12) 的正式 metadata/summary 将 image-level attack 概括为 adversarial attack 与 reconstruction attack。这里的对象是已经成为模型输入的图像或模型决定过程；它不同于 ISO PAD 所定义的、在采集设备前拿纸张、屏幕或实体物件呈现的 physical PA。

本项目的 Gate 1/M 实验只测 sensor-side physical PA：攻击物是否在本相机、本阈值下同时通过 gate/PAD 和 target matcher。数字注入、模型/模板篡改、adversarial input pipeline 与 relay 是单独的系统安全问题，不能因光学 PAD 成功而宣称已经防住。该 review 本轮未取得全文，故不从它补写更细 taxonomy 或性能主张。

## 2. COLFISPOOF 实际给出的协议教训

[Kolberg et al. 的 WACV Workshops 2023 论文](https://openaccess.thecvf.com/content/WACV2023W/MAP-A/papers/Kolberg_COLFISPOOF_A_New_Database_for_Contactless_Fingerprint_Presentation_Attack_Detection_WACVW_2023_paper.pdf) 与其 [官方数据页](https://dasec.h-da.de/colfispoof/) 记录了 7,200 个 PA sample、72 个 PAI species 和两款 smartphone。数据页列出每个具体 PAI/material，作者的 [repo](https://github.com/dasec/COLFISPOOF) 提供 ground-truth、四个 LOO partition、预处理和 ROI script；partition README 明确每个 species 有 100 sample。

最值得借鉴的不是它的指纹模型，而是它将两种完全不同的问法并排公开：

| protocol | development/test 的关系 | 能回答什么 | 不能回答什么 |
| --- | --- | --- | --- |
| random baseline | 每一个 PAI species 都按 30%/20%/50% 进入 train/valid/test | 对已见 species 不同 frame 的分类 | 对未知材料、未知 PAI 或新重拍链的泛化 |
| four LOO groups | 一个完整 `printout`、`transparent`、`default color` 或 `colored silicone` group 不参与 train/valid，只在 test | 对该预定义 group 的未见攻击压力 | 对所有未来 PAI、所有设备或其他生物特征的泛化 |

官方页面称数据可在其链接下载且无需额外限制；本项目没有下载它、没有 hash 原始文件，也没有以此训练或报告任何数字。repo 目前没有显式 code license。因此它只作为 protocol 阅读工件，不能变成本项目的可运行 palmprint 数据依赖。

## 3. 自采协议因而如何收紧

每次攻击呈现应建立可追溯层级：

```text
presentation id
  -> PAI specimen id
     -> material family
        -> manufacture/output device and settings
           -> capture device/geometry/environment/session
```

在 development 前先确定哪一层会被留出。只有多个相关 specimen 支持一个 material family 时，才可写 `material-family holdout`；若只有一个纸张、一个屏幕或一个贴片，正确标签只能是 `held-out specimen`，或在改变输出/重拍设备时称 `output/capture-chain holdout`。所有层都要同时记录 bona-fide retry、APCER/BPCER 及 target-match IAPMR，防止通过增加真人拒绝来取得表面上的 PA 改善。

这比“随机把 print/screen 图分到 train 和 test”严格，但仍不自动说明真实世界鲁棒。小型 FYP 的合理目标是透明地说明在哪个 predeclared holdout 上失败或获益，而不是声称 universal unknown-attack protection。

## 4. 对候选主线的影响

M 只有在相对 B2 静态多谱、相同的 frozen PAIS hierarchy 和 session holdout 下仍降低最终 IAPMR 时，才可讨论主动 gate 的额外价值。若 B2/M 只在 random-split samples 上变好，可能只是记住了已见材料或重拍痕迹，不能支持 active illumination/freshness 的研究主张。
