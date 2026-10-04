# Dukkan Bot Deployment Guide

This project is already set up as a FastAPI WhatsApp bot and can be deployed locally or to any Docker-compatible host.

## Quick local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in environment variables in .env
uvicorn app:app --host 0.0.0.0 --port 8000
```

Then verify:

```bash
curl http://localhost:8000/health
```

## Docker run

```bash
docker build -t dukkan .
docker run --rm -p 8000:8000 --env-file .env -v dukkan-data:/data dukkan
```

## Railway

1. Push the repo to GitHub.
2. Go to Railway and create a new project from GitHub repo.
3. Use the existing `Dockerfile` automatically.
4. Add environment variables from `.env.example`.
5. Add a persistent volume at `/data` for SQLite.
6. Redeploy.

Example environment variables:

```env
WHATSAPP_TOKEN=
PHONE_NUMBER_ID=
VERIFY_TOKEN=
APP_SECRET=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
DB_PATH=/data/shop.db
TZ_NAME=Asia/Riyadh
CURRENCY=ر.س
LOW_STOCK=5
```

## Render

1. Create a new Web Service on Render.
2. Select the GitHub repo.
3. Use the included `render.yaml`.
4. Add the same environment variables.
5. Render mounts `/data` automatically through the config.
6. Deploy.

## Fly.io

1. Install Fly.io CLI.
2. Run:

```bash
fly launch --dockerfile Dockerfile --name dukkan-bot --region iad
fly volumes create dukkan_data --region iad --size 1
fly deploy
```

3. Add the required environment variables in Fly.io Secrets or dashboard.
4. Confirm the app is healthy on `/health`.

## Webhook setup

After deployment, set Meta webhook URL to:

```text
https://<your-public-domain>/webhook
```

Use your `VERIFY_TOKEN` as the webhook verify token.

## Production note

The bot uses SQLite at `DB_PATH`; in a container or cloud deployment you should keep `/data` persistent to avoid data loss.
