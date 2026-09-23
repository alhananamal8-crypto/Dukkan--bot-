import json
import os
import re

from anthropic import Anthropic

MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
_client = None

SYSTEM = """أنت محلل رسائل لنظام محاسبة دكان عبر واتساب. حوّل رسالة صاحب الدكان إلى JSON فقط، بلا أي نص آخر.
الشكل:
{"intent": "...", "amount": number|null, "customer": string|null, "note": string|null, "item": string|null, "qty": number|null, "period": "today"|"week"|"month"|null}

قيم intent:
- sale: بيع نقدي ("بعت بـ 50"، "مبيعات 120")
- expense: مصروف أو شراء بضاعة أو دفع لمورد ("دفعت 200 كهرباء")
- debt: بيع بالدين، زبون أخذ بضاعة ولم يدفع ("أحمد أخذ بالدين 30")
- payment: زبون سدّد كله أو بعضه ("أحمد سدد 20")
- report: طلب ملخص/تقرير/ربح/كم بعت (period حسب الطلب، الافتراضي today)
- debts: طلب قائمة الديون، أو دين زبون معيّن (ضع اسمه في customer)
- stock_add: توريد/شراء صنف للمخزون بكمية ("وصل 20 حليب"، "اشتريت 10 سكر بـ 100" — amount = التكلفة إن ذُكرت)
- stock_set: جرد/تصحيح كمية ("الحليب صار 12")
- stock_check: سؤال عن المخزون أو النواقص (item إن سُئل عن صنف، وإلا null)
- undo: تراجع أو حذف آخر عملية
- help: مساعدة أو تحية
- unknown: غير مفهوم

قواعد: حوّل الأرقام العربية إلى إنجليزية. amount رقم موجب فقط. note وصف مختصر (مثل: كهرباء، مورد الحليب). لا تخترع بيانات غير موجودة في الرسالة.
الأصناف: اكتب item بصيغة موحّدة (مفرد، بدون "ال"، مثل: حليب). في sale/debt إن ذُكر صنف وكمية ("بعت 3 حليب بـ 15") املأ item وqty."""

_AR = str.maketrans("٠١٢٣٤٥٦٧٨٩٫", "0123456789.")


def parse_message(text: str) -> dict:
    global _client
    _client = _client or Anthropic()
    text = text.translate(_AR)
    try:
        r = _client.messages.create(
            model=MODEL,
            max_tokens=250,
            system=SYSTEM,
            messages=[{"role": "user", "content": text}],
        )
        raw = r.content[0].text
        m = re.search(r"\{.*\}", raw, re.S)
        return json.loads(m.group(0)) if m else {"intent": "unknown"}
    except Exception:
        return {"intent": "unknown"}
