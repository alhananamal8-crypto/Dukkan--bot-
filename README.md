# مساعد الدكان الرقمي — WhatsApp Cloud API

Dukkan Bot is a WhatsApp-powered shop assistant for managing sales, expenses, inventory, debt tracking, and daily reporting through natural Arabic messages.

## Features

- Sales and expense logging
- Customer debt tracking and payments
- Inventory management with low-stock alerts
- Daily / weekly / monthly reports
- Audio message transcription using Whisper
- Multi-shop support per WhatsApp number
- SQLite-backed local database

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in the values in .env
uvicorn app:app --host 0.0.0.0 --port 8000
```

Verify app health:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Required Environment Variables

Create a `.env` file using the values from `.env.example`:

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

## Meta / WhatsApp Setup

1. Go to developers.facebook.com and create a Business app.
2. Add the WhatsApp product.
3. Copy the `PHONE_NUMBER_ID` from WhatsApp API Setup.
4. Create a System User and generate a permanent token with `whatsapp_business_messaging` permission.
5. Copy the `APP_SECRET` from Settings → Basic.
6. Configure Webhook in WhatsApp Configuration:
   - Callback URL: `https://<your-public-url>/webhook`
   - Verify Token: your `VERIFY_TOKEN`
   - Subscribe to the `messages` field.
7. Send a test message from your WhatsApp number: `بعت بـ 50`

More detailed instructions are in:

- `SETUP_META_WHATSAPP.md`

## Local Test in Codespaces

A ready-to-run script is included:

```bash
bash test-codespace.sh
```

This script will:
- create a venv
- install dependencies
- create `.env` if missing
- start the app
- test `/health`
- test the webhook verification endpoint

Full instructions are in:

- `LOCAL_TEST_GUIDE.md`

## Docker

```bash
docker build -t dukkan .
docker run --rm -p 8000:8000 --env-file .env -v dukkan-data:/data dukkan
```

## Cloud Deployment

This repo includes deployment configs for several platforms:

- `railway.json` - Railway deployment
- `render.yaml` - Render deployment
- `fly.toml` - Fly.io deployment

### Railway

1. Connect the repo to Railway.
2. Use the existing Dockerfile.
3. Add env vars from `.env`.
4. Mount a persistent volume at `/data`.
5. Deploy.

### Render

1. Create a new Web Service.
2. Connect the repo.
3. Use the included `render.yaml`.
4. Add env vars and deploy.

### Fly.io

```bash
fly launch --dockerfile Dockerfile --name dukkan-bot --region iad
fly volumes create dukkan_data --region iad --size 1
fly deploy
```

See:

- `DEPLOYMENT_GUIDE.md`

## Webhook Example

After deployment, set your Meta webhook to:

```text
https://<your-public-domain>/webhook
```

Then use the same `VERIFY_TOKEN` in Meta and in `.env`.

## Notes

- Every WhatsApp number acts as a separate shop ledger.
- Audio files are downloaded from Meta and transcribed using OpenAI Whisper.
- Database data should stay in a persistent volume (`/data`) in production.
- Do not commit `.env` files to Git.

## Repo Assets

- `README.md`
- `SETUP_META_WHATSAPP.md`
- `DEPLOYMENT_GUIDE.md`
- `LOCAL_TEST_GUIDE.md`
- `railway.json`
- `render.yaml`
- `fly.toml`
- `test-codespace.sh`
- `.dockerignore`

## Next Steps

1. Add real Meta credentials to `.env`
2. Start the app locally or in Codespaces
3. Make port 8000 public for testing
4. Configure the Meta webhook
5. Deploy to Railway / Render / Fly.io

For full setup and troubleshooting, refer to the guide files above.
