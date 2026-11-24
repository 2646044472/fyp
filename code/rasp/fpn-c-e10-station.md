# FPN + C E10｜60 秒独立采集站

这是可以从新开发机检出的 **原生 PyTorch** 采集入口，不依赖 ONNX。它复用 V3 的登记、限时选帧与同帧原图／ROI 复核，换成冻结 FPN 裁掌和 C E10 特征。旧 `palm-capture-station.service`、旧 8088 和 PKLNet + FastCC 库不变。本入口只展示比对分数，没有身份结论、通过阈值或通行操作；不修改系统服务。Pi 5 的实际相机、速度、内存压力和识别表现**尚未验收**。

## 启动前

1. 跟 [原生依赖与本机清单](fpn-c-e10-shadow.md) 准备独立 Python 环境，运行预检。两份模型均须来自获准的本机来源且 SHA-256 与可信的原版清单一致。代码库不含模型、填写后的清单、数据或模板。
2. 腾出相机。确认旧 8088 服务没有登记正在进行、也不再占用要测的相机，再在 Pi 上或连接该相机的 Linux 开发机运行。此入口不会擅自终止其他程序，也不要让两个进程同时控制一台相机。
3. 选一个**新的 0700 私有目录**，不得使用旧采集或模板目录。服务运行时用模型摘要锁定这套模板；换了模型，使用新的目录重新登记。不要把模板或清单提交到 Git。

```sh
mkdir -m 700 -p "$HOME/.local/share/fpn-c-e10-v3-local"
python fpn_c_e10_station.py \
  --manifest /PATH/TO/LOCAL/manifest.json \
  --runtime "$HOME/.local/share/fpn-c-e10-v3-local" \
  --uvc-device /dev/v4l/by-id/YOUR-CAMERA-video-index0
```

以上在 `code/rasp/` 内运行。UVC 参数必须指向本机真实 Video Capture 设备；用 CSI 时省略 `--uvc-device`，如需要可加 `--csi-tuning /PATH/TO/LOCAL/tuning.json`。主进程首次加载依赖/模型，然后开相机；设备不适配时非零退出，不默默换回旧模型。服务只绑定 `127.0.0.1:8089`，不要暴露到 LAN/公网。

## 登记与分数验收

- 打开 [8089 登记界面](http://127.0.0.1:8089/enroll)，页面标明 **FPN + C E10**。[`/station-health`](http://127.0.0.1:8089/station-health) 显示 `backend: fpn-c-e10-frozen`、`mode: scores_only` 和设备就绪；`ready: true` 不代表任意一帧可用于登记。相机预览独立运行，FPN 只处理最新待用帧；过时不复用（如状态出现 `fpn_frame_stale`，要查 Pi 实际推理耗时）。
- 从 Yesand 连接时，另选一个未占用的本机端口。旧 README 的「本机 8089 → Pi 8088」仍是 PKLNet + FastCC，不是本入口。示例：`ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8090:127.0.0.1:8089 PI_SSH_ALIAS`（把 `PI_SSH_ALIAS` 换成自己的 Pi SSH 别名）。先打开 `http://127.0.0.1:8090/station-health`，确认 `backend: fpn-c-e10-frozen` 和 `mode: scores_only`，再打开 `http://127.0.0.1:8090/enroll`。
- 从按下「开始」计时，取帧服务端最长 59 秒，页面最多约 60 秒，补拍不重开总计时。得到五张不简单立刻锁定，V3 策略从较好的且相互有帮助的有效帧中选。浏览器、相机或系统资源异常时不能保证总问答延迟；延迟送达的帧不能混进已结束轮次。
- 逐对查看原图和 128×128 ROI，点击可放大。删除某一对会移除同一候选的图和特征，剩余有效图可继续补齐；只有明确点击「确认同一只手并保存」且五张齐全才写入独立本机模板。未确认的图不作为持久照片或视频写盘；本入口不实现旧的原图批次归档（如需可复用的全分辨率原图与采集元数据，请另用旧程序的 `/collect`，先停用当前占用相机的进程，不要同时开同一相机）。
- [分数预览](http://127.0.0.1:8089/gate) 手动取一次当前新鲜 FPN 掌区，显示每个掌模板五张取最大余弦后的前两分（不显示身份）。并列如实显示，不给自动判断；陌生掌和同掌都只会得到分数。旧的 identify、confirm、支付、旧模板访问路由在这个服务不可用。
- 在授权实拍中检查登记、复核、删除补拍、刷新状态、明确保存以及移开手后新鲜分数。测试 CPU 内存、连续帧和处理时延。这个分数路线还不能加载旧模板，也不能拿旧系统的阈值上线。

合成测试（无真实相机、模型、掌纹）：

```sh
python verify_fpn_c_e10_station.py
```

用程序生成的像素和替代模型，跑实际 V3 HTTP 登记、同帧两图、删除补拍、手动确认、异版本模板拒绝和地址／路由边界。真实 PyTorch 模型结构的合成测试是单独的 `verify_fpn_c_e10_native.py`。
