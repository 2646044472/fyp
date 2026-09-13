# 无屏启动树莓派

你没有 HDMI 线也没关系。第一次启动就用电脑远程控制。

## 电脑上做

1. 下载并打开 Raspberry Pi Imager：
   https://www.raspberrypi.com/software/
2. 把 64GB SD 卡插入电脑。
3. 选择系统：`Raspberry Pi OS Lite (64-bit)`。
4. 选择 SD 卡后，点右下角的设置/自定义。
5. 填写这些内容：

   - 主机名：`palm-pi`
   - 用户名：自己设，例如 `bankey`
   - 密码：自己设，记住但不要发到聊天
   - Wi-Fi：填写你现在电脑所连 Wi-Fi 的名称和密码
   - 国家：选中国
   - Remote Access：打开 `Enable SSH`，选 `Use password authentication`

6. 点击写入。完成后安全弹出 SD 卡。

## Pi 上做

1. **断电状态**下插入 SD 卡、接好散热和相机。
2. 接上电源开机。
3. 等 2 分钟，让它自动连接 Wi-Fi。

不需要显示器、键盘或鼠标。

## 电脑连接 Pi

打开 Windows PowerShell：

```powershell
ssh 你设置的用户名@palm-pi.local
```

例如用户名是 `bankey`：

```powershell
ssh bankey@palm-pi.local
```

第一次问是否连接时输入 `yes`，然后输入你在 Imager 设置的密码。密码不会显示字符，正常。

连接成功后，电脑终端中显示的就是 Pi 的终端。

如果 `palm-pi.local` 连不上：

1. 确认电脑和 Pi 是同一个 Wi-Fi。
2. 等待 2 分钟后重试。
3. 在路由器管理页查看新设备的 IP，然后执行：

   ```powershell
   ssh 你设置的用户名@192.168.x.x
   ```

## 安装 USB 包

SSH 连上之后，插入含 `palm_demo_pi.zip` 的 U 盘到 Pi，再在电脑 PowerShell 的 SSH 窗口执行：

```bash
ls /media/$USER
cp /media/$USER/*/palm_demo_pi.zip ~/
unzip ~/palm_demo_pi.zip -d ~/palm_demo
cd ~/palm_demo
chmod +x install_usb_offline.sh
./install_usb_offline.sh
```

如果 `unzip` 不存在，Pi 需要联网一次：

```bash
sudo apt update
sudo apt install -y unzip python3-picamera2
```

## 之后

每次只要 Pi 开机并连到同一个 Wi-Fi，电脑执行：

```powershell
ssh 你设置的用户名@palm-pi.local
```

官方参考：https://www.raspberrypi.com/documentation/computers/getting-started.html
