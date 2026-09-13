# 用电脑远程操作树莓派

## 需要什么

- Pi 已安装 Raspberry Pi OS 64 位。
- Pi 和电脑连接同一个 Wi-Fi，或都接同一个路由器的网线。
- 你知道 Pi 的用户名和密码。
- Windows 10/11 通常已经自带 `ssh`，不需要额外安装软件。

## 第一次启用 SSH

**不需要显示器或键盘。** 用 Raspberry Pi Imager 写入 SD 卡时，填写 Wi-Fi、用户名、密码，并打开 `Enable SSH`。完整步骤见 [HEADLESS_FIRST_BOOT.md](HEADLESS_FIRST_BOOT.md)。

`enable_ssh_remote.sh` 只给已经有本地终端的 Pi 作为备用；无屏首次启动不需要它。

## 在 Windows 电脑连接

打开 PowerShell，执行：

```powershell
ssh pi用户名@192.168.1.35
```

第一次会问是否信任主机，输入 `yes`，然后输入 Pi 密码。密码输入时不会显示字符，这是正常的。

连接成功后，你看到的终端就是 Pi 的终端，可以直接执行：

```bash
cd ~/palm_demo
./run_palm_demo.sh --help
rpicam-hello --list
```

## 从电脑复制文件到 Pi

在 Windows PowerShell 执行：

```powershell
scp C:\Users\bankey\Desktop\code\fyp\code\palm_demo\dist\palm_demo_pi.zip pi用户名@192.168.1.35:/home/pi用户名/
```

如果只是第一次部署，使用 U 盘更简单；SSH 主要用于之后改代码、查看日志和运行命令。

## 远程运行掌纹 demo

```bash
cd ~/palm_demo
./run_palm_demo.sh --authorized-local-biometric --camera 0 --capture-profile rgb enroll --user demo-rgb --samples 5 --interactive
```

相机拍摄仍然发生在 Pi 上。SSH 窗口只显示文字，不能代替相机预览；首次调相机建议接显示器运行 `rpicam-hello -t 0`。

## 安全提醒

- 不要把 Pi 的密码写进脚本、Git、U 盘说明或聊天。
- 不要把 SSH 端口暴露到公网路由器。
- 只在自己的局域网内使用；实验结束可以关闭 SSH：

  ```bash
  sudo systemctl disable --now ssh
  ```

- 如果 IP 变化，重新在 Pi 上运行 `hostname -I` 查看新地址。
- 我不能仅凭 USB 包自动连接你的 Pi；需要你先让 Pi 开机联网，并在当前环境中提供可用的局域网连接信息和授权。
