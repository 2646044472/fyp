# 掌纹数据集｜来源和本机布局

这里只跟踪数据集说明，不分发图片、压缩包、标注、裁图、模板、特征、参与者信息或逐样本结果。下面是原发布方的**全库描述**，不是本项目实际训练／测试人数或分母。能看到下载入口，不等于获得转载、传给组员或上传云端的许可。每位使用者使用机构或发布方认可的授权；适用条款以你取得数据时的协议为准。

| 数据集 | 发布规模和采集条件 | 取得方式／使用边界 |
| --- | --- | --- |
| [MPD‑v2](https://cslinzhang.github.io/MobilePalmPrint/) | 400 掌、16,000 张原图；两台手机、两次采集，每掌每台每次 10 张。发布方另列派生 ROI 和关键点检测数据，不能再加进原图数量。 | 作者项目页列原始发行版入口及说明。依发布方条件取得；此仓库不转存。 |
| [Tongji Contactless（TCD）](https://cslinzhang.github.io/ContactlessPalm/) | 300 人、600 掌、12,000 张；同一受控非接触设备，两次平均相隔约 61 天，每次每掌 10 张。 | 原图和作者裁好的掌区是两份不同的发布物。均由作者项目页取得；不要把裁图当成额外采样或把下载链接当转载许可。 |
| [X‑Palm](https://github.com/X-Palm/X-Palm-2026#dataset-access) | 103 人、206 掌、6,006 图，含受控多光谱与手机静态照；用来讨论姿势、环境及采集域变化。 | 官方要求签署 EULA 并经批准，限非商业学术使用，禁止转发与重识别尝试。仅贴原发布入口，不在仓库或共享附件中放原件和衍生物。 |
| [CASIA Multi‑Spectral（CASIA‑MS）](https://biometrics.idealtest.org/dbDetailForUser.do?id=6) · [NIST 发布目录](https://tsapps.nist.gov/BDbC/Search/Details/225) | 100 人、7,200 张图，两次相隔超过一个月；每次三次采样，每次同时记录六个光谱（含白光）。 | 从 CASIA 发布方获取并核当前条款。不要和普通 CASIA Palmprint 数据库混用；一套多光谱不能计作六次真实复访。 |
| [IIT Delhi Touchless Palmprint v1](https://web.comp.polyu.edu.hk/csajaykr/IITD/Database_Palm.htm) | IIT Delhi 非接触采集，作者提供原始手图和自动归一化掌区。版本和输入类型要记录。 | 在作者页走申请方式；按 [v1 使用条款](https://www4.comp.polyu.edu.hk/~csajaykr/myhome/database_request/palm/term.htm) 审批、引用，不与 PolyU‑IITD v3 视作同一发行版。 |
| [11K Hands](https://wp.lancs.ac.uk/icvl/research/datasets/) | 官方全套 190 人、11,076 张，含掌面和手背。跑掌纹时仅用符合条件的掌面图；不将全套大小当成掌纹查询数。 | 从项目发布方的目录查原始入口与许可；不把第三方镜像条款当成原授权。 |
| 组内 Pi 自采 | 现场采集，实际人数、掌数、批次、光线和相机版本以受控记录为准。 | 仅按知情同意和组内规定处理；没有已授权的公开下载入口。同意采集不等于同意公开或转发。 |

## 组员怎样放本机数据

开发和合成测试不需要任何数据。获准使用的内容建议放在**仓库之外**的本机数据目录，由本机环境变量或命令行参数指定，不把个人路径硬编码到脚本：

```text
<local-palm-data>/
  mpd-v2/
    originals/
    author-roi/
  tongji-contactless/
  x-palm/
  casia-ms/
  iitd-v1/
  11k-hands/
  pi-capture/
  derived-local/
```

如果为了本机操作一定要放在克隆目录内，可放 `dataset/local/`。本目录默认忽略除本页和 `.gitignore` 之外的所有内容；不要 `git add -f` 绕过。保留发布方目录与原文件只读，裁图和分析产物另存。共享结果只放许可允许的匿名汇总；写清数据集及版本、切分、登记与查询条件、有效归一化覆盖、查询分母。运行前核训练与测试人员是否隔离、同人是否跨库重叠，不按数据集宣传数字补缺失。
