# FPN + C E10｜独立 CPU 影子检查

这里把 X 上同一构建的 **FPN 自动掌区 + C E10 双分支识别器**接到可单独运行的命令行。它不更换 8088 的已部署服务，不改阈值、账户或已登记模板，不接门禁，也不返回“通过 / 失败”。缺少板端速度与实拍验收，以及代表真实陌生人的拒识校准，所以不把离线名次分数作为门禁放行。

如需在浏览器使用同一模型的 60 秒登记及复核，请看 [独立采集站](fpn-c-e10-station.md)，与这个单次回放入口分开。

## 换电脑先检查代码

从 `code/rasp/` 运行。用独立虚拟环境，别替换正在用的采集站环境。`requirements-fpn-c-e10.txt` 记录 X 的版本组合；这是原生 PyTorch 推理，不需要 ONNX。在目标系统确认对应的 PyTorch/Torchvision **CPU** wheel 后安装，Pi 5 AArch64 的依赖、内存和帧率仍待实机确认。不能把显卡版 X 所用轮子直接复制到 Pi。

```sh
python verify_fpn_c_e10_shadow.py
python verify_fpn_c_e10_native.py  # 已安装完整依赖时
python fpn_c_e10_shadow.py --help
```

命令行合成回归只需要 NumPy 和 Pillow，使用假的模型与人造纯色小图，不需要模型、相机或真实掌纹。

## 仅在已授权设备装入冻结模型

从项目已授权的本机资产来源准备两份**精确发行版** safetensors：自动裁图 FPN 和对应的 C epoch 10。代码库不附模型或校验值。把 [manifest 示例](fpn-c-e10.manifest.example.json) 复制到仓库外，和两份本机模型放在同一个目录。填从可信模型保管方获得的原版摘要（小写十六进制 SHA-256），不是给随手拿到的文件重新生成一个摘要冒充同一发行版。格式、摘要、张量名称与尺寸均严格检查；文件与可信发行摘要不符时停止。禁止提交模型、填写后的清单、样本路径清单和运行输出。

```sh
python fpn_c_e10_shadow.py --manifest /PATH/TO/LOCAL/manifest.json preflight
```

`preflight` 真正尝试在 CPU 装载两份模型，不读图片。缺依赖或检查点时返回非零，不偷偷退回到另一模型。它通过也**不是**板端部署完成，也没说明摄像头画面速度。

## 计算一次分数，不保存或通过

仅在采集条件及协议允许的本机输入上手动运行；预先固定同一掌的 5 张登记照，另一张作独立查询：

```sh
python fpn_c_e10_shadow.py --manifest /PATH/TO/LOCAL/manifest.json shadow-score \
  --query /PATH/TO/LOCAL/query.jpg \
  --enroll /PATH/TO/LOCAL/e1.jpg /PATH/TO/LOCAL/e2.jpg /PATH/TO/LOCAL/e3.jpg \
           /PATH/TO/LOCAL/e4.jpg /PATH/TO/LOCAL/e5.jpg
```

六个文件须不同；文件去重只能挡字节级重复，不能替你核对是不是同一掌或拆分是否独立。所有输入走冻结 FPN，同一 C E10 识别器产生 512 维特征，浮点 64 位重新归一化，再取查询与五张登记的最大余弦。任何一张裁不出来则报告所在阶段，不返回分数、不自动补模板。成功也只打印无姓名的单项分数；不要把分数与参与者编号相连发到 Git 或公共日志。它不是人脸活体检查，也不做身份或通行决策。

现场替换 8088 之前，另须完成：有授权的 Pi 原生依赖和实际内存核验；授权数据上的相机 → ROI → 识别端到端计时；验证器与冻结参考同输入的几何和分数一致；独立陌生掌的拒识校准与真掌漏接验证。如未完成，继续保留原采集服务及自己的本机数据。
