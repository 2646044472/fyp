# USB 离线资源

这个目录可以直接复制到 U 盘，再复制到树莓派。

## 已下载内容

- Fast-CC 源码：已锁定在 `vendor/palmprint-recognition-python`。
- ARM64 wheels：Python 3.11（NumPy 2.2.6、SciPy 1.16.3、Pillow 12.2.0）和 Python 3.13（NumPy 2.3.5、SciPy 1.17.1、Pillow 12.2.0）。
- Picamera2 0.3.37 wheel：仅作备用，不覆盖系统相机库。
- `install_usb_offline.sh`：离线安装 Python 依赖并创建本地虚拟环境。

## Pi 端使用

建议安装 Raspberry Pi OS 64 位 Bookworm。把整个 `palm_demo` 文件夹复制到 Pi，然后执行：

```bash
cd ~/palm_demo
chmod +x install_usb_offline.sh
./install_usb_offline.sh
rpicam-hello --list
```

如果系统提示缺少 Picamera2，只需联网一次安装系统组件：

```bash
sudo apt update
sudo apt install -y python3-picamera2
```

之后 NumPy、SciPy、Pillow 和 Fast-CC 都可从 USB 包离线使用。官方建议 Picamera2 和 `libcamera` 由 Raspberry Pi OS `apt` 配套安装；不要随意用 pip 覆盖系统 Picamera2。

## 运行

```bash
./run_palm_demo.sh --authorized-local-biometric --camera 0 --capture-profile rgb enroll --user demo-rgb --samples 5 --interactive
./run_palm_demo.sh --authorized-local-biometric --camera 0 --capture-profile rgb verify --user demo-rgb
```

NoIR + 红外补光使用另一个 profile 和用户：

```bash
./run_palm_demo.sh --authorized-local-biometric --camera 1 --capture-profile noir-ir enroll --user demo-noir --samples 5 --interactive
```

## 重要限制

- wheels 只适用于 `aarch64` + Python 3.11 或 3.13；不要在 32 位系统或其他 Python 版本上强行安装。
- `Picamera2` wheel 不等于完整 `libcamera` 驱动；相机无法识别时仍需系统 apt 包。
- 这个包不包含研究数据、个人模板或运行日志；它们在 Pi 上运行后才会生成。
- 如果要把包带给别人，先确认里面的数据、视频和模型没有受限授权。

来源：

- https://www.raspberrypi.com/documentation/computers/camera_software.html
- https://pypi.org/project/picamera2/
