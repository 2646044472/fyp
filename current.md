# 当前进度：树莓派掌纹基础 Demo（2026-10-06）

## 用户当前目标

先把掌纹算法和最基本的演示跑通，再考虑 FYP 研究方向。用户会自己重拍；采集和演示操作不应强制等待“稳定五帧”，也不应要求每张之间移开手或手臂。

## 当前设备与页面

- 树莓派的调试服务 `palm-debug-ui.service` 正在运行，局域网地址 `http://10.12.194.1:8080/`。
- `/collect` 已可连续采十张，每张保留 3280×2464 原图，并显示自动定位的 128×128 ROI 和 512×512 原始像素局部；此页仍存在。
- 2026-10-06 本轮新增 `/demo`：五张高清录入、一次高清查询、显示候选身份及实际送进匹配器的 ROI、人工确认后扣除 MOP 20 模拟余额。识别错误可取消重拍。页面在 Pi 上可访问；`/api/demo/users` 返回正常。**没有在真人手掌上完成端到端操作检查。**
- **部署状态要特别注意：** Pi 上目前部署的是 `/demo` 的第一版：使用原有宽 ROI + DoN。工作区随后已改为“精细关键点 ROI + FastCC”、增加取消接口，但这批最新代码**尚未传到 Pi，也尚未重启服务**。不要把下面的新结果误写成现网已生效。需要部署的文件至少有 `code/palm_demo/debug_ui.py`、`demo_flow.py`、`demo_page.py`；部署后应检查服务状态和页面。当前 `/collect` 所用宽 ROI 仍与 `/demo` 拟采用的精细 ROI 不同。

## 现有照片和直接观察

- `minutes/10-06-highres-own-capture-diagnostic.md`：旧组 38 张，左 17／右 21，均为同一人，连续短时间采集。旧预览曾使用局部传感器视野；离线比较全部从高清原图重新定位裁图。
- `minutes/10-06-white-labelled-continuous-capture-diagnostic.md`：新组 20 张，左 10／右 10，同一人。标签写“白纸”，但原图实际仍显示暗色桌面和绿色区域，不能据此评价白纸作用。
- [E] 原来用拍照前预览帧坐标裁高清图，新组只生成 16/20 个 ROI；直接从所保存高清图重新定位为 20/20。旧坐标与新坐标的 ROI 中心相差中位数约 51.5 像素（左）和 86.2 像素（右），最大约 638 像素。`/collect` 此后已改为高清图拍后重新定位。
- [E] 新组用高清图 ROI、前五张录入／后五张查询时，现有 DoN 正确手排第一 7/10。同手与另一只手的距离中位数分别 0.1243、0.1251；调试阈值下限 0.15 接受全部十次另一只手比较。此数据只有一个人的两只手，**不能据此计算人口层面误认率**。

## 本轮算法对照（刚完成）

脚本 `code/palm_demo/tools/compare_pi_roi_variants.py` 从原图重新检测，比较宽 ROI（MCP 跨度的 2.0 倍）、掌心核心 ROI（1.3 倍）、是否使用 21 点手部姿态、DoN／FastCC、128／256 输入，以及固定 CLAHE。报告在忽略版本控制的 `code/palm_demo/data/processed/pi-own-captures/highres-2026-10-06/white-continuous-2026-10-06/roi-variant-comparison.json`。前五张作 gallery；同组查询只用其余照片，跨组查询用对方组全部照片。

| 输入与匹配器 | 旧组内 | 新组内 | 旧组录入→新组查询 | 新组录入→旧组查询 |
| --- | ---: | ---: | ---: | ---: |
| 宽 ROI + DoN（当前调试算法） | 11/28 | 7/10 | 8/20 | 22/38 |
| 精细关键点核心 ROI 128 + DoN | 28/28 | 7/10 | 9/20 | 24/38 |
| 精细关键点核心 ROI 128 + FastCC | 28/28 | 10/10 | **8/20** | 24/38 |
| 上行加固定 CLAHE + FastCC | 28/28 | 8/10 | 8/20 | 23/38 |
| 精细关键点核心 ROI 256 + FastCC | 28/28 | 6/10 | 13/20 | 32/38 |

- [E] 21 点姿态模型对旧组 38/38 都输出精细定位，对新组只输出 14/20：新左 9/10、新右 5/10。其余样本自动回退到粗掌部检测；尤其新右第 6–10 张均回退。裁图来源应在演示结果中提示。
- [E] 新旧两组相机曝光中位数由约 10 ms 变为左 6.11 ms／右 6.36 ms，增益由约 1.06–1.14 变为 1.0。用归一化后的精细 128 ROI 计算，旧组掌心中心 Laplacian 方差中位数约 116–131，新组约 62–71；新组的整体像素标准差反而更高（约 43–46 对旧组 26–28）。这支持“大范围亮暗变化更强、细小纹线信息更弱”的描述，**不能单独证明是对焦、照明、运动或算法哪一个造成**。
- [E] `code/palm_demo/tools/check_pi_cross_group.py` 的固定 HOG 对照：128 ROI 的旧→新为 13/20；256 ROI 为 14/20。并非只有 DoN／FastCC 出问题。输出在同目录 `cross-group-check.json`。
- [C] 跨组骤降最可能是裁图位置／方向、光照和纹线细节的联合变化。单纯 CLAHE、中心截取或换一个匹配器都还没有稳定跨组证据。
- [GAP] 所有数据只有一个人，左右手同组是连续照片；尚无独立受试者、真正跨天或不同条件的固定对照，也没有人工标注的标准掌心 ROI。旧新组已被反复查看，不能作为未触碰的验证集。

## 新右手 8–10 张 ROI 失败复现（2026-10-06）

- [E] 直接对新右手 `sample_008`、`sample_009`、`sample_010` 的 `full.jpg` 重新运行当前工作区检测器，三张都成功得到 `tracking`：掌心检测分数分别为 `0.8657`、`0.9758`、`0.8901`，MCP 跨度约 `107.9`、`52.1`、`96.5` px，几何检查均通过。
- [E] 启用 21 点姿态模型时，这三张没有走 `handpose`，而是正确回退到 `palm_detector`；再用精细 1.3 倍核心 ROI 计算也全部成功。因此这些原图不是“没有可检测的手”。
- [E] 这三张保存的元数据却是 `roi_available=false`、无 `roi_error`。原因是它们来自旧版采集路径：该路径只使用拍摄前实时预览的 ROI；实时帧没有新 ROI 时，拍下的高清图也不会重新检测。工作区当前 `capture_highres()` 已改为对刚拍下的 `full.jpg` 调 `detect_full_still()`，但这批修复尚未部署到 Pi。
- [E] 右手第 8–10 张的 `FocusFoM` 为 `3066/3032/2838`，曝光为 `4.688/4.442/4.007 ms`；相比第 1–5 张更暗且清晰度指标下降，属于需要继续控制光照/对焦的成像问题，但不能解释旧路径的 `NO ROI` 记录。

## 2026-10-06 新采集 benchmark 与预处理复跑

- [E] 从 Pi 拉回最新两组各 10 张：左手 10/10、右手 9/10 已保存 ROI；对 20 张高清原图重新运行当前 detector，结果仍为 `19/20` 成功，唯一失败是右手第 1 张，错误为 `span_too_small`。
- [E] 右手第 1 张不是模糊导致：detector 的 close-range recovery 得到检测分数 `0.9012`，但在 320×240 检测坐标中 MCP 跨度只有 `27.1 px`，低于当前 `32 px` 几何门槛。图像里手掌过近、多个手指和掌根贴近/超出画面边缘，导致关键点几何不完整；21 点姿态模型也不能修复这一张。
- [E] 对其余 19 张分别测试原始 ROI、CLAHE、去光照、256×256 ROI 后再缩回 128，以及组合预处理。用同一 subject 的左右手做小规模留出 sanity check（前 5 张 gallery，后 5 张 probe；不是人口级识别准确率）：原始 128 ROI + DoN 为 `4/10`，原始 128 ROI + FastCC 为 `4/10`；CLAHE 128 + FastCC 为 `7/10`。
- [E] 最好的本轮组合是“高清 256×256 ROI -> CLAHE -> 缩回 128”+ FastCC：`8/10`，类内/跨手距离中位数约 `0.4100/0.4175`，间隔约 `0.0075`。但样本只有一个人、左右手也不是独立负样本，不能把 `8/10` 当成真实身份识别率。
- [E] DoN 对这些预处理基本没有收益，FastCC 在 CLAHE/高分辨率先处理时略有改善；因此当前主要问题不是“再锐化就能解决”，而是 ROI 几何、采集姿态/边界和跨组条件变化。预处理 benchmark 输出图在 `code/palm_demo/runtime/pi-latest-2026-10-06/preprocess-benchmark/`，尚未把任何预处理强行接入线上流程。

## 2026-10-06 PKLNet 接手记录

- [K] 远端 `origin/main` 的提交 `7e575ad` 新增完整 PKLNet 源码和 `net_params_500.pth` 权重；已从该提交取到当前工作区的 `code/pklnet/`，但没有把 `origin/main` 整体合并进当前分支，因为 `debug_ui.py`、`palm_roi.py` 等存在本地冲突。
- [K] PKLNet 的 ROI 流程不是直接输出 ROI 图片：先把输入按上游 `test.py` 旋转/缩放/补零到 `400x300`，网络回归掌边关键点，再由 `code/pklnet/roiExtractor.py` 的 `getROIckp()` 生成四边形并透视成 `128x128` ROI。
- [C] `code/palm_demo/pklnet_roi.py` 已建立懒加载适配器，保留 PKLNet 原始预处理和坐标反变换；当前 Python 3.13 环境没有 PyTorch，因此尚未在本机完成权重加载和图片推理，也尚未接入 `debug_ui.py` 的正式采集路径。
- [GAP] 下一位接手者需要先在可运行的 PyTorch 环境验证 `net_params_500.pth` 能加载，并用 `runtime/pi-latest-2026-10-06/highres_capture/` 的 20 张高清图输出 PKLNet ROI；重点检查左右手方向、四边形是否覆盖掌心、右手第 1 张是否仍失败，再决定是否替换当前 detector 或保留 detector fallback。
- [GAP] PKLNet 原始 README 要求 Python 3.8、PyTorch 1.7 和 GCC 7.5；不能假设当前 Python 3.13 或树莓派系统直接兼容。正式部署前需要单独验证 CPU 推理耗时、内存和 PyTorch 安装方式。

## 代码状态与下一步

1. 工作区中的 `/demo` 已改用 FastCC + 21 点姿态优先的 1.3 倍掌心核心 128 ROI；精细定位失败会回退粗掌部定位。匹配只**排序候选人**，没有可信的陌生人拒绝阈值；用户核对姓名后才能模拟扣款。`runtime/demo_templates/` 和 `runtime/demo_payment.sqlite3` 与旧调试数据隔离。上述新改动尚未部署。
2. 先审查并部署最新演示代码，确认页面能走完“录入→查询→显示 ROI／裁图来源→确认模拟扣款”；不要把组内 10/10 写成识别可靠。若要改动 `demo_flow.py` 的存储格式或匹配器，先处理旧模板兼容；现网 `/api/demo/users` 在本轮部署后曾返回空列表。
3. 为了判定为何跨组差，可在现有高清图上盲标一小批掌心四角，比较人工 ROI 与自动 ROI 的跨组分数；只改变一个物理因素重拍（固定距离与手掌姿态，记录曝光／增益，依次改变照明或对焦）。采集按钮仍可立即拍摄，不必加稳定等待。将后一批照片留作真正未参与调参的验证。
4. 若人工 ROI 仍使跨组匹配接近随机，再考虑经过公开数据训练且能合法取得权重的成熟掌纹模型；若人工 ROI 明显改善，优先修定位。任何阈值都需要多人的非同手分布，不能从当前两只手的十几张照片估计。

## 工作区注意事项

- 根目录 `AGENTS.md` 将研究资料与 demo 实现分开；用户当前明确要求先完成 demo。`research/active/` 研究方向目前不用更新。
- 工作树已有大量用户自己的已修改／未跟踪文件，不要清理、重置或覆盖。原始采集图和上述诊断报告在忽略版本控制的 `code/palm_demo/data/processed/` 下。
- 技术说明和已知限制：`code/palm_demo/README.md`；现网调试服务配置：`code/palm_demo/palm-debug-ui.service`。
# 2026-10-25 接续：ROI v3 与恢复复核（本地完成，未部署）

- 当前工作区 C:/Users/bankey/Desktop/code/research/fyp。用户明确要求优先修算法，忽略对比度/锐度门槛；Pi 网络由用户处理，暂不排查或部署。
- 默认 PKLNetROI 已改为固定 heatmap 分支，版本 pklnet-heatmap-v3。避免与方向相反的 FC 端点直接平均，所有样本用相同规则。两分支一致性只记诊断；有限值、越界和最小跨度仍是几何约束。旧 legacy/consensus 策略显式保留作历史复现。
- 相同40原图、每手前5录入后5查询、无质量或几何筛样本的实际 ONNX 回放：DoN 3→11/20，FastCC 9→11/20，配套神经 matcher 12→14/20。36/40 通过几何，4张仍错误；不可称彻底解决定位。真实几何拦截另算完整20查询：DoN10/20、FastCC11/20，拒绝2查询，gallery为5/4/5/4。
- 端点对齐后平均的替代方案 DoN5/20、FastCC7/20、神经13/20，未启用。现有 OpenCV 手检测器四方向对照仅返回22/40，且存在明显背景误检，未作为回退。
- 对比度/锐度仅记录，不拒绝匹配；完全常量图仍不能归一化。旧ROI模板不混用，新录入原编号保留账户、余额、交易，五张成功才替换。
- 92项相关测试通过（包含ONNX）；历史 test_existing_pipeline.py 仍引用已迁移模块，未纳入。实际heatmap与独立PyTorch缓存最大坐标差0.019043px。
- 最新报告、实际回放、文件hash与补丁在 code/palm_demo/runtime/pi5-new-camera-20261021/heatmap-v3-20261025/。consensus-v2报告/zip仅为历史，已被取代，不再以拒绝样本或补拍作为当前修复结论。
- 用户进一步要求查本地 PalmIR 式恢复的方法。已查训练源码/配置及权重哈希：CompactRestorer，PolyU-II掌类别ROI，Gaussian/motion模糊训练，冻结配套神经matcher的RIA损失；不是官方PalmIR，也不是为DoN直接优化。
- 本轮全40张、固定6个输入/恢复变体：raw、RIA、半强度混合均神经14/20；1/99亮度归一化、归一化+RIA、归一化+半强度均15/20。DoN/FastCC全为11/20。只查询恢复与双侧恢复均未增加正确数。不能把归一化收益归于恢复。
- RIA对原始相机ROI平均仅改0.086/255；归一化后仅0.025/255。原PyTorch权重与ONNX最大差2.8e-5，排除本批次的导出误差。8张预定训练域图加合成Gaussian1.5的响应检查有明显恢复，不能当独立验证。更像训练退化与实际输入不匹配，不能证明相机图模糊。恢复实验在 restoration-adaptation-20261025/。
- 已有pixel-only checkpoint对照：原始输入神经13/20，归一化后15/20；仍无恢复增益。恢复完整报告 restoration-adaptation-20261025/report.html，最新补丁为 heatmap-v3-20261025/heatmap-v3-patch.zip，zip内逐文件SHA验证通过。
- 尚未训练新模型，未改研究队列或历史科学实验。后续若做相机域恢复训练，应固定ROI、用训练身份做匹配的成像退化与少量几何扰动，保留新身份/新会话独立验证；不要以当前40张反复调参后冒充验证。
- **未部署Pi。** 只保留本地可复现修复。连接恢复后先检查并备份远端代码/服务配置，保留capture-only或recognition原模式，离线验收再重启。不要将USB断开时10.55.0.1的VPN端点误作Pi。

# 2026-10-26：参考 ROI 对照确认主要瓶颈

- 用户要求“继续，肯定是ROI问题”。完成40张助手目视指缝参考点：食指–中指、无名指–小指＋掌心侧点，统一PalmKit alpha=.15/beta=1.2。匿名随机编号显示，未显示自动预测或分数；但此前已看过标签，不能称盲法或独立人工金标准。评分前复查全40张，纠正S05一次坐标并记录，然后固定文件SHA。
- 原划分20录入/20查询、全样本不筛选，只换ROI：DoN旧融合3→自动heatmap11→参考17/20；FastCC9→11→19/20；神经原像素12→14→17/20。参考ROI归一化神经16/20，RIA均无额外收益。**19/20是目视参考ROI的开发对照，不是自动修复后的准确率。**
- 自动heatmap与参考框IoU中位数.754，9/40低于.5；不只此前4个几何拒绝，部分合法框覆盖不同掌区和尺度。
- 自动原型都保留失败结果且未启用：分割范围放大再定位DoN6/FastCC10/神经12；GrabCut轮廓三指缝（16/40替换，其余heatmap）7/4/13；灰度四方向MediaPipe仅19/40返回框。不能把这些当修复。单图OpenCV5 vs ORT detector同输入原始输出接近，未找到该图的后端解释。
- 当前默认仍heatmap-v3，无新增运行时算法修改、训练或Pi部署。下一步应针对真实两个指缝定位做相机域校准/训练，当前40张是开发标注，需新会话验收，不可训练后拿同批40张冒充验证。Pi仍由用户处理。
- 新工具：audit_reference_roi.py（prepare/render/score，评分后禁止改标注）、audit_pklnet_zoom.py、audit_contour_valleys.py、write_reference_roi_report.py；audit_landmark_roi.py增加可选灰度输入。全部实际回放完成，脚本编译检查通过。未改应用代码，不重复主套件（上一轮92通过）。
- 产物：code/palm_demo/runtime/pi5-new-camera-20261021/reference-roi-20261026/，含annotations、输入哈希、全部40张自动/参考叠图、逐查询分数、geometry-summary.json、report.html。参考标注SHA 7cfafd709f8697813f114d1990213723affa28332574f764ed7e741a9938915b。失败原型分别在segmentation-zoom-20261026、contour-valleys-replay-20261026、landmark-gray-20261026；无数据清理。

# 2026-10-27：Pi 5 连接修复、部署与历史数据端到端验收

- 用户授权离开期间自主排查并跑通完整流程，后明确要求用之前的数据；已通过 USB `10.55.0.1` 登录 `rasp5`（用户 `fyp5`），Wi-Fi 当时为 `192.168.31.55`。凭据不保存到文件。
- USB 故障根因：UDC 为 configured，Windows RNDIS 正常，但 Debian 的 `85-nm-unmanaged.rules` 把 gadget 标为 `NM_UNMANAGED=1`，导致 usb0 DOWN。已安装 `/etc/udev/rules.d/90-usb-gadget-managed.rules`，限定 usb0，重新加载并启动现有 `usb-gadget` 连接。PC DHCP `10.55.0.27`，SSH/HTTP 通过；仓库留有同名 deploy 规则。
- 部署前备份在 Pi `/home/fyp5/maintenance-20261027/palm-demo-before.tar.gz`（SHA256 `509af3ea962f7ab91f3af8ddb85cd6d3770c0340697add9b06d4594a67ad002b`），并保存服务配置。已部署当前 heatmap-v3 运行时代码和 diagnostic ONNX，模型加载校验通过。服务保持 capture-only。
- 用户接入 UVC 相机后实测预览、状态、自动对焦状态与 2592×1944 全图拍摄，HTTP 正常，拍后预览恢复；镜头无手掌，未宣称真人现场识别。用户随后拔掉 USB 相机。服务已重启到等待相机状态，下一次接入可启动。发现拔出后旧 JPEG 仍报 ready，已修复五秒新鲜度判断、stale 预览 HTTP503 和拍照前 stale 检查；不是自动热插拔恢复。
- 并行相机/推理负载时有真实欠压日志，`get_throttled=0x50005`；降低回放负载到一个 CPU 核后为 `0x50000`（只留历史标志）。没有上一启动日志，不能断言之前卡死唯一原因。需要足额供电再长时间运行相机＋推理。
- 新相机 40 图在 Pi 实际回放：旧融合几何31/40、heatmap36/40；无筛图 DoN3→11/20，FastCC9→11/20。启用几何检查且保留20查询分母，Pi上DoN与FastCC均10/20（FastCC与此前本地11/20不同，按实测报告）。实际五图录入只有两组左手成功，两组右手各有坏几何录入图。不能称新相机算法已完全修好。
- **旧数据完整流程通过**：本机只有10月12–13日四个ZIP（sessions.json记12组，不能称全120张已用）。校验SHA后40图不删样本，四个掌纹身份各1–5录入、6–10查询；几何40/40，DoN/FastCC离线20/20，实际HTTP DoN20/20，4/4录入成功。每身份一张留出查询正确后确认模拟MOP20，四笔交易、余额100→80；重复确认与取消后确认均拒绝。采集/ZIP、恢复/参考/过期快照也通过，共125次HTTP请求。相机边界使用历史图，ROI、matcher、模板、交易和HTTP处理均为真实代码；生产数据和账户未改。
- 新工具 `code/palm_demo/tools/replay_pi_pipeline.py` 支持原始runtime或ZIP目录，必须全新独立输出；保存全部输入哈希、逐图诊断、全分母评分、HTTP轨迹和模拟数据库。Pi输出分别 `/home/fyp5/pipeline-audit-20261027` 与 `/home/fyp5/pipeline-older-audit-20261027`。
- 本地结果与中文报告：`code/palm_demo/runtime/pi5-maintenance-20261027/report.html`。证据包 `pipeline-evidence.tar.gz` SHA256 `64757a41881a5fade1c0f51eaa17709ed42b7a3cef50f2d5996dbb5044748e98`。53项相关测试通过；2项本地缺ORT而跳过，实际ORT已在Pi运行。原始图前后哈希不变。

# 2026-10-27：新相机 ROI v4 条件重试（已部署）

- 当前默认 `pklnet-heatmap-aspect-v4`：先用 v3 全图；仅越界/跨度过小的几何失败图，按原方向居中取4:3视野重试，再映回原图、按原有阈值检查，从原始像素透视裁图。无身份选择、无人工标注参与推理、无训练或阈值放宽。显式 `policy="heatmap"` 保留 v3。
- 新相机40图，本地和Pi一致：几何36→40/40、五图录入2→4/4、全20查询DoN10→13/20、FastCC12/20。真实HTTP DoN13/20，4个身份各以一张正确留出查询完成隔离模拟扣款，重复/取消后确认被拒绝。还剩7张错配，几何通过不代表准确掌心；不能称彻底修好。
- 旧四ZIP40图本地重放：几何40/40、DoN/FastCC20/20、4录入4扣款。新相机原本有效36张和旧40张ROI像素均完全不变。原始数据哈希不变。
- Pi单核实测ROI中位1.52s/p95 3.06s，重试需两遍推理；本次前后throttled=0x0。新相机数据是反复查看的开发集，不是独立验证。参考标注17/20和19/20不可当自动结果。
- 已核对主机密钥，经Wi-Fi192.168.31.55部署并加载ONNX验证，服务重启正常，保持capture-only等待已拔摄像头。不要向当前走tun0的10.55.0.1发凭据。备份 `/home/fyp5/maintenance-20261027/pre-aspect-v4-231905/`；Pi回放 `/home/fyp5/pipeline-roi-v4-20261027/`。
- 证据与中文报告 `code/palm_demo/runtime/pi5-roi-v4-20261027/report.html`，`deployment.json`有部署SHA。38项相关测试通过。更换几何版本后需重录模板，原账户余额保留。
- 未采用的热图锐化/峰值期望、全量4:3裁图、分割视野实验保存在 `runtime/pi5-new-camera-20261021/heatmap-decoding-20261027/` 和 `aspect-roi-20261027/`。下一步应以新会话验证，并改善几何合法但位置不一致的掌心定位。

# 2026-10-28：持续改善 ROI、PalmIR 与现场画质压力测试

- 用户要求继续自主迭代，因为现场demo可能同样画质；已创建当前聊天每小时heartbeat，automation ID `roi-palmir`，有实质改善/完成/失败/确需操作才通知。电脑及桌面应用需运行；不需要用户守着或为了离线实验一直插相机。不要创建重复自动化。
- 本地当前代码候选默认 `pklnet-illumination-consistent-v5`，固定gamma=.6只影响定位输入。原始v4与gamma预测都运行；两者有效时IoU>=.5才采用gamma，否则保留v4。原始失败而gamma成功可采用后者。最终裁图来自原始像素，原几何阈值不变。显式 `policy="aspect"` 保留v4，`heatmap`保留v3。
- 新工具 `tools/audit_roi_robustness.py` 固定五种对照：新图v4 DoN13/FastCC12，gamma15/15，CLAHE7/8，亮度预测中位11/13，视野预测中位13/12；旧40图所有方案均20/20。随后 `audit_roi_consistency.py` 增加IoU>=.5的保守控制，新图仍15/15，7张回退v4。助手参考IoU<.5数目：v4为6、纯gamma为8、带一致性为6；这仍是重复查看开发集，不能称独立验证。
- DoN相对v4纠正3张，新增错配1张（bankey:left #8，20261020T165527743661Z-bc841602），净增2张。不得说原7张只剩其中5张：有新增错误。最终仍5/20错配。
- PalmIR已实际跑v4、纯gamma、最终consistent三套完整40图，原图/归一化、两端恢复/只恢复查询/50%混合均无增益。最终consistent：DoN15/20、FastCC15/20；配套神经raw14/20、normalized13/20，恢复后都不变。纯gamma的神经raw15/20不可混写为最终consistent结果。使用现有Local PalmIR-style RIA CompactRestorer，不是官方PalmIR；未训练新权重，默认识别不接入无收益恢复。
- `tools/stress_roi_pipeline.py` 固定每组前5张原图录入，后5张查询合成变暗(.65)、原图sigma3模糊、水平+3%/垂直-3%平移。全20查询分母；v4→v5：DoN变暗13→16、模糊14→15、平移7→16；FastCC9→16、17→16、13→16。平移v5仍1张几何失败。合成开发压力测试不是独立现场验证。
- 当前证据根目录 `code/palm_demo/runtime/roi-palmir-20261028/`；最终对照 `consistency-new`，PalmIR `palmir-consistent`，压力 `stress`，旧数据实际HTTP流程 `old-runtime-consistent`（40有效、4录入、20/20、4模拟扣款）。43项相关测试通过。报告生成器 `tools/write_roi_v5_report.py`。
- Pi纯gamma候选已跑通，证据 `pi-gamma/`。最终consistent候选在 `/home/fyp5/roi-v5-consistent-candidate-20261028/`，回放输出 `/home/fyp5/pipeline-roi-v5-consistent-20261028/`。本段记录时仍在候选验收；部署是否完成以本证据目录 `deployment.json` 和后续记录为准，不把纯gamma回放当最终版。
- 下一步优先：更多身份/新会话的独立验证、录入和查询条件不一致的固定压力测试、几何合法但掌区偏移的指缝定位。若做恢复训练，先确定相机真实退化再设计训练；不能在这40张训练后用同批数据宣称泛化。保留原图、生产账户余额和capture-only模式；Pi单核避免欠压。

## 本轮最终验收和部署（覆盖上段候选状态）

- 用户随后明确要求**现在持续迭代，不要每小时调度后停工**。已删除 `roi-palmir` automation（工具确认deleted）。不得重建或把工作推迟到定时任务。先前报告中的每小时安排已失效，应在下次报告更新时删除。

- 最终consistent v5已在Pi完整回放并部署。Pi实际HTTP DoN **14/20**，FastCC15/20；几何40/40、录入4/4、模拟扣款4笔，重复和取消确认均拒绝，原图哈希不变。单核median3.162s/p95 6.223s，throttled=0x0。默认版本 `pklnet-illumination-consistent-v5`，服务重启正常、保持capture-only等待相机。
- 本地最终实际HTTP仍15/20；Pi多错的查询为 `20261020T165631315754Z-64b36032`（stephen:left）。所有40张坐标max差0.001923px，归一化ROI平均绝对像素差0.250269/255。把Pi保存的ROI交给本地DoN得到14/20，证明差异在ROI像素生成上游而非HTTP/matcher选择。尚未分清JPEG解码、颜色转换、透视插值具体贡献。`backend-parity.json`保留逐图与分数证据。下一轮可隔离这些环节，但不要只为这张近乎平分样本改阈值。
- Pi相对v4 DoN13→14、FastCC12→15；不是Pi15/20。最终仍6/20查询错误。本地纠正3/新增错1仅适用于本地；报告已分开。纯gamma的Pi15/20为历史候选，因几何跳变更大未选为最终默认。
- 备份位于 `/home/fyp5/maintenance-20261028/` 下，精确路径与已核对文件SHA见 `runtime/roi-palmir-20261028/deployment.json`。实际结果 `pi-consistent/summary.json`，Pi40张归一化ROI已取回 `pi-consistent/roi_pixels/`。本地最终完整回放 `new-runtime-consistent/` 与 `old-runtime-consistent/`。中文报告 `runtime/roi-palmir-20261028/report.html`。

## 正在继续的定位/匹配实验

- `audit_warp_stages.py` 已隔离跨平台差异：40张JPEG解码RGB完全相同，透视矩阵max差1.7e-12；但同坐标的OpenCV uint8透视后RGB有32397个通道值差1，灰度9390个像素差1，归一化mean差0.2299/max16。主要差异来自透视插值量化，不是JPEG或匹配器。证据 `warp-pi`、`warp-local`、`warp-stage-comparison.json`。
- 新建实验采样器 `roi_sampling.py`，保留浮点灰度的NumPy四角双线性采样；4项测试通过。冻结Pi坐标本地比较 `sampling-new`：OpenCV u8 DoN15/FastCC14；float OpenCV、float NumPy、rounded NumPy均14/14。没有识别提升，**未接入运行默认/未部署**。Pi采样对照因SSH banner EOF未开始；不是需要用户介入的阻塞，可继续本地。
- `audit_pose_matching.py` 固定9种旋转±12度和尺度.85/1/1.15，所有身份同规则，从原图扩展取像素。新图full-context median：DoN15，FastCC17。若仅变换现有128 ROI、反射补边则DoN14/FastCC14，不能混报full-context成绩。其二进制相关实现快速DoN距离与原实现10个随机/真实对照max差2.8e-17，只用于审计，不改变运行代码。
- 现有5模板取median可能受ROI偏移模板影响，附加统一聚合对照：现有ROI无pose DoN nearest16；ROI pose+nearest17；FastCC ROI pose+best3均值16。旧40图这些对照均20。属于开发集探索，尚无新默认版本。当前继续跑full-context的逐模板距离以检查这一假设。证据 `pose-new`、`pose-roi-new`、`pose-roi-old`、`pose-full-template-new`。
- 后续算法重点仍为相机域指缝定位与独立新会话验证；旧数据20/20是短时开发集排序，不是人群准确率或陌生人接受阈值。恢复默认不启用。未改科学训练队列。

## 2026-10-28：九姿态候选与新旧相机稳定性审计（本地，未部署）

- 用户要求现在持续修复并检查新旧数据稳定性；每小时 `roi-palmir` 自动任务已删除，不重建。最新报告 `code/palm_demo/runtime/roi-palmir-20261028/stability/report.html`，旧部署报告已有入口且删除自动跟进陈述。
- 可选 `FastCCPoseNearest-v1` 已接入 `pose_matcher.py`、两个 biometric loader/score hook、debug_ui 的全图上下文特征提取及 replay 的 `--demo-matcher`。固定九姿态（0/±12度、.85/1/1.15），每身份同规则，查询各姿态与录入原始ROI比较、五模板nearest聚合。非法可选姿态用-1，不是零特征。独立版本标识，旧模板不能混用，默认DoN不变。
- 本地真实HTTP候选新18/20、旧20/20，各4组录入与4笔隔离模拟支付；原图/生产账户不变。`pose-http-new` / `pose-http-old`。相关31项测试及存储/支付等21项测试已通过，计数重叠不可相加。候选未部署Pi。Pi最新已部署仍v5 ROI+DoN，实际14/20。
- 80张原图hash唯一且保留，全80×80距离、完整特征和逐样本分数在 `stability/`；元数据显式映射旧日期后缀为同一标签。新旧各5张重复提取特征完全一致，但这不是跨拍摄条件稳定。
- 十种固定随机5/5划分：新候选15–18/20，mean16.7；DoN13–17，mean15.1；FastCC13–18，mean15.7。新反向划分候选16、DoN18、FastCC17，存在退步。旧数据原/反/全部随机均20/20。重复划分仍是同40图，不是200个独立样本。
- 跨相机：旧录入→新后5查询候选6/20，反向10/20；查询全另一批40图分别14/40、16/40。不能称已稳定，更不能把18/20作为现场可靠性。全局四方向×镜像×反色共16变换控制，old→new DoN最佳10/FastCC9；new→old DoN最佳8/FastCC10，未发现统一变换可解决。没有据此改标签。`cross-orientation/`。
- 固定混合录入控制（查询永远各批6–10、录入仅1–5）：旧3+新2模板，候选旧20/20、新固定17，十种随机新8–17；旧2+新3，旧20、新固定18，随机新9–18。旧5+新5也只新15/20。异域模板带来竞争错配，不采用为修复；10模板只是审计，未改五张录入应用。`mixed-enrollment/`，工具 `audit_mixed_camera_enrollment.py`。
- 九姿态候选合成stress：dark19/20、blur17/20、shift16/20（含1几何失败）。25姿态更宽搜索退步，128裁图补边变换也差，不采用。不能把这些开发扰动视作独立采集验证。
- Pi现网络路径经tun0/VPN，SSH banner失败。没有弱化主机指纹验证，没有继续反复认证，也不以此阻止本地工作。服务最后已知保持capture-only；无本轮实时相机或Pi候选验收。
- 当前判断：优先修跨拍摄条件的同掌区定位/对齐，随后独立新会话验证。当前两个被反复检查的人的照片只能作开发证据。不要启用未校准自动拒绝阈值、身份特定ROI或数据标签变更。

## 2026-10-28：用户收窄为单设备，已实现自动局部对齐候选

- 用户明确说 cross device 不用管，只要单device。后续勿再拿跨设备失败作为当前demo验收标准。只在每个设备内分别划分录入与查询。
- 错误集中：原十随机+正反向共12划分中，bankey:left #1错8/8，stephen:right #6错7/7，stephen:left #1错7/8，stephen:right #5错6/6，bankey:right #8错6/8。重复计算不是随机；同照片落在不同录入/查询侧、模板覆盖变化导致15–18波动。
- 原v5框对已有助手参考框，bankey:right #8 IoU .164，边长比.452，中心偏移.368个参考边长；stephen:left #1 IoU .324、边长比.631；stephen:right #5 IoU .440、边长比.677。参考为开发标注非独立GT。只换固定参考ROI而保留FastCC median：原19、反19、十随机18–20(mean18.9)；参考nearest原/反20、随机17–20(mean19.5)。不能叫自动成绩。
- 已完成自动修复 `registered_matcher.py`：可选 `FastCCRegisteredBest2-v2`，仍用自动v5 quad。原图384ROI上RootSIFT，原始与Gaussian sigma2两个描述子视图；双方比率.85、互为最近邻，partial-affine RANSAC3px、≥4内点、面积≥.02、scale .5–2、角度≤40。通过时从原始灰度上下文对齐后重新计算FastCC；最终识别像素不平滑。原图或768上下文越界则保留九姿态距离。身份score为五模板中best2均值，所有身份同规则，无标注/身份路由。v1保留单描述子控制。
- 两个biometric loader已接入v1/v2，原debug_ui全图context hook复用，deploy清单加入registered_matcher.py。默认DoN未改、Pi未部署。独立uint8固定格式，v2每样本未压缩1,639,136bytes，压缩NPZ保存，包含掌部灰度上下文和描述子，按生物模板保护。版本隔离、旧模板须重录，账户余额保持。
- **最终v2实际运行特征保存/重载、全部3200同device距离**：新原20/20(原候选18)，反18(原16)，原十随机17–20 mean18.3(原15–18 mean16.7)；另100固定seed2026102900:2026103000，新16–20 mean18.65(原15–20 mean17.28)，83组改善16持平1退步。旧所有112划分都是20/20。新增划分仍同40图，绝非2000独立验证样本。
- **实际HTTP完整回放v2** 新20/20、旧20/20，各4录入、4隔离模拟支付，原图hash保持。相机边界为历史图，ROI/算法/模板/交易执行真实代码。分别 `single-device/http-v2-new`、`http-v2-old`。没有实时相机或Pi验收。
- 未采用的对照均保留：纯SIFT计数比现有差，汇总/双向矩阵只小改善；单sigma2新十随机16–20、额外100 mean18.61；单sigma4十随机17–20 mean17.8。最终双视图同规则融合比单视图更稳。runtime-v2实际分数复现双视图离线组合结果。
- 27项测试通过（registered/pose/gallery/templates/payment/capture-only），包含格式损坏/版本隔离、无对应回退、几何分布约束、原图越界保护、best2 hook、模板保存和重提特征确定性。本机v2特征提取median180.9ms，不含ROI；每对匹配median9.96ms；不是Pi时延。
- 最新报告 `code/palm_demo/runtime/roi-palmir-20261028/single-device/report.html`。原stability报告已在开头链接新单设备报告，保留历史跨设备证据但不是目标。新图40张ROI总览roi-grid.jpg，error-diagnosis.json，runtime-v2/results.json含224个划分每种算法逐样本分数/录入列表。原图80hash、查询不在gallery、同device范围、分母、报告链接已校验。
- 新工具 `audit_local_alignment.py`、`audit_registered_matching.py`、`audit_registered_runtime.py`、`audit_alignment_smoothing.py`、`write_single_device_report.py`。可部署补丁 `single-device/single-device-v2-patch.zip`，manifest逐文件SHA验证；需现有v5模型/依赖，不含原图/凭据。未直接部署当前VPN路由不可达Pi。
- 剩余：严重小框/对应不足的个别样本仍错，最低16/20，不能宣称完全稳定。下一步可继续针对自动ROI定位/同设备新会话验证；不要为改善表面成绩删除难图、强加质量门槛、改标签或扩大回跨设备任务。

## 2026-10-28：原生图片核对、多ROI v3与额外窗口实验

- 用户要求具体看图片。已检查 image-review/bankey-right.jpg、stephen-left.jpg、stephen-right-native.jpg。主要是自动ROI过小偏指根。右手#5原生主纹仍在，不能凭放大ROI断言失焦。背光低对比存在于成功/失败样本，不能单独解释错误。参考框仍为助手开发估计。
- 新可选 FastCCMultiROI-v3 已实现，保留原图/gamma两有效定位，384/768字段×sigma0/2局部对应，原生灰度一次重采样，v2回退；独立8.16MB模板。两个loader/debug_ui/deploy接入，默认DoN未动、Pi未部署。native crop header边界验证已加入。
- 实际运行保存/重载v3：新original20、reverse19、十随机19–20 mean19.8、额外100 18–20 mean19.92；旧全部20。真实本地HTTP新旧各20/20、4录入、4模拟支付；80hash/同设备/查询不在gallery已复核。44项相关测试通过。report-v3.html/verified-v3.json保存证据。
- 对照全保留：wide-context改善bankey右8从51/63错到0；dense-alignment(ECC)无增益，grid-alignment(LK)无增益；wider-field无增益；palm-coverage直接大框回退；coarse-structure小幅增益。roi-hypotheses解决stephen右5全部53/53错误，剩左1错10/51、右6错1/52。
- tools/audit_localizer_windows.py固定三个4:3窗口原图/gamma预测；所有有效候选统一使用，无身份选择。audit_roi_hypotheses.py --candidate-file 支持上述候选。window-hypotheses：新original/reverse/十随机全20；额外100为99组20、一组19（mean19.99），旧全部20。解决左1全部剩余错误。唯一错为stephen右6 seed2026102984，真身份距离.373535，错身份stephen左.370605。
- tools/audit_hypothesis_union.py 将window-hypotheses与既有coarse-structure几何验证距离统一min，再用原best2；**新旧各112个原定划分全20/20**。无改标签、删图、按身份选分支、修改划分。原始/反向/10seed/100seed均保留。但仍是反复查看过的80图开发实验；不是独立验收。
- window-coarse-union方案只离线验证，尚未集成到v3运行提取流程；不能把全20离线分数称作v3/现场/Pi成绩。下一步若继续demo落地，应版本化集成窗口定位及粗尺度描述子，复测存储重载/HTTP/计算成本，再新会话验收。当前Pi不可达，不重复认证或变更capture-only服务。
- 新报告工具write_multiroi_report.py生成single-device/report-v3.html，旧report.html/v2补丁保留。仍未创建新定时任务/新线程/子代理。

## 2026-10-28：联合方案已接入可选v4，并完成运行与重新推理验收

- 延续授权：审计union/base_full差异、接入通用运行方案、复测完整协议和HTTP；禁止部署Pi或改网络。无新线程/子代理/自动任务。
- 新union_matcher.py / window_roi.py，算法FastCCWindowUnion-v4；原图/gamma原候选sigma0/2/4/8，固定3个4:3窗口各原图/gamma候选sigma0/2，384/768搜索。录入描述子只主ROI，统一RootSIFT几何验证，原生无损灰度一次采样，min候选+v2回退，身份best2。原expanded_strict分支完整保留；base_full未隐式加入。两个loader/debug_ui capture hook/deploy源清单已接入。原默认DoN、Pi服务不改。
- 新docs/ROI_PIPELINE.md解释各阶段和版本差异。16MiB固定uint8模板容量，变量有效载荷含v2、原生灰度PNG、实际数量描述子；溢出报错不删候选。版本隔离、无pickle、PNG尺寸与视图边界检查。新增4项tests/test_union_matcher.py；共48项相关测试通过。
- union-audit.json：80原图hash未变，224固定划分(每设备112)完全一致。v4缓存定位运行特征保存/加载后的3120非自身同设备配对，与离线window-coarse-union距离**逐对完全相等**。base_full单独对照比v2改善210配对，仍有5配对比union低，最大差.0009765625；未为凑结果纳入。
- audit_union_fresh_features.py重新ONNX定位：76/80模板完全相等，4张新图有微小定位/描述子差异，原像素与v2底模板核对未变。fresh-v4保存差异模板；audit_union_fresh_distances.py重算所有涉及它们的300有向配对，只复用两端模板均逐字节相等的其余配对。runtime-v4-fresh中**新旧各正反、原十随机、额外100随机全部20/20**。
- 真实本地HTTP历史图回放http-v4-new/http-v4-old各20/20、4录入、4隔离模拟支付，原图hash保持。不是现场相机/Pi测试。此前v2/v3及失败实验全保留。
- 资源：压缩NPZ单模板median5,439,208.5bytes、max7,063,675、80张total430,543,827；未压缩16MiB。并行开发测试时cached几何提取median1378ms、pairmedian138ms；fresh定位+提取median3712ms/p956025；HTTP新图identify median9998ms/p9513640，旧图median4754ms。批量80模板工具进程曾测peak约1.6GB。均非隔离性能基准、非Pi承诺；交互demo目前仍慢，优化需要保持原协议与分数一致。
- report-v4.html为最终报告，resource-v4.json/union-audit.json/完整逐样本结果为证据。tools/write_union_report.py可复现；tools/package_union_patch.py生成版本化源补丁并逐文件SHA验证。没有独立新会话/陌生人拒绝率/泛化证明，不可宣称产品完全稳定。
