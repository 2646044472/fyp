# 不用屏幕：USB-C 直连 SSH

这套做法适用于 **Pi 5 + Windows 电脑 + 支持数据的 USB-C to USB-C 线**。电脑会把 Pi 识别为一张 USB 网卡，你就能 SSH 进去；不需要 HDMI、键盘或路由器。

## 先在电脑做一次

双击运行本目录的官方驱动：

`windows\\rpi-usb-gadget-driver-setup.exe`

按 Windows 安装向导完成即可。驱动装好后，只有接上已正确烧录的 Pi 才会出现新的网卡。

## 烧录 SD 卡（最关键）

1. 在电脑安装或更新 **Raspberry Pi Imager**。
2. 选择最新的 **Raspberry Pi OS Lite (64-bit, Trixie)**。不要选旧的 Bookworm 镜像。
3. 点齿轮设置，填写主机名 `palm-pi`、用户名和密码；同时启用 SSH（密码认证即可）。可顺手填 Wi-Fi，但 USB-C 直连不依赖它。
4. 在同一设置里启用 **USB Gadget Mode / USB 网络模式**。这个选项只在足够新的 Trixie 镜像中出现；找不到就先更新 Imager 和系统镜像，不要用旧镜像继续烧卡。
5. 写入完成后安全弹出 SD 卡。

## 接线和登录

1. Pi 断电状态插好 SD 卡。第一次只测试直连，不接相机。
2. 用 C-to-C 线把电脑和 Pi 的 USB-C 口直连。这个接口也会给 Pi 供电，先不要再插官方电源。
3. 等约两分钟。在电脑 PowerShell 输入：

```powershell
ssh 你设置的用户名@palm-pi.local
```

例如用户名是 `pi`：

```powershell
ssh pi@palm-pi.local
```

第一次会问是否信任指纹，输入 `yes`，再输入你在 Imager 里设置的密码。

登录成功后，把 USB 盘插入 Pi 的普通 USB-A 口，再部署 `palm_demo_pi.zip`。确认 SSH 稳定后，先执行 `sudo poweroff`，等停机后再接相机排线。

## 连不上时

- 先确认线不是“仅充电线”，换另一根数据线试一次。
- 确认系统是 Trixie，且烧卡时已开启 USB Gadget Mode；普通旧镜像不能靠插线自动变成 USB 网络。
- Pi 反复重启、红灯异常或电脑提示 USB 设备断开，说明电脑口供电可能不足。拔线，改用官方电源，再按 Wi-Fi/网线方式 SSH。
- 不要在 Pi 通电时插拔 CSI 相机排线。

官方说明：https://www.raspberrypi.com/news/usb-gadget-mode-in-raspberry-pi-os/
