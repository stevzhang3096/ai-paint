#!/bin/bash
# ai-paint 一键同步脚本：本地提交 → 推送到 GitHub → 服务器拉取 + 重启
set -e

cd /root/.openclaw/workspace/ai-paint

# 1. 提交本地改动
git add -A
echo "📦 提交信息: $@"
git commit -m "$*" 2>/dev/null || echo "  没有新改动"

# 2. 推送到 GitHub
echo "⬆️  推送到 GitHub..."
git push 2>&1 | tail -2

# 3. 服务器拉取
echo "⬇️  服务器拉取并重启..."
sshpass -p '@Zzg12-12-12-' ssh -o StrictHostKeyChecking=no ubuntu@119.28.43.97 "
  cd /var/www/paint
  git pull
  # 修复 MySQL 配置
  sed -i 's/3306,/3307,/' backend/config.py
  sed -i 's/paint_pwd_2026/paint123/' backend/config.py
  sudo systemctl restart ai-paint
  echo '✅ 服务器已更新并重启'
" 2>&1

echo "✅ 同步完成！"
