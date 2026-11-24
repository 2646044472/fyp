# 树莓派掌纹采集站（rasp）

如需了解当前登记取帧时限、候选排行与双图复核，请看 [60 秒登记与排查](capture-60s.md)。

这是 FYP 的 **Pi 5 本地采集界面与部署代码**，不是独立识别模型。它使用已有的 **PKLNet + FastCC v6**，不包含 X 上的 FPN+C E10，不修改验证阈值。照片、ROI、登记模板、采集记录和模型文件均不随此目录分发。

| 页面 | 能做什么 |
| --- | --- |
| `/enroll` | 连续预览，从有效 ROI 中挑出清楚、互补的五张；可放大原图和 ROI、删掉某一对及其候选特征、只补缺额。点击「确认同一只手并保存」才提交。 |
| `/gate` | 放掌后自动试一次；移开后再开始下一轮。 |
| `/collect` | 在 Pi 本机管理采集记录。 |

每次登记从按下「开始」起最多 60 秒（服务端 59 秒取帧上限，含补拍）。凑齐五张后也会短暂浏览已有候选，正常可提前结束；不足五张时可预览已有的。程序不保存整段视频。

开发新基线：另有以原生 PyTorch 运行的 [FPN + C E10 60 秒独立采集站](fpn-c-e10-station.md)（8089）。它使用 V3 登记和复核、另存模板且只显示分数。也可先用 [独立命令行](fpn-c-e10-shadow.md) 做本机预检。以下 8088 的现有服务和回退步骤不变；新入口尚未在 Pi 实拍验收。

## 换一台电脑开发

如果尚未克隆，可以只检出应用代码，跳过仓库历史数据目录：

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --sparse https://github.com/2646044472/fyp.git
cd fyp
GIT_LFS_SKIP_SMUDGE=1 git sparse-checkout set code/rasp
cd code/rasp
```

在已有克隆中更新 `main` 即可。逻辑和回归测试在普通电脑用 Python 3 运行，不需要 Pi、模型、相机或真实样本：

```sh
python3 verify_best_frame.py
python3 verify_review.py
python3 verify_ranked_window.py
python3 verify_adapter.py
bash -n install-on-pi.sh && bash -n rollback-on-pi.sh
```

- `capture_station.py` 提供三页、用户服务的入口和采集站请求处理。
- `enrollment_best_frame.py` 连接基础识别程序；`ranked_window.py` 选帧；`enrollment_window_adapter.py` 管开始、超时、停止与补拍；`enrollment_review.py` 管本次待确认的原图和 ROI。
- `palm-capture-station.service` 是 **用户** systemd 单元；`palm-capture-station.env.example` 是无机器信息的相机配置模板。

## 部署到 Pi 5

基础应用的配置、依赖、回退方法见 [识别引擎说明](ENGINE-README.md)。采集站服务假定 Pi 上已有 `${HOME}/palm_demo`、该目录可用的 `.venv/bin/python`，以及可用的 PKLNet/FastCC v6 本地模型。基础引擎源码也在本目录。新建 Pi 基础环境时，把本目录中的源码部署至运行目录，不要覆盖已有的本机模型、设置与采集数据。采集站本身不安装基础模型或系统依赖。部署前先在 Pi 上用基础应用的虚拟环境验证导入（此命令不开摄像头）：

```sh
(cd "$HOME/palm_demo" && .venv/bin/python -c 'from palm_app import debug_ui; from demo_flow import enrollment_quality_issue; assert "enrollment_quad" in debug_ui.ProcessedFrame.__dataclass_fields__, "sync compatible camera module before v3 install"')
```

**更新已装采集站**：旧的基础运行目录必须先更新相机代码。先备份本机基础应用和采集站代码，按上面的基础应用说明更新到兼容的完整源码，并确认上面的导入检查成功；不要用单个基础模块强行覆盖异版。保存或结束所有进行中的登记，然后在 Pi 上进入本目录运行 `bash install-on-pi.sh`。脚本先测试，再备份代码并重启用户服务；页面未恢复时还原。页面响应不等同摄像头就绪，下面仍要实机检查。它不会修改登记或模型；重启会丢失尚未保存的候选。手动回退：`bash rollback-on-pi.sh <安装时打印的备份目录>`。

**全新 Pi（仅克隆仓库不能直接运行）**：先准备基础引擎、相机依赖和已获准的模型。确认以下两项，再把采集站装为用户服务：

1. 服务实际运行的是 `$HOME/palm_demo/.venv/bin/python`，不是 `.venv-pklnet`。该环境需要能导入 `onnxruntime`，以及基础引擎所需的 OpenCV、NumPy、Pillow 和相机依赖。旧 `deploy/install_pi.sh --with-pklnet` 只给另一个环境安装 PKLNet 依赖，不能代替这项检查。
2. 从已获准的本地来源准备匹配的三件套：`net_params_500.pth`、`pklnet-keypoints-diagnostics.onnx` 和 `pklnet-keypoints-diagnostics.json`。三件套放在与 `$HOME/palm_demo` 并列的 `pklnet/`（若该目录存在会优先使用），或放在应用目录内的 `pklnet/`。引擎会校验 JSON 中的原始权重及 ONNX 摘要。旧导出教程中的 `pklnet-keypoints.onnx` 不是当前默认裁掌策略所用的诊断版，不能替代。未经许可不要通过 Git 或共享附件转发模型文件。

基础应用和上述依赖就绪后，在 Pi 上从本目录放入代码及服务（用户权限即可）：

```sh
install -d -m 700 "$HOME/.local/share/palm-capture-station" "$HOME/.config/systemd/user"
install -m 600 capture_station.py enrollment_best_frame.py enrollment_review.py ranked_window.py enrollment_window_adapter.py "$HOME/.local/share/palm-capture-station/"
install -m 644 palm-capture-station.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
```

USB 相机用 `v4l2-ctl --list-devices` 核对真实 Video Capture 节点，把稳定的设备路径写入 Pi 本机 `~/.config/palm-capture-station.env`，可参考随附模板；不要把其他机器的设备路径复制进去。CSI 排线应关机后接入，默认走已有高清采集路径；可选连续 CSI 实验模式仅在实机验证过后启用。若以前的 `palm-debug-ui.service` 正在占用同一相机，先在 Pi 上停止旧应用再启动新服务；避免两个服务同时抢占相机。准备好后运行 `systemctl --user start palm-capture-station.service`。开机要不要启动及启动顺序由实际部署决定；本目录不自动修改旧服务或用户登录策略。

旧版 Pi 基础应用可能缺 `enrollment_quality_issue` 或使用不同状态字段。如果导入报错或页面正常但候选一直不能保留，先检查基础应用/采集站版本，不要放宽验证阈值。现场 Pi 的 USB 本机配置与临时兼容补丁未同步，这个目录不能当作现场 Pi 文件系统的逐字备份。

## 现场验收与访问

Pi 本机打开 [登记页](http://127.0.0.1:8088/enroll)。新电脑如果可以通过自己的 SSH 连接访问 Pi，可在新电脑运行 `ssh -N -L 127.0.0.1:8089:127.0.0.1:8088 <用户>@<Pi地址>`，再打开 [本机 8089](http://127.0.0.1:8089/enroll)，不要改成公网监听。站点只监听回环地址。

先确认 `systemctl --user is-active palm-capture-station.service` 返回 `active`，且画面实时更新、不停在等待页。用同意参加的测试编号走一轮：登记预览 → 比对原图与 ROI → 删除一对并补齐 → 手动保存 → 移开手 → 同掌验证 → 再用未登记的掌确认不误通过。浏览器显示的请求时间不含把手举进画面和等到合格 ROI 的时间，不能当作全程响应时间。仓库里的测试只验证软件流程，不证明实际采集、识别准确率或硬件速度。

请勿提交原图、ROI、模板、运行日志、模型、私钥或相机本机配置。
