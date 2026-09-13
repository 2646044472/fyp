#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "请使用 sudo 运行：sudo ./enable_ssh_remote.sh" >&2
  exit 1
fi

if ! command -v sshd >/dev/null 2>&1; then
  echo "系统没有 OpenSSH Server。需要联网一次安装："
  echo "  apt update && apt install -y openssh-server"
  apt update
  apt install -y openssh-server
fi

systemctl enable ssh
systemctl restart ssh

PI_USER="${SUDO_USER:-$(id -un)}"
echo
echo "SSH 已启用。"
echo "Pi 用户名：$PI_USER"
echo "Pi 地址："
hostname -I | tr ' ' '\n' | sed '/^$/d'
echo
echo "在电脑 PowerShell 测试："
echo "  ssh $PI_USER@<上面的IP地址>"
echo "不要把密码写入脚本或发到聊天里。"
