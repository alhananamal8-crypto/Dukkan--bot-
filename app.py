import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request  # noqa: E402
from fastapi.responses import PlainTextResponse  # noqa: E402

import db  # noqa: E402
import stt  # noqa: E402
import whatsapp  # noqa: E402
from nlu import parse_message  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dukkan")

TZ = ZoneInfo(os.getenv("TZ_NAME", "UTC"))
CUR = os.getenv("CURRENCY", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
LOW = float(os.getenv("LOW_STOCK", "5"))

db.init()
app = FastAPI(title="مساعد الدكان الرقمي")

HELP = """أهلًا بك في *مساعد الدكان الرقمي* 🏪
اكتب لي عملياتك بشكل طبيعي:

• بعت بـ 50
• دفعت 200 كهرباء
• أحمد أخذ بالدين 30
• أحمد سدد 20
• كم الديون؟ / كم دين أحمد؟
• تقرير اليوم / الأسبوع / الشهر
• بعت 3 حليب بـ 15
• وصل 20 حليب  /  الحليب صار 12
• كم باقي حليب؟ / المخزون
• تراجع (يحذف آخر عملية)

🎙️ يمكنك أيضًا إرسال رسالة صوتية."""


def today():
    return datetime.now(TZ).date()


def money(x: float) -> str:
    s = f"{x:,.2f}".rstrip("0").rstrip(".")
    return f"{s} {CUR}".strip()


def _num(x) -> float:
    try:
        return float(x or 0)
    except (TypeError, ValueError):
        return 0.0


def fmt(n: float) -> str:
    return f"{n:g}"


def stock_line(phone: str, item: str, qty: float) -> str:
    """يخصم المبيع من المخزون (إن كان الصنف مسجّلاً) ويعيد سطر الرصيد."""
    if not item or qty <= 0 or db.stock_get(phone, item) is None:
        return ""
    db.stock_change(phone, item, -qty)
    left = db.stock_get(phone, item)
    warn = " ⚠️ قارب على النفاد" if left <= LOW else ""
    return f"\n📦 المتبقي من {item}: {fmt(left)}{warn}"


def report(phone: str, period: str) -> str:
    t = today()
    start, title = {
        "week": (t - timedelta(days=6), "آخر 7 أيام"),
        "month": (t.replace(day=1), "هذا الشهر"),
    }.get(period, (t, "اليوم"))
    s = db.summary(phone, str(start))
    cash, credit = s.get("sale", 0), s.get("debt", 0)
    exp, paid = s.get("expense", 0), s.get("payment", 0)
    sales = cash + credit
    return (
        f"📊 *تقرير {title}*\n"
        f"المبيعات: {money(sales)} (نقدي {money(cash)} + دين {money(credit)})\n"
        f"المصروفات: {money(exp)}\n"
        f"تحصيل ديون: {money(paid)}\n"
        f"الربح التقريبي: {money(sales - exp)}\n"
        f"صافي النقد: {money(cash + paid - exp)}"
    )


def run(phone: str, p: dict) -> str:
    intent = p.get("intent")
    cust = (p.get("customer") or "").strip()
    note = (p.get("note") or "").strip()
    item = (p.get("item") or "").strip()
    qty = _num(p.get("qty"))

    if intent == "stock_add":
        if not item or qty <= 0:
            return "اذكر الصنف والكمية. مثال: وصل 20 حليب"
        db.stock_change(phone, item, qty)
        extra = ""
        cost = _num(p.get("amount"))
        if cost > 0:
            db.add(phone, "expense", cost, "", f"شراء {item}", str(today()))
            extra = f"\nوسُجّل مصروف {money(cost)}"
        return f"📦 أُضيف {fmt(qty)} {item}. الرصيد: {fmt(db.stock_get(phone, item))}{extra}"

    if intent == "stock_set":
        if not item or p.get("qty") is None or qty < 0:
            return "اذكر الصنف والكمية. مثال: الحليب صار 12"
        db.stock_set(phone, item, qty)
        return f"📦 {item}: {fmt(qty)}"

    if intent == "stock_check":
        if item:
            q = db.stock_get(phone, item)
            return f"لا يوجد {item} في المخزون" if q is None else f"📦 {item}: {fmt(q)}"
        rows = db.stock_list(phone)
        if not rows:
            return "المخزون فارغ. مثال: وصل 20 حليب"
        lines = [f"• {i}: {fmt(q)}" + (" ⚠️" if q <= LOW else "") for i, q in rows]
        return "📦 *المخزون* (الأقل أولًا)\n" + "\n".join(lines)

    if intent in ("sale", "expense", "debt", "payment"):
        try:
            amt = float(p.get("amount") or 0)
        except (TypeError, ValueError):
            amt = 0
        if amt <= 0:
            return "لم أفهم المبلغ 🤔 مثال: بعت بـ 50"
        if intent in ("debt", "payment") and not cust:
            return "من هو الزبون؟ مثال: أحمد أخذ بالدين 30"
        db.add(phone, intent, amt, cust, note, str(today()), item or None, qty or None)
        if intent == "sale":
            return f"✅ تم تسجيل بيع {money(amt)}" + stock_line(phone, item, qty)
        if intent == "expense":
            return f"✅ تم تسجيل مصروف {money(amt)}" + (f" ({note})" if note else "")
        bal = db.balance(phone, cust)
        if intent == "debt":
            return f"✅ سُجّل على {cust} دين {money(amt)}\nإجمالي دينه: {money(bal)}" + stock_line(phone, item, qty)
        return f"✅ استلمت من {cust} {money(amt)}\nالمتبقي عليه: {money(bal)}"

    if intent == "report":
        return report(phone, p.get("period") or "today")

    if intent == "debts":
        if cust:
            return f"دين {cust}: {money(max(db.balance(phone, cust), 0))}"
        rows = db.debts(phone)
        if not rows:
            return "لا توجد ديون مستحقة 🎉"
        lines = [f"• {c}: {money(b)}" for c, b in rows]
        return "📒 *الديون المستحقة*\n" + "\n".join(lines) + f"\n\nالإجمالي: {money(sum(b for _, b in rows))}"

    if intent == "undo":
        r = db.undo(phone)
        if not r:
            return "لا توجد عمليات لحذفها"
        if r["type"] in ("sale", "debt") and r["item"] and r["qty"] and db.stock_get(phone, r["item"]) is not None:
            db.stock_change(phone, r["item"], r["qty"])
        return f"↩️ تم حذف آخر عملية ({r['type']} بمبلغ {money(r['amount'])})"

    return HELP


def process(phone: str, text: str) -> str:
    try:
        return run(phone, parse_message(text))
    except Exception:
        log.exception("handler error")
        return "حدث خطأ، حاول مرة أخرى 🙏"


def handle(phone: str, msg_id: str, text: str) -> None:
    if db.first_time(msg_id):
        whatsapp.send_text(phone, process(phone, text))


def handle_audio(phone: str, msg_id: str, media_id: str) -> None:
    if not db.first_time(msg_id):
        return
    try:
        audio, mime = whatsapp.download_media(media_id)
        text = stt.transcribe(audio, mime)
    except Exception:
        log.exception("audio error")
        text = None
    if not text:
        whatsapp.send_text(phone, "لم أتمكن من فهم الرسالة الصوتية 🎙️ اكتبها نصًا من فضلك")
        return
    whatsapp.send_text(phone, f"🎙️ سمعت: {text}\n\n{process(phone, text)}")


@app.get("/webhook")
def verify(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
):
    if mode == "subscribe" and VERIFY_TOKEN and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    raise HTTPException(403)


@app.post("/webhook")
async def incoming(request: Request, bg: BackgroundTasks):
    raw = await request.body()
    if not whatsapp.valid_signature(raw, request.headers.get("x-hub-signature-256")):
        raise HTTPException(403, "bad signature")
    data = await request.json()
    for entry in data.get("entry", []):
        for ch in entry.get("changes", []):
            for m in ch.get("value", {}).get("messages", []):
                phone, mid = m.get("from"), m.get("id")
                if m.get("type") == "text":
                    bg.add_task(handle, phone, mid, m["text"]["body"])
                elif m.get("type") == "audio":
                    bg.add_task(handle_audio, phone, mid, m["audio"]["id"])
                else:
                    bg.add_task(whatsapp.send_text, phone, "أرسل لي رسالة نصية من فضلك ✍️")
    return {"ok": True}  # Meta تتوقع 200 بسرعة


@app.get("/health")
def health():
    return {"status": "ok"}
