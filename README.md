# مساعد الدكان الرقمي — WhatsApp Cloud API

## التشغيل محليًا
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # عبّئ القيم
uvicorn app:app --port 8000
ngrok http 8000           # للحصول على رابط HTTPS عام
```

## الربط مع Meta
1. developers.facebook.com ← Create App ← نوع Business ← أضف منتج **WhatsApp**.
2. من *API Setup* انسخ `PHONE_NUMBER_ID`، وأنشئ **System User** بتوكن دائم (`WHATSAPP_TOKEN`) بصلاحية `whatsapp_business_messaging`.
3. `APP_SECRET` من *Settings ← Basic*.
4. *WhatsApp ← Configuration ← Webhook*: Callback URL = `https://<رابطك>/webhook`، Verify token = قيمة `VERIFY_TOKEN`، ثم اشترك في حقل **messages**.
5. أرسل رسالة من هاتفك إلى رقم الاختبار: "بعت بـ 50".

## النشر
`docker build -t dukkan . && docker run -p 8000:8000 -v dukkan-data:/data --env-file .env dukkan`
(على Railway / Render / Fly.io يكفي ربط المستودع وإضافة المتغيرات ووحدة تخزين دائمة لـ /data).

## ملاحظات
- كل رقم واتساب = دفتر مستقل (متعدد المحلات تلقائيًا).
- الرد داخل 24 ساعة من رسالة العميل مجاني الصياغة؛ الرسائل الاستباقية (تذكير الديون، تقرير يومي) تحتاج **Message Templates** معتمدة.
- الخطوات التالية: الرسائل الصوتية، المخزون، تصدير Excel، الاشتراكات.

## الرسائل الصوتية والمخزون
- الصوت: يُنزَّل من Meta ثم يُفرَّغ عبر Whisper (`OPENAI_API_KEY`)، ثم يُعالج كنص. بدون المفتاح يطلب البوت من المستخدم الكتابة.
- المخزون: "وصل 20 حليب" (أو "اشتريت 20 حليب بـ 100" فيُسجَّل مصروف أيضًا)، "الحليب صار 12" للجرد، "المخزون" للنواقص. البيع بصنف وكمية ("بعت 3 حليب بـ 15") يخصم تلقائيًا للأصناف المسجّلة فقط، و"تراجع" يعيد الكمية.
