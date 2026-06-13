#!/bin/bash
# ai-paint 同步到服务器
set -e

HOST="119.28.43.97"
USER="ubuntu"
PASSWORD="@Zzg12-12-12-"
LOCAL="/root/.openclaw/workspace/ai-paint"
REMOTE="/var/www/paint"

echo "📦 同步前端..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
  "$LOCAL/frontend/index.html" \
  "$USER@$HOST:$REMOTE/frontend/"

echo "📦 同步后端 (config.py 除外)..."
for f in app.py db.py ai_api.py; do
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
    "$LOCAL/backend/$f" \
    "$USER@$HOST:$REMOTE/backend/"
done

echo "🔄 重启服务..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "sudo systemctl restart ai-paint"

echo "✅ 同步完成！"
