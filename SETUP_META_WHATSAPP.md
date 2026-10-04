# 🔐 Meta/WhatsApp Cloud API Setup Guide

This guide walks you through setting up WhatsApp Cloud API credentials for Dukkan Bot.

---

## Step 1: Create a Meta Business App

### 1.1 Go to Meta Developers
- Visit: https://developers.facebook.com/
- Sign in with your Meta/Facebook account (create one if needed)

### 1.2 Create a New App
1. Click **"My Apps"** (top right)
2. Click **"Create App"**
3. Fill in the form:
   - **App Name**: `Dukkan Bot` (or your preferred name)
   - **App Contact Email**: Your email
   - **App Purpose**: Select **"Business"**
4. Click **"Create App"**

### 1.3 Add WhatsApp Product
1. In your app dashboard, click **"+ Add Product"**
2. Search for **"WhatsApp"**
3. Click **"Set Up"** on the WhatsApp Business Platform card
4. Complete the setup wizard (just follow the defaults)

---

## Step 2: Get WhatsApp API Credentials

### 2.1 Get Phone Number ID
1. In your app, go to **"WhatsApp > API Setup"**
2. You'll see a section with:
   ```
   Phone Number ID: xxxxxxxxxx
   Business Account ID: xxxxxxxxxx
   ```
3. **Copy the `Phone Number ID`** → Save it (you'll need this for `PHONE_NUMBER_ID`)

### 2.2 Get or Create a Test Phone Number
- You should see a **"Test Phone Number"** in the same section
- Note this number (you'll use it to test the bot)
- If not, click **"Add Recipient Phone Number"** and add your phone

### 2.3 Get App Secret
1. Go to **"Settings > Basic"** (left sidebar)
2. Find the **"App Secret"** field
3. **Copy it** → Save it (you'll need this for `APP_SECRET`)
4. ⚠️ Keep this secret - don't share it publicly!

---

## Step 3: Create System User & Get Permanent Token

### 3.1 Create a System User
1. Go to **"Settings > Users and Roles"**
2. Click **"System Users"** tab
3. Click **"Add System User"**
4. Fill in:
   - **Name**: `Dukkan Bot System` (or any name)
   - **Role**: Keep as default or select **"Admin"**
5. Click **"Create System User"**

### 3.2 Generate Access Token
1. Find your newly created system user in the list
2. Click the **"..."** (three dots) → **"Generate Access Token"**
3. Select:
   - **App**: Choose your Dukkan Bot app
   - **Token Expiration**: Select **"Never"** (for permanent token)
   - **Permissions**: Check **`whatsapp_business_messaging`**
4. Click **"Generate Token"**
5. **Copy the token** → Save it (you'll need this for `WHATSAPP_TOKEN`)
6. ⚠️ Store this safely - you won't see it again!

---

## Step 4: Set Up Webhook

### 4.1 Get Your Public URL

Before setting up the webhook, you need a public HTTPS URL. Choose one:

**Option A: Local Testing with ngrok (Recommended)**
```bash
# Install ngrok from https://ngrok.com/download or use Homebrew
brew install ngrok  # macOS
# or
choco install ngrok  # Windows

# Start ngrok (in a new terminal)
ngrok http 8000
# You'll see:
# https://xxxxx-xxx-xxx-xxx.ngrok.io -> http://localhost:8000
# Copy the HTTPS URL
```

**Option B: Already Deployed**
- If deploying to Railway/Render/Fly.io, you'll have a URL like:
  - `https://dukkan-bot.railway.app`
  - `https://dukkan-bot.onrender.com`
  - `https://dukkan-bot.fly.dev`

### 4.2 Configure Webhook in Meta
1. Go to **"WhatsApp > Configuration"**
2. In the **"Webhook Configuration"** section, click **"Edit"**
3. Fill in:
   - **Callback URL**: `https://<your-url>/webhook`
     - Example: `https://xxxxx-xxx-xxx-xxx.ngrok.io/webhook`
   - **Verify Token**: Enter any secret string (e.g., `my-secret-dukkan-token-123`)
     - ⚠️ This becomes your `VERIFY_TOKEN` environment variable
4. Click **"Verify and Save"**
5. Meta will send a GET request to your callback URL to verify it works
   - If successful, you'll see a green checkmark

### 4.3 Subscribe to Webhook Fields
1. Under **"Webhook Fields"**, make sure **`messages`** is checked
   - This tells Meta to send incoming messages to your webhook
2. Click **"Save"**

---

## Step 5: Create .env File

Create a `.env` file in your repository root with all your credentials:

```bash
# Copy .env.example and fill in your values
cp .env.example .env
```

Edit `.env` and fill in:

```env
# Meta / WhatsApp Cloud API
WHATSAPP_TOKEN=your_permanent_access_token_here
PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=my-secret-dukkan-token-123
APP_SECRET=your_app_secret_here

# Claude AI (get from https://console.anthropic.com)
ANTHROPIC_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-haiku-4-5-20251001

# Configuration
TZ_NAME=Asia/Riyadh
CURRENCY=ر.س
DB_PATH=shop.db

# Audio Transcription (get from https://platform.openai.com)
OPENAI_API_KEY=your_openai_api_key_here
STT_LANG=ar
LOW_STOCK=5
```

---

## Step 6: Test the Connection

### 6.1 Start the Bot Locally
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --port 8000

# In another terminal, start ngrok (if testing locally)
ngrok http 8000
```

### 6.2 Send a Test Message
1. Find your **test phone number** from Step 2.2
2. From your personal phone, send a WhatsApp message to the test number:
   ```
   بعت بـ 50
   ```
   (This means "I sold for 50")

3. You should receive a response:
   ```
   ✅ تم تسجيل بيع 50.00 ر.س
   ```

### 6.3 Test More Commands
Try these commands to test different features:

```
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

# Voice message
(Send an audio message in Arabic)

# Get help
مساعدة
```

---

## Troubleshooting

### "Webhook validation failed"
- ❌ Make sure your callback URL is correct and publicly accessible
- ❌ Verify that your server is running and responding to GET requests at `/webhook`
- ❌ Check that your `VERIFY_TOKEN` matches exactly

### "Invalid access token"
- ❌ Double-check you copied the `WHATSAPP_TOKEN` correctly
- ❌ Make sure the token hasn't expired (set to "Never" when generating)
- ❌ Verify you selected the right app when generating the token

### "No messages received"
- ❌ Confirm that **messages** field is checked in Webhook Fields
- ❌ Make sure your webhook URL is reachable (test with: `curl https://your-url/webhook`)
- ❌ Check server logs for errors

### "ngrok connection lost"
- ❌ ngrok free tier disconnects after 2 hours
- ❌ Restart ngrok and update the webhook URL in Meta
- ❌ For production, use a real domain (see deployment guide)

---

## Security Best Practices

1. ⚠️ **Never commit `.env` file** to Git
   - It's already in `.gitignore`

2. ⚠️ **Keep tokens secret**
   - Don't share `WHATSAPP_TOKEN`, `APP_SECRET`, or `ANTHROPIC_API_KEY`
   - Rotate tokens periodically

3. ⚠️ **Use HTTPS only**
   - Meta requires HTTPS for webhook URLs
   - Never use HTTP in production

4. ⚠️ **Verify webhook signatures**
   - The bot already does this (line 214 in `app.py`)
   - This ensures messages are actually from Meta

---

## Next Steps

✅ After successful setup:
1. Deploy to a cloud platform (Railway/Render/Fly.io)
2. Update webhook URL to your production domain
3. Add more phone numbers for different users
4. Customize settings (timezone, currency, low stock threshold)

See `DEPLOYMENT_GUIDE.md` for cloud platform setup.

---

## Support

- 📖 Meta WhatsApp Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/
- 📖 Claude AI Docs: https://docs.anthropic.com/
- 📖 OpenAI Whisper: https://platform.openai.com/docs/guides/speech-to-text
