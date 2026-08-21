# 维护访问故事证据日志：工作流先例不等于澳门市场

最后更新：2026-08-21。这个日志审计“受控、时限维护核验”为什么能成为候选故事，也明确它尚未证明什么。目的不是为掌纹找一个听起来合理的应用，而是保证故事可以被现场流程和成本数据推翻。

## 1. 读到的外部证据

现行 [NIST SP 800-171r3](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/800-171r3/NIST.SP.800-171r3.html) 将以下事项区分开来：

1. `03.07.06` 要求建立 maintenance personnel authorization process、维护 authorized personnel/organization list、核验非陪同维护人员所需授权；未具备授权者应受具备授权与技术能力者监督。
2. 同一节的 discussion 指出，未预先识别的 manufacturer、vendor、consultant、systems integrator 可能需要 privileged maintenance access；组织可依 risk assessment 发放一次或极短期的 temporary credential。
3. `03.10.01`--`03.10.07` 又独立讨论设施 access list、发放/移除 access authorization、physical access monitoring 和 audit log。它列出的 physical access device 包括 keys、locks、combinations、biometric readers 和 card readers，未指定其中任何一种必须使用。

与之互补的 [NIST SP 1800-2b utility scenario](https://www.nccoe.nist.gov/publication/1800-2/VolB/index.html) 以工单触发 centralized authorization，预同步到现场 PACS，完工后 de-provision；该 scenario 的通信失败是能源变电站背景下的行业输入。

[Chin, Kim & Choi (2017)](https://doi.org/10.1016/j.proeng.2017.07.204) 则提供了一个反向的采用证据。它以 construction field 的访谈、现场观察和实际使用视频比较 RFID、QR、指纹、静脉、虹膜和人脸；其研究现场发现，姿态调整和 false rejection 使 biometrics 的处理时间高于 RFID/QR，论文的峰值通行模型把 FRR 与每人处理时间共同计入总排队/终端数量。这个结论**不**证明澳门、维护工作或掌纹的具体数字，但足以反对把 biometrics 写成普遍更快或更方便的门禁替代。

[Yamasaki et al. 的 door-key management model](https://www.researchgate.net/publication/31910237_Modeling_Costs_of_Access_Control_with_Various_Key_Management_Systems) 还有一个不同层面的提醒：它将 door 视为 resource、key 视为 credential，把 smart card、biometric、metal key 与 password 放入同一 policy-change/issue/collect/revoke 的抽象，再计算改变授权关系的管理操作成本。它不是实地调查，也没有设备采购、使用者等待、攻击或澳门数据；但它说明比较方案时不能只看一次识别，而要把授权、撤销、补发、登记和维护流程逐项记入 `C_deploy/C_operate/C_existing/C_switch`。

这些资料足以支持一件有限的事：**临时、时限、可审计的维护访问是一个真实存在的 access-control workflow pattern。** 它们不证明目标工作流应该用掌纹，不证明澳门存在同样网络/流程问题，也不提供任何经济价值数值。

同样重要的是，这个候选不能扩张为施工考勤、人员统计或高峰入口。若一个点位需要连续处理大量人流，或现有 QR/RFID 已满足吞吐与例外处理，生物核验引入的 pose/retry 成本就是反对部署的证据，而不是再加入更多终端的理由。

即使场景是关键工具或实体钥匙领取，也不能假定掌纹有优势。先问现有台账、钥匙柜、卡/QR 或人工流程在“授予、撤销、借出、归还、遗失、审计”各步骤的实际成本；没有明确差异时，保持为 B0 测量 demo，而不是把 resource custody 当经济故事。

## 2. 因此什么可以成为 demo，什么不能

```text
existing work order / authorization system
          |
          v
signed, versioned record: pseudonymous claim + site/tool + time window + expiry
          |
          v
Pi performs local palm 1:1 only for the presented claim
          |
          +--> match + valid record -> minimal audit event
          +--> mismatch / expired / unknown version / live-revocation needed -> human fallback
```

这里最重要的边界是：工单/授权系统才是 permission source of truth；Pi 不创建权限、不解释法律或劳动资格，也不在 record 过期、版本不确定或需要实时撤销时自行放行。掌纹只回答“呈现者是否匹配该已授权 claim”，并且必须有非生物 fallback。

## 3. 经济故事必须收集的证据

下列每项必须来自目标流程的访谈、shadowing 或已有记录，而不是标准、论文或个人体感：

| 必要证据 | 最小问题 | 若答案为空，项目结论 |
| --- | --- | --- |
| 工作量与期限 | 一个月有多少 temporary/limited-time access 或 tool handover？谁授予、谁撤销？ | 没有足够场景，不主张应用需求。 |
| 例外成本 | card/QR/工单、人员、网络或审计发生例外时，谁多花多久？ | 没有可计量人工/审计代价，不虚构 ROI。 |
| 网络与离线规则 | 何种故障下可用预同步且未过期记录？何种情况必须等待后台/人工？ | 离线功能不成立，删除 offline value claim。 |
| 真实替代方案 | 现有 card/PIN/guard/商用 palm terminal 为什么不够？ | 没有明确差异，做 B0 measurement demo，不写部署故事。 |
| 接受度与公平 fallback | 是否允许 biometric？拒绝、手套/伤口、隐私顾虑怎样处理？ | 若无可接受替代路径，停止现场 biometric 主线。 |
| 吞吐边界 | 该点位是否有高峰多人通行？每次需在多少秒内完成，重采一次的后果是什么？ | 若是考勤/人流入口或 QR/RFID 更快且足够，排除该场景，不以 biometric 替代。 |

## 4. 这轮反思

“maintenance access”比“澳门没有掌纹”更可辩护，因为它是一个可画出的授权状态机，而不是对城市技术普及度的猜测。但它仍只是一条**候选**叙事：如果本地访谈显示工单与卡片已经足够、网络稳定、临时访问极少，或组织不接受 biometrics，正确结果就是不部署。届时论文应收敛为低成本 edge palm verification/PAD measurement，而不是继续把维护故事写成经济价值。
