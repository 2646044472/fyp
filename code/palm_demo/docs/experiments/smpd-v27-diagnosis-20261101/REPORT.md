# SMPD v27暂停前缀：失败归因与受控后续

2026-11-01。本报告先只读检查封存日志，随后单独获得授权执行固定8图几何小试。原全量没有重启、覆写或续跑，STOP没有移除。祖先路径和本次code/palm_demo工作路径没有额外磁盘AGENTS.md；遵守用户提供的GitHub/代理与执行环境规则。未联网、安装、提交、推送或部署。

## 封存边界

父运行 `runtime/smpd-lossless-v27-20261031`，fp `710aac923ffd87b71a20716c494000ae9e3302056218dbd879a6a0b4b711cdd2`；续跑 `runtime/smpd-v27-continuation-20261031-r1`，fp `23778a4613d516f39138b3487238bad813484800c238d8b3916318bd19795e47`。只读 `report_smpd_continuation.snapshot()`验证父子协议/记录链，父216＋子1023＝1239/3217，末样本036-RF19。status=paused_STOP、STOP存在、子无inflight。末journal digest `2fa89b4581bcdd8cb40afd64d5a3cd938af8d2632de5ae409cd48bbb7db3c61a`。

1239条中354正确、676误认、209处理失败、零拒识/true_identity_nonunique，194正确且≤2.5s。460注册帧447特征成功/13失败，86/92身份进入完整五帧图库。本报告计数来自实际记录，不将未完成1978条推断成结果。原记录protocol中的历史source_commit与当前分支HEAD不是同一概念，本报告不自行证明任何远端HEAD。

## 互斥失败分解

|类别|数量|直接证据|
|---|---:|---|
|关键点跨度过小|183|roi_geometry_reason=pklnet_keypoint_span_too_small|
|ROI越界|26|roi_geometry_reason=roi_out_of_bounds|
|真身份缺图库但接受其他身份|118|truth_enrolled=false，真身份score不存在|
|真身份在图库但排序错|558|真身份在86项完整scores中，返回身份是argmin|

209处理失败全部HTTP400、空scores、同一定位不稳定消息、无terminal RF trace，每条均保留一次localization。所有1030个HTTP200查询的roi_geometry_valid均true。这支持将209个已完成失败归于ROI门，不支持归于网络HTTP、特征容量、图库加载或内存异常。它不分类历史旧v26容量失败、未提交尝试或未完成查询。

失败样本开始前最低可用内存约5.40GB，其他约4.73GB；这些标量没有证明完全没有换页/资源影响。HTTP400是应用返回的ROI失败，不是网络连接故障。

ROI几何有效不代表解剖学ROI正确。558个排序错误的上游归因仍未确定：不能仅凭姿态标签、低分差或几何门通过，断言裁剪错、姿态不对应或纹理冲突。真身份rank2有12例、rank3–5有30例、rank6–10有35例、rank>10有481例。

## 注册失败与缺图库

|身份|失败帧|原因|当前查询：正确/误认/处理失败|
|---|---|---|---|
|008|F03|越界|0/31/4|
|020|F02、F04|跨度过小|0/24/11|
|024|F02、F03、F04|跨度过小|0/33/2|
|025|F00、F03|跨度过小|0/30/5|
|041|F00、F01、F04|越界；aspect retry仍失败|尚未查询|
|080|F03、F04|越界|尚未查询|

固定五帧全部成功才注册。447成功特征中430进入86人图库，17属于未完整注册身份；不能改为部分注册。前4个缺图库身份140查询＝118误认＋22ROI失败，后22已包含在209内，不能重复计数。补图库不保证118条全正确。固定final distance1.0/margin0/rejection=false导致缺图库样本也会接受最优其他人，零拒识不是FAR或识别良好的证据。运行时不能使用真实身份标签判缺图库；拒识改善不等于正确识别。

## 姿态、身份与分区

|原始姿态标签|查询|正确|误认|失败|跨度/越界|
|---|---:|---:|---:|---:|---|
|F|180|143|22|15|11/4|
|RF|360|157|153|50|36/14|
|P|350|52|273|25|25/0|
|RP|349|2|228|119|111/8|

36个已查询身份均有处理失败和误认。完整逐身份、逐姿态、逐分区计数在by-identity.csv、by-pose.csv、by-partition.csv；1239条逐样本归因和原record digest在query-diagnosis.csv。身份036只完成15条，004完整固定前缀为34条，不能强补35。P/RP困难是关联，尚非ROI因果结论。

development994＝286正确/542误认/166失败；protected245＝68/134/43。原split为ID被5整除的18人保护，其余74人开发，完整目标2588/629。保护集仅报告既有基线总体，不用于新机制样本选择、阈值或人工逐例修补；未来候选冻结前不得通过这些已暴露标量反向拟合。此保护是前瞻性，不是独立盲测。

## 可复核匿名证据

距离越小越好。以下是原记录，无新特征推理。

|样本/sequence|证据|
|---|---|
|001-RP31 /26|span=.075858<.1，HTTP400，空scores|
|008-RF17 /256|解码宽2448，预测顶点x=2492.376，ROI越界；不能仅凭此证明坐标程序bug|
|008-F05 /244|ROI通过、真身份缺图库，错认057，best=.380705/second=.390000|
|001-RP30 /25|几何通过、branch_span_too_small诊断；错认031=.402692，真身份=.420591/rank31；不能直接认定解剖ROI错|
|006-P20 /189|ordinary真006第一=.358871；RF改错083=.385031，真=.402116/rank18|
|006-P25 /194|ordinary错079=.361328，真=.388672；RF纠正006=.380833，second=.384615|

676误认全部exhaustive_terminal_rf_evidence。731末级内部ordinary→RF：19错→对、13对→错、36保持正确、663保持错误。development分别14/12/32/530。它们是同一次请求内部的完整分数向量，不能叫独立旧算法重跑。简单撤RF会丢19当前正确、净少6正确；按分差组合/扫描阈值没有新的机制证据。准确性评分修改暂不合格。

开发集精确非唯一argmin只有2条：034-RF11/1160在055和081间同为.38583333333333336；036-RF19/1238在061和072间同为.39666666666666667。两条均误认、真身份不在并列、零开发正确受影响。结构性拒认的离线反事实只是286正确不变、542误认→540误认＋2拒认、166失败不变；未实施政策，不是正确识别提升。另需原168全部当前166正确逐例守护，不能从这两条推断全局安全。

## 延迟证据和缓存边界

|既有计时求和|秒|占全部HTTP|
|---|---:|---:|
|1239 HTTP|39002.299|100%|
|731末级HTTP|37733.257|96.75%|
|original_scoring|37953.523|97.31%|
|追加RF|272.681|0.699%|
|全部localization|517.577|1.33%|

计时嵌套不能逐行相加。1030个HTTP200 capture/extract共619.057s、gallery38250.852s。末级P50/P95=49.075/99.602s；299非末级=1.160/10.287s。仅对少量记录检查细分，未全量profile。003-RF11的166.913s中original scoring165.311s、RF.743s。original_scoring包含lazy exhaustive提取、配准、各级匹配，无法据现有日志分出FastCC/OpenCV/CompNet/Python；97%不是神经网络占比。仅移除追加RF的理想累计节省上界也只有约0.7%，还会丢正确。

已保存447注册feature NPZ、父/子各86 gallery NPZ；没有查询feature NPZ或持久化code-pair。scores可离线重放身份排序与ordinary/RF对照，不能重放新ROI、新逐帧聚合或新pair metric。相同源/解码/ROI/模型/版本锁下可只读复用注册图库；ROI改变必须重提取受影响帧，成功但不完整的17帧不能偷偷当注册完成。最终答案缓存不能作为推理提速。

原1030成功请求共有ordinary_calls=9,623,820，逐帧captured_pairs=3,786,153，因此相同代码对重复调用至少60.66%。源码AcceleratedFastCC.match的32×32分支是局部bool/float转换、matchTemplate、积分和min，无状态写入；可提出单请求内按有序左右码字节缓存old_match的精确等价假设。仍须证明全部输入语义相同、线程安全、trace计数保留、跨请求清空、内存有界；打包/锁开销可能抵消收益。未实现、未微基准、不能宣称60%整体提速。

## 最多三个机制方向与门槛

1. 固定OOB-only half-turn，保留原有效结果，原bounds/span/IoU=.5不变；现有008-F03证据支持有限几何试验，不支持183个span自动可修。已批准的8图见下，图像几何通过不是正确识别。
2. RF跨数据分布存在双向排序改变；现有19收益/13损失否定简单回退。未找到无标签选择机制前，不实施评分混合或阈值修改。
3. 单请求内相同32×32代码对精确缓存：先固定非生物fixture等价/成本微基准，再少量完整gallery真实配对。必须whole-gallery scores/route/身份完全相同，含缓存建立/内存/打包成本，并实测净收益；失败不调参重复至通过。GPU迁移仅规划，未安装依赖。

共同门：旧正确逐例不丢、误认不增加、目标失败实际减少；失败→wrong不能算识别改进。速度必须同主机同gallery/runtime/线程的实际净收益，正确≤2.5s覆盖不下降，启动/注册/查询分开。小试通过不代替全已见开发与原168回归，不自动授权全量或推广。

## 固定8图几何试验（唯一一次）

完整协议、机器结果、fixture和逐图日志在 `runtime/smpd-roi-oob-pilot-20261101`。protocol fp为900f736501be07c97c63a2ebd90541c0b2fc0fd11ceb6e27ef6974d82e47655a。非生物测试8/8通过后，在原CPU环境执行每图一次；实际PKLNetROI＋HalfTurnROIRecovery、ORT CPU、3线程、OpenCV1，无matcher/gallery。

5个OOB中恢复008-F03、041-F00、041-F04，IoU .905861/.944671/.974411，新增几何约465/1157/1020ms。041-F01及008-RF17 retry_geometry_invalid，保留失败并分别增加约943/358ms。008-F00与041-F02有效控制、001-RP31 span负控制全原样且零retry。全部8个原预测quad/diagnostics精确复现封存记录，原decoded RGB哈希相同；预设几何门全部通过，无异常。

只说明008可能补齐原五帧，041仍有F01失败不能注册。没有识别准确性或速度改善主张。父子2457文件stat不变，其中1838非NPZ逐字节SHA不变；619大型NPZ本轮只核对文件身份/size/mtime/ctime，未声称全部重hash。源/模型/依赖/8图另有逐字节哈希。STOP保留，原链/运行结果不改。后续真实识别小试需要另立协议与结果，不拼接原3217。

## 原168守护及硬件边界

`docs/experiments/v26-device-reference-20261030/summary.json`是验证实际v26的165/168 Windows基准；`docs/experiments/terminal-rf-full168-20261030/summary.json`为当前terminalRF候选166/168、2误认、157≤2.5s，P95 4.094s/max8.933s。须同时保护原165和新增纠正37d0c433，155原快速路径不得变exhaustive。不能用总正确相等掩盖逐例丢失。

强制要求见 `docs/protocols/CANDIDATE_DEVICE_REGRESSION_REQUIREMENTS_20261030.json`：169原图、全部168查询、4固定case、34次五帧注册；每例转移、原图/模板哈希、隔离支付确认/余额/重复确认/取消守护；启动、注册、首/热查询计时分开。历史half-turn全168实际v24误标v26，不能继承其资格。v27容器修复30注册＋8查询仅有限等价诊断，不是新全168证明。Pi推广前需要Pi本机回归及授权。

主agent只读硬件观察：Intel Core Ultra5 338H，12物理/12逻辑；内存33,873,752,064 bytes。4070 SUPER确实连接，driver610.88，12282MiB显存；CUDA UMD13.3仅表示驱动能力。原export-env torch2.15.0+cpu、torch.version.cuda=None、cuda_available=false；ORT1.31.1仅Azure/CPU provider，无ORT-gpu/cupy。base元数据也未发现这些GPU库，不代表全机任何目录都无CUDA环境。未安装依赖。可用内存、磁盘余量/瞬时IO由主agent提供，不是原实验瓶颈证据。

模型回执：主agent以gpt-6-astra请求创建本任务，工具可见回执只有canonical任务ID，没有独立actual-model字段；只能陈述请求被接受并创建任务，不虚构运行模型认证。

本数据是Windows公开已见开发数据；未完成前缀、顺序执行和各阶段不同gallery边界须保留。不是Pi速度、独立泛化或陌生人FAR证据。原始掌纹图像、ROI、特征、模型不写入本公开标量报告，也没有上传。

## 后续：唯一固定8查询真实识别小试

这一步在几何结果报告后另外获得明确授权，使用独立新目录 `runtime/smpd-oob-identification-pilot-20261101`。没有续写原3217记录。
协议在推理前封存，fp `a92d20f467909f77c559d14798c01e81c6eec60d5350636b0ff2e6409326b2e5`；driver fixtures 5/5通过。实际执行结果complete=True，预设pilot_pass=True。
008原F00..04五张均重新提取，原本有效F00/F01/F02/F04与父特征数组及codec严格一致。原86模板byte-copy保留，008模板使用新候选指纹/恢复来源；041未加入。实际LosslessUnionMatcher、magic2801166、UNIONV2、retained＋terminal RF、final1/margin0/rejection-off均断言。全87图库/cache/index只准备一次，原阈值及评分源不改。

|样本|原结果|候选结果|返回身份|route|本次HTTP秒|
|---|---|---|---|---|---:|
|smpd-008-F-05|wrong_identity_accepted|correct|smpd-008-right|pose_confident|0.731|
|smpd-008-F-06|wrong_identity_accepted|correct|smpd-008-right|pose_confident|0.693|
|smpd-008-F-07|wrong_identity_accepted|correct|smpd-008-right|pose_confident|0.708|
|smpd-008-F-08|wrong_identity_accepted|correct|smpd-008-right|compnet_evidence_confident|0.832|
|smpd-008-F-09|wrong_identity_accepted|correct|smpd-008-right|pose_confident|0.812|
|smpd-001-F-05|correct|correct|smpd-001-right|pose_confident|0.829|
|smpd-006-P-25|correct|correct|smpd-006-right|exhaustive_terminal_rf_evidence|94.299|
|smpd-001-RP-31|processing_failure|processing_failure|None|None|0.461|

预设门逐项结果（失败不调参、不重试）：
```json
{
  "all4_valid_registration_features_exact": true,
  "all5_registration_success": true,
  "all8_complete": true,
  "complete_gallery87": true,
  "controls_all_exact": true,
  "inherited86_copies_byte_exact": true,
  "negative_unchanged": true,
  "no_new_wrong": true,
  "target_genuine_correction": true,
  "target_no_new_processing_failure": true,
  "zero_transactions": true
}
```
运行异常：`None`。只报告实际保存的8条；没有补样本。
candidate HTTP时间为历史基线之后的单独epoch，注册/全图库ready另计，不能据此声称公平提速；原基线未重跑。所有token仅取消，无confirm/扣款。
原始保护回执：`{"all_file_bytes_and_stats_unchanged": true, "changed_paths": [], "files": 2457}`。
原链结束快照：`{"completed_queries": 1239, "journal_tip": "2fa89b4581bcdd8cb40afd64d5a3cd938af8d2632de5ae409cd48bbb7db3c61a", "state": "paused_STOP", "stop_exists": true}`。
完整机器摘要见recognition-pilot-summary.json；私有运行目录保留protocol、8条attempt/结果、5条注册记录、新特征和ROI、完整scores、支付/ready与source hash信息。
主agent对008-F03原图/候选ROI的视觉观察：可见指缝/掌纹及部分边缘背景；不作为关键点或解剖位置认证。
小试结论不代替原168守护，也不证明整个SMPD提升。不得推广、全量续跑、安装CUDA依赖或启动新的速度实验。

## 2026-11-01 后续规划记录：两条设备误认，只读审计

本回合只读代码、既有结果和原图，新增本节规划；未改算法、未启动评测或推理。当前无匹配项目的 Python worker；SMPD status=paused_STOP、1239/3217、STOP仍存在。后续步骤均为提案，不是启动授权，也不恢复原3217。4070 SUPER连接不改变本阶段CPU-only范围。未安装、下载、改网络、部署或改PPT。

协议校正：原168设备配对识别覆盖已完成，双方166正确/2误认，全部168 ROI/分数/决策与34组五帧模板相同。但首轮在候选113/168处未通过12 GiB启动门槛，余55条来自独立8 GiB门槛的continuation；这是实际协议差异，不能称原冻结12 GiB门槛全程通过。历史文件保持原样。159对153条正确且≤2.5秒存在分段/主机负载混杂，不是算法提速。后续任何新run恢复启动可用内存≥12 GiB、运行≥2 GiB、RSS≤14 GiB、单worker；不满足就记录停止，不降低门槛、不关闭其他应用。

### 已有证据足以避免一次重复诊断跑

来源：device-halfturn-guard-20261101-r1/regression-results.json；device-error-evidence-20261030-r2/audit/results.json；terminal_rf_evidence.py、registered_matcher.py、anchored_matcher.py、compnet_alternate_roi_matcher.py、indexed_demo_matcher.py。本地私有样本以后缀61f30739、8d6441d2关联，分别称A、B。早期审计两条的普通全图库分数及query quad与新基线逐项一致；从已保存pose/geometry支持分数按现有逐帧min、五帧best2还原出的完整RF分数向量，也与新基线完全相同。因此以下逐帧归因有跨版本数值核对，不是假定旧诊断自动适用。

两错来自同一设备case、同一真身份；均有完整五帧注册，均进入exhaustive_terminal_rf_evidence，非缺图库或提前退出。169原图全部主ROI有效，半转越界恢复在设备集未触发。目视原图有掌面/指缝，偏暗；没有人工解剖ROI真值，不能仅据观感认证定位正确。

|既有量|A|B|
|---|---|---|
|主ROI span|0.18193|0.15241|
|分支分歧|FC span仅0.01245；original/gamma IoU 0.20455|方向cos 0.19863、两头quad IoU 0.00406|
|真身份五帧RF距离|.424501,.440000,.423333,.429630,.424615|.395833,.413462,.394587,.418210,.421667|
|返回错误身份五帧RF距离|.424383,.394231,.404800,.405000,.389423|.423868,.375000,.416667,.389423,.398462|
|真身份/错误身份聚合距离|.423917/.391827|.395210/.382212|
|主ROI CompNet真身份名次|7/11|9/11|
|主ROI CompNet真身份五帧距离|.494374,.479996,.475640,.513393,.512186|.511302,.494358,.493882,.503387,.510842|

A已存在alternate ROI的CompNet真身份排名第一，但聚合.426356、margin .015090，未通过原.32/.08门。这不是可直接接受的识别正确，不能据此放宽阈值。B没有保存第二个有效原/gamma候选。两条真身份五帧注册ROI均有效，四帧双头一致、一帧span分歧；不允许换掉第五帧。

A/B诊断分别1487/1486次普通调用，其中1485均为pose调用，几何调用仅2/1；unknown target/query均0。真身份和最终错误身份的逐帧RF最小值均来自pose分支。观测到的所有pose/geometry支持均为完整784个RF有效位置，无额外内部越界支持损失。这削弱“再改padding支持/收紧局部配准即可修复这两错”的依据，也不支持直接换best-k。当前仍缺解剖关键点真值、旋转后定位重复性和未见会话结果；尚不能证明ROI是唯一原因。

全部168查询中23条双头不一致：2错、21原本正确。直接把不一致设为拒识会损失21条正确，绝不列为准确率改进。这里只统计已保存诊断，不执行新的拒识回放。

### 唯一优先机制：终末困难路径的无身份定位一致性修复

假设：部分有效但不稳定的ROI存在方向敏感定位错误；同一原图的固定直角旋转，映射回原坐标后可以形成一致的掌区定位。身份距离不得参与选择。它不同于此前失败的全图固定旋转替换，但同样可能失败，不能预称有效。

候选限于原流程已走到terminal exhaustive且原双头consensus=false的查询；所有原自信早退路径原样返回。保持现有越界半转规则独立，不扩大为无指缝样本修复。固定输入视图0/90/180/270度，复用原0度结果，其余各一次现有illumination localizer；不扫描角度/gamma、不增加任意crop。映射回原图后统一四角顺序，沿用现有span/bounds与IoU .5。事先冻结规则：至少3个不同旋转视图形成两两IoU≥.5的唯一最大团；只选该团中IoU总和最高的实际候选quad，不平均坐标。并列优先原0度，其余按固定角度顺序。无唯一三视图一致组则保留原结果，不拒识、不选身份低分ROI。三视图多数是预设几何一致性要求，不在结果上调成2或改变IoU。

若得到不同quad，直接从原像素采样一次，重算查询相关特征并对原完整图库重新评分一次，沿用原best2、阈值和terminal RF；禁止递归修复和新旧身份距离择优。该候选明确是查询侧定位修复，注册五帧政策保持冻结；不能声称解决缺图库、注册失败或所有姿态。额外计算只发生在原慢终末路径，首先检验是否真正认对，速度可能变差。

最小分阶段小试（需下一阶段单独冻结协议后才执行）：

1. 设备固定6查询：A、B；按原case/sample排序取首个正确且span分歧、首个正确且direction分歧；历史terminal RF纠正例；新相机首个自信快速正确例。角色重复则去重，不因结果不好补样。完整原case图库和每身份五帧保留。先仅几何检查：若A/B都不能产生不同且满足一致组的ROI，立即淘汰此机制，不继续身份推理或另扫角度。
2. 几何可行才做同一6例baseline/candidate配对。必须至少一条原误认变为正确且所有正确控制保持；重拍/拒识不算修复。任何正确变错/拒识/失败，或无真纠正，立即淘汰。输出每例转移、全图库/五帧分数、几何来源、HTTP及各嵌套计时、取消token和零交易。观察钩子须先证明基线分数/路径不变。
3. 设备通过后，才冻结独立目录的公开开发小面板：仅SMPD已完成前缀且属于既有development划分、排除此前8图；按全局序号首个分别选“已入库、错误、terminal、双头分歧”“已入库、正确、terminal、双头分歧”“正确、自信快速”“span失败”“OOB失败”“缺图库误认”。空类别明确缺失，不能换一个更好修的样本。保留原86图库、原五帧及原分母；不得读取reserved查询结果来选样。若修复目标类别为空，公开迁移小试暂不可执行。样本可有可见指缝人工注记，但注记不改选样/分母。
4. 公开面板应出现真实纠正且零原正确损失，才能称跨这两个已见开发面板有效；失败则不宣称跨场景改善、不在这批面板上迭代调参。通过后仍需原全168及先前固定的公开reserve/未来新设备会话验证；此处不授权启动。reserve不是训练来源已知的独立泛化集，也不能反复使用。CASIA/PalmBig v26不重跑来挑本候选。

不提出第二个并行算法候选：已有证据不支持再次叠加姿态搜索、改best-k或直接收紧拒识。若唯一机制失败，保留失败并回到解剖定位/表示能力证据，不临时兜底。

### 重算范围、资源与实际模型证据

只读阶段已完成旧日志归因，不需重跑diagnose_valid_support。未来小试注册政策不变，允许对源/模型/codec和每数组hash核验后复制冻结五帧模板至隔离目录；只算加载/图库ready，不能冒称新注册时间。改变ROI的查询必须重算pose、SIFT/上下文、CompNet、exhaustive特征和完整图库分数；不得复用旧ROI的查询特征或分数。若以后改成注册侧一致性策略，所有受影响五帧、模板/index/links、注册与全查询守护必须另算，不能沿用本提案资格。正式全168应按原要求双方各34次新鲜五帧注册。

设备原错误HTTP为5.831/5.568秒，主定位约.413/.446秒；已有11身份面板新注册100.613秒、加载ready13.863秒。额外3个定位视图可先用约1.2–1.4秒/触发例作粗略成本占位，旋转/illumination分支不同可更慢；第二次完整评分可再次花数秒，无法许诺≤2.5秒。设备6例双臂加几何观测暂设5分钟停止预算而非ETA；达到预算完成当前请求后停、标不完整、不重试。保留单次超时及失败。此前设备峰值约1.79 GiB是旧路径观测，新路径尚无测量。

公开续跑已有P95 HTTP约79秒、单条max约158秒，旧8图困难控制94.299秒；因此公开面板不能按设备速度估计，二次完整评分可能近似翻倍。预设30分钟面板预算、完成请求边界停，模型/图库ready与逐查询墙钟另计；这不是完成保证。当前不加载86身份图库、不占用GPU。资源门槛如前固定12/2/14 GiB，若不满足就不开始。

本回合没有切换模型或新建Astra任务；运行工具未返回actual-model字段，不能认证本回合由Astra执行。任务要求是Astra规划、Sol/Terra实现、Luna监控；本节为当前助手的可审计草案，Astra规划资格仍需有明确模型设置的后续审阅，不能用早先任务创建回执替代。未启动监控或新增自动化。

### 后续实现回合：六例已封存，12 GiB启动检查未通过

当前developer明确提供模型标识gpt-6.1-sol；仍没有独立工具actual-model回执。接入任务把上一节称作Astra规划，但上一节实际没有Astra执行证据，本回合不沿用该错误称谓。

新增隔离工具terminal_rotation_consensus.py、pilot_terminal_rotation.py及15项通过的合成测试；算法/触发/三视图几何团/medoid/单次重评分按上一节冻结。新授权将面板定为四设备＋两公开，而不是原草案六设备后六公开：两设备误认、首个同case正确terminal分歧控制、首个正确快速分歧控制；再按序选首个符合条件的开发F正面误认terminal分歧例、首个开发快速正确例。公开保留原86身份与五帧、不读reserved结果选样、排除以前8图。六例清单已写入本地protocol，源绑定指纹73ebec4ba28743bbeadf3eef48a72f42c70b2e83aaa96c1bcf6b46b3ad768214。图号/身份/路径不进入提交报告；候选代码不按这些信息分支。

正式一次启动预检记录available=11953897472 bytes=11.13293457 GiB，RSS=47538176 bytes，触发MemoryError: Frozen available-memory/RSS limit。没有RUN_STARTED、没有query record、没有加载模型/图库或实际图像推理；12条配对HTTP计划当前完成0条。保持12/2/14 GiB，未降低门槛、未杀应用、未重试或预约自动恢复。当前为资源未启动，不是候选准确率失败或通过；不能进入168回归。SMPD仍paused_STOP1239/3217、STOP存在。

脱敏实现/验证报告：docs/experiments/terminal-rotation-six-20261101/REPORT.md。本地私有protocol和startup-preflight回执保留在runtime/terminal-rotation-six-20261101。未修改正式服务、原图/模板或PPT，未安装GPU/下载/改网络。

### 后续授权资源复查与一次实际运行：10/12，未晋级

新授权后只读确认无已有项目worker；未对命令行不可见的pythonw或其他用户进程操作，也无可通过自身机制释放的存活项目缓存。重新核验原六例、模型、模板及协议，实际指纹为73ebec4ba28743bbeadf3eef48a72f42c70b2e83aaa96c1bcf6b46b3ad768214（接入消息有省略字符，采用实际文件核验值，不改协议）。可用内存恢复到≥12 GiB后启动一次。原11.13 GiB失败预检保持原样。

实际完成10条HTTP：设备4条baseline＋4条candidate，公开2条baseline。设备双方2正确/2误认，0拒识/并列/查询处理失败；两条旧误认均未纠正，两条正确控制保持。6条baseline完整分数/决策/路径/主ROI精确复现，4条candidate原流程shadow精确复现。D1一致组选择只带来最大0.0001220703125像素差异，仍触发重评分，原误认不变；D2/D3没有三视图组，D4快速原样。真实逐例ID、完整分数、ROI/变换、时间都保留在私有atomic records，不加入Git。

公开candidate准备开始前触发12 GiB启动内存门，未加载该组图库、未发送P1/P2候选查询。原结果保持complete=false/pilot_pass=false、MemoryError: Frozen available-memory/RSS limit。没有重试、续跑、168回归或公开全量。末内存available10.520969 GiB、RSS3.022110 GiB是结束快照，不是门判断瞬间；281遥测样本最小available3.194427 GiB、峰值RSS10.298286 GiB，Windows进程峰值10.298504 GiB。运行≥2/RSS≤14门未在样本中违反。公开字节全量前后SHA一致，SMPD始终paused_STOP1239/3217。10条原子record digest和固定唯一键另行核对通过。

事后仅合成验证发现两件事：PKLNet预处理会将横图转竖，非方形图四旋转实际产生两组相同网络输入；不能称四份独立定位证据。另HTTP epoch内部GC时，handler/server/closure仍在栈上持有App；在epoch返回后GC才可释放合成App的引用环。已增加后者通用清理helper和receipt，保持candidate/scoring/阈值原样，19项合成测试通过。这不证明实际缺口全部来自该引用环，且补丁未用来重复图像实验。修改driver前已核验旧锁并byte-exact归档executed-driver.py，协议/结果不覆写；当前源码的清理补丁需要未来单独源码绑定，不能伪称本次使用。当前不晋级候选；公开候选迁移效果仍未知。脱敏REPORT和summary.json已更新，源图、失败及未跟踪私人文件保留。
