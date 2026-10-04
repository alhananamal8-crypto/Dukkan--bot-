#!/bin/bash
set -e

echo "==> Creating virtual environment"
python3 -m venv .venv
source .venv/bin/activate

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Preparing .env"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
  echo "Please edit .env and fill in your real Meta/WhatsApp values before testing the webhook."
else
  echo ".env already exists"
fi

echo "==> Starting app in background"
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/dukkan-bot.log 2>&1 &
echo $! > /tmp/dukkan-bot.pid

sleep 5

echo "==> Checking /health"
curl -sS http://localhost:8000/health || {
  echo "Health check failed. Showing recent logs:"
  tail -n 100 /tmp/dukkan-bot.log
  exit 1
}

echo "==> Testing webhook verification endpoint"
VERIFY_TOKEN=$(grep '^VERIFY_TOKEN=' .env | cut -d= -f2- || echo "change-me")
curl -sS "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=${VERIFY_TOKEN}&hub.challenge=hello"

echo ""
echo ""
echo "✅ App started successfully in the background."
echo "Logs: tail -f /tmp/dukkan-bot.log"
echo "Stop it: kill \$(cat /tmp/dukkan-bot.pid)"
echo ""
echo "Next steps:"
echo "1. Edit .env with your real Meta/WhatsApp credentials"
echo "2. Make port 8000 public in the Ports panel (VS Code)"
echo "3. Set Meta webhook URL to: https://<your-public-codespace-url>/webhook"
echo "4. Test by sending: بعت بـ 50 to your WhatsApp test number"
