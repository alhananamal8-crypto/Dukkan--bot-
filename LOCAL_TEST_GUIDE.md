# Local Testing Guide for Dukkan Bot

This guide walks you through testing Dukkan Bot in a GitHub Codespace.

## Quick Start (One Command)

In your Codespace terminal, run:

```bash
bash test-codespace.sh
```

This will:
1. ✅ Create virtual environment
2. ✅ Install all dependencies
3. ✅ Copy `.env.example` to `.env`
4. ✅ Start the FastAPI app on port 8000
5. ✅ Test `/health` endpoint
6. ✅ Test webhook verification

---

## Manual Setup (Step by Step)

If you prefer to run commands individually:

### Step 1: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your real values:

```env
WHATSAPP_TOKEN=your_permanent_access_token_here
PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=your_webhook_verify_token_here
APP_SECRET=your_meta_app_secret_here

ANTHROPIC_API_KEY=your_claude_key_here
CLAUDE_MODEL=claude-haiku-4-5-20251001

TZ_NAME=Asia/Riyadh
CURRENCY=ر.س
DB_PATH=/data/shop.db

OPENAI_API_KEY=your_openai_key_here
STT_LANG=ar
LOW_STOCK=5
```

### Step 4: Start the App

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Testing the App

### Test 1: Health Check

In a new terminal:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Test 2: Webhook Verification

```bash
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=change-me&hub.challenge=hello"
```

Expected response:

```text
hello
```

⚠️ If it returns 403, make sure your `VERIFY_TOKEN` matches the one in `.env`.

---

## Testing with Real WhatsApp

To test with a real WhatsApp message:

### 1. Make Port 8000 Public

In VS Code Codespace:
1. Open the **Ports** panel (bottom of screen, or Ctrl+Shift+X)
2. Right-click port 8000
3. Select **Make Public**
4. Copy the forwarded URL (e.g., `https://xxxxx-xxx-xxx-xxx.preview.app.github.dev`)

### 2. Configure Meta Webhook

Go to Meta Developers Console:
1. **WhatsApp > Configuration > Webhook**
2. Click **Edit**
3. Fill in:
   - **Callback URL**: `https://<your-public-codespace-url>/webhook`
   - **Verify Token**: same as `VERIFY_TOKEN` in `.env`
4. Click **Verify and Save**
5. Subscribe to **messages** field

### 3. Send a Test Message

From your personal WhatsApp, send to your test number:

```text
بعت بـ 50
```

Expected bot response:

```text
✅ تم تسجيل بيع 50.00 ر.س
```

### 4. Try More Commands

```text
# Sales
بعت بـ 100

# Expense
دفعت 50 كهرباء

# Customer debt
أحمد أخذ بالدين 200

# Check debt
كم دين أحمد؟

# Report
تقرير اليوم

# Inventory
وصل 20 حليب
كم باقي حليب؟

# Get help
مساعدة
```

---

## Troubleshooting

### "Connection refused" on localhost:8000

- Make sure the app is still running (check the first terminal)
- If it crashed, check logs:
  ```bash
  tail -f /tmp/dukkan-bot.log
  ```

### "403 Forbidden" on webhook verification

- Make sure `VERIFY_TOKEN` in the URL matches `.env`
- Example: if `.env` says `VERIFY_TOKEN=my-secret`, then use:
  ```bash
  curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=my-secret&hub.challenge=hello"
  ```

### "No module named fastapi"

- Make sure you activated the virtual environment:
  ```bash
  source .venv/bin/activate
  ```
- Then reinstall:
  ```bash
  pip install -r requirements.txt
  ```

### Webhook not receiving messages

- Confirm port 8000 is **public** in the Ports panel
- Confirm the callback URL in Meta matches exactly
- Confirm `VERIFY_TOKEN` matches in Meta and `.env`
- Check logs:
  ```bash
  tail -f /tmp/dukkan-bot.log
  ```

---

## Next Steps

Once local testing is complete:

1. **Deploy to Railway/Render/Fly.io** — See `DEPLOYMENT_GUIDE.md`
2. **Set up permanent Meta credentials** — See `SETUP_META_WHATSAPP.md`
3. **Configure webhook for production** — Update callback URL to your deployed domain

---

## Stop the App

When done testing:

```bash
# Press Ctrl+C in the app terminal
# Or if running in background:
kill $(cat /tmp/dukkan-bot.pid)

# Deactivate virtual environment
deactivate
```
