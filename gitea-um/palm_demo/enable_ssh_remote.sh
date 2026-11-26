#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script with sudo: sudo ./enable_ssh_remote.sh" >&2
  exit 1
fi

if ! command -v sshd >/dev/null 2>&1; then
  echo "OpenSSH Server is not installed. Connect to the internet once to install it:"
  echo "  apt update && apt install -y openssh-server"
  apt update
  apt install -y openssh-server
fi

systemctl enable ssh
systemctl restart ssh

PI_USER="${SUDO_USER:-$(id -un)}"
echo
echo "SSH is enabled."
echo "Pi username: $PI_USER"
echo "Pi address:"
hostname -I | tr ' ' '\n' | sed '/^$/d'
echo
echo "Test from PowerShell on your computer:"
echo "  ssh $PI_USER@<IP-address-above>"
echo "Do not put the password in a script or send it in chat."
