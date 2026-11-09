# 演示预览严格质量门控（2026-11-09）

## 问题

`/demo` 的自动采集前置检查之前使用诊断型 `quality_status`。该 gate 的对比度/清晰度下限为 0，因此低质预览仍可能被标成 READY，随后才在高分辨率抓拍处理失败。

## 改动

- 保留原诊断 gate（min contrast/sharpness 均为 0），继续向 debug/诊断页报告状态。
- 增加演示专用 gate：连续 5 帧、contrast ≥ 12、sharpness ≥ 2，并沿用 ROI 新鲜度和几何稳定性判断。
- `/demo` 浏览器控件和服务端抓拍前置检查优先使用 `demo_quality_*` 字段；缺少新字段的测试替身仍走旧字段兼容路径。
- 低清晰度、低对比度和不稳定掌区显示可执行提示。服务端未就绪时在高分辨率抓拍前返回 WAIT/RETRY，不增加采集失败预算。
- 质量值由同一处理后的 128×128 灰度 ROI 计算。阈值与仓库已有 `pklnet_policy.require_matchable_quality`、`EnrollmentPhotoSelector` 一致；这只说明测量域和现行阈值复用，不代表真人可用性已验证。

## 验证

X 主机，无真人掌纹输入：

- `tests/test_roi_quality.py` 与 `tests/test_pklnet_no_hand_normalization.py`：31 passed。
- `node tests/test_demo_page.cjs`：交互检查通过，含诊断 READY 但演示质量失败时保持禁用、显示模糊提示、且动作不触达服务端。
- Python `py_compile`：通过。

## 限制

相机当前没有手掌可供真人验收；本轮未做实时光线/模糊阈值调整、Pi 摄像头或识别端到端耗时测量。此 gate 是可回滚的体验保护改动，不能算识别准确率提升。

## X UVC 无手实机检查补充（2026-11-09）

- X 上 `/dev/v4l/by-path/pci-0000:00:14.0-usb-0:6:1.0-video-index0` 映射到 Integrated Webcam HD；只读预览脚本在 640×360 连续运行约 4 秒，10/10 状态为 NO_HAND，捕获约 30.2–30.3 fps、检测 24.9–29.5 ms。脚本不含录入/识别路由，不写帧。
- 主 `/demo` App 在 X 上以 `--camera-backend uvc --roi-mode pklnet --enable-recognition` 启动，监听仅限 `127.0.0.1`；`/api/status` 十次均为相机就绪、ROI新鲜、诊断和严格 gate 都是 NO_HAND，0/5 连续就绪。`GET /demo` 返回新页面。
- 对该隔离实例发 1 次空场景 `POST /api/demo/identify`，返回 `RETRY/NO_HAND`，无分数/ROI图像。源码路径在 gallery 之前先执行 live gate；因此没有图库比对或身份分数。响应里 `gallery` 计时约 0.225ms 是 gallery-integrity 检查，不是匹配计算。隔离 runtime 的 users/accounts/transactions 均为 0。
- 主 App 首次启动暴露 `.venv-pklnet` 缺少仓库 `requirements-dev.txt` 已声明的 `scipy>=1.14`；仅在该 venv 使用 `uv` 安装 scipy 1.18.1，未改依赖清单。隔离 runtime 位于 `/tmp/codex-palm-demo-nohand-uvc-v2-20261109`；没删除它。App 和预览服务都已正常退出。
- 这只证明当前空场景及本地 API 的安全阻断，不是真人 READY 录入/识别、Pi 验证或准确率结果。
