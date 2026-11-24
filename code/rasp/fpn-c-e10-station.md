# FPN + C E10｜60 秒独立采集站

这是 **原生 PyTorch** 采集与验证入口，使用冻结 FPN 裁掌和 C E10 特征。8080 展示本机照片库、最高匹配候选和演示判断。真实相机上的识别阈值仍待校准。

## 启动前

1. 跟 [原生依赖与本机清单](fpn-c-e10-shadow.md) 准备独立 Python 环境，运行预检。两份模型均须来自获准的本机来源且 SHA-256 与可信的原版清单一致。代码库不含模型、填写后的清单、数据或模板。
2. 腾出相机。确认旧 8088 服务没有登记正在进行、也不再占用要测的相机，再在 Pi 上或连接该相机的 Linux 开发机运行。此入口不会擅自终止其他程序，也不要让两个进程同时控制一台相机。
3. 选一个**新的 0700 私有目录**，不得使用旧采集或模板目录。服务运行时用模型摘要锁定这套模板；换了模型，使用新的目录重新登记。不要把模板或清单提交到 Git。

```sh
mkdir -m 700 -p "$HOME/.local/share/fpn-c-e10-v3-local"
python fpn_c_e10_station.py \
  --manifest /PATH/TO/LOCAL/manifest.json \
  --runtime "$HOME/.local/share/fpn-c-e10-v3-local" \
  --uvc-device /dev/v4l/by-id/YOUR-CAMERA-video-index0 \
  --uvc-native-size 2592 1944
```

以上在 `code/rasp/` 内运行。UVC 参数必须指向本机真实 Video Capture 设备，`--uvc-native-size` 必须是 `v4l2-ctl --list-formats-ext` 列出的 MJPEG 尺寸。指定后保留相机原始 JPEG，实时预览与识别使用 640×480。用 CSI 时省略两个 UVC 参数，如需要可加 `--csi-tuning /PATH/TO/LOCAL/tuning.json`。主进程首次加载依赖/模型，然后开相机；设备不适配时非零退出，不默默换回旧模型。服务只绑定 `127.0.0.1:8080`，不要暴露到 LAN/公网。

## 登记与分数验收

- 打开 [8080 登记界面](http://127.0.0.1:8080/enroll)，页面标明 **FPN + C E10**。[`/station-health`](http://127.0.0.1:8080/station-health) 显示 `backend: fpn-c-e10-frozen`、`mode: scores_only` 和设备就绪；`ready: true` 不代表任意一帧可用于登记。相机预览独立运行，FPN 只处理最新待用帧；过时不复用（如状态出现 `fpn_frame_stale`，要查 Pi 实际推理耗时）。
- 从 Yesand 连接时，本机和 Pi 都用 8080。运行 `ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8080:127.0.0.1:8080 PI_SSH_ALIAS`，把 `PI_SSH_ALIAS` 换成自己的 Pi SSH 别名。用 `/station-health` 确认后端后，打开同一个登记地址。
- 服务端从开始采集计时，最多 60 秒。补拍沿用本轮截止时间，采集结束后可以继续复核。确认后，选出的 10 组全部进入照片库。首次登记用排序前 5 组建验证模板。相同编号、同一只手再次采集时，新增照片记录并沿用已有验证模板。
- 采集页和[照片库](http://127.0.0.1:8080/collect)都可放大查看相机原图、从同一曝光裁出的高清 ROI 和实际用于识别的 128×128 ROI。原图可切换四边形标记。移除待确认候选后可补拍缺额。确认保存后，图像位于 `--runtime` 目录下的 `enrollment_pairs/<归档 ID>/`，每组带尺寸和配对清单。
- [放掌验证](http://127.0.0.1:8080/gate) 检测到稳定掌区后自动比对。每个掌模板取 5 个样本中的最大余弦作为分数。最高分达到演示阈值 **0.80** 且无并列时，页面显示「匹配」。阈值可用 `--match-threshold` 设置，等待本机同掌与陌生掌采样后校准。页面展示最高候选的编号、显示名、左右手和该样本的登记 ROI。移开手后可再验证。
- 在授权实拍中检查登记、复核、删除补拍、刷新状态、明确保存以及移开手后新鲜分数。测试 CPU 内存、连续帧和处理时延。这个分数路线还不能加载旧模板，也不能拿旧系统的阈值上线。

合成测试（无真实相机、模型、掌纹）：

```sh
python verify_fpn_c_e10_station.py
```

用程序生成的像素和替代模型，跑实际 V3 HTTP 登记、同帧两图、删除补拍、手动确认、异版本模板拒绝和地址／路由边界。真实 PyTorch 模型结构的合成测试是单独的 `verify_fpn_c_e10_native.py`。
