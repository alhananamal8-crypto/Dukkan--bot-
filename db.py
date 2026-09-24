import os
import sqlite3

PATH = os.getenv("DB_PATH", "shop.db")


def conn():
    c = sqlite3.connect(PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tx (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            type TEXT NOT NULL,            -- sale | expense | debt | payment
            amount REAL NOT NULL,
            customer TEXT,
            note TEXT,
            item TEXT,
            qty REAL,
            day TEXT NOT NULL,             -- YYYY-MM-DD (بتوقيت المحل)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS ix_tx_phone_day ON tx(phone, day);
        CREATE TABLE IF NOT EXISTS seen (msg_id TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS stock (
            phone TEXT NOT NULL, item TEXT NOT NULL,
            qty REAL NOT NULL DEFAULT 0, PRIMARY KEY (phone, item)
        );
        """)
        for col in ("item TEXT", "qty REAL"):  # ترحيل قواعد قديمة
            try:
                c.execute(f"ALTER TABLE tx ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass


def first_time(msg_id):
    """True إذا لم تُعالج الرسالة من قبل (منع التكرار عند إعادة إرسال Meta)."""
    with conn() as c:
        cur = c.execute("INSERT OR IGNORE INTO seen(msg_id) VALUES (?)", (msg_id,))
        return cur.rowcount == 1


def add(phone, type_, amount, customer, note, day, item=None, qty=None):
    with conn() as c:
        c.execute(
            "INSERT INTO tx(phone,type,amount,customer,note,day,item,qty) VALUES (?,?,?,?,?,?,?,?)",
            (phone, type_, amount, customer or None, note or None, day, item, qty),
        )


def undo(phone):
    with conn() as c:
        row = c.execute(
            "SELECT * FROM tx WHERE phone=? ORDER BY id DESC LIMIT 1", (phone,)
        ).fetchone()
        if row:
            c.execute("DELETE FROM tx WHERE id=?", (row["id"],))
        return row


def summary(phone, since_day):
    with conn() as c:
        rows = c.execute(
            "SELECT type, SUM(amount) s FROM tx WHERE phone=? AND day>=? GROUP BY type",
            (phone, since_day),
        ).fetchall()
    return {r["type"]: r["s"] or 0 for r in rows}


_BAL = "SUM(CASE type WHEN 'debt' THEN amount WHEN 'payment' THEN -amount ELSE 0 END)"


def balance(phone, customer):
    with conn() as c:
        r = c.execute(
            f"SELECT {_BAL} b FROM tx WHERE phone=? AND customer=? COLLATE NOCASE",
            (phone, customer),
        ).fetchone()
    return r["b"] or 0


def debts(phone):
    with conn() as c:
        rows = c.execute(
            f"""SELECT customer, {_BAL} b FROM tx
                WHERE phone=? AND customer IS NOT NULL
                GROUP BY customer COLLATE NOCASE
                HAVING b > 0.001 ORDER BY b DESC""",
            (phone,),
        ).fetchall()
    return [(r["customer"], r["b"]) for r in rows]


def stock_change(phone, item, delta):
    with conn() as c:
        c.execute(
            "INSERT INTO stock(phone,item,qty) VALUES (?,?,?) "
            "ON CONFLICT(phone,item) DO UPDATE SET qty=qty+excluded.qty",
            (phone, item, delta),
        )


def stock_set(phone, item, qty):
    with conn() as c:
        c.execute(
            "INSERT INTO stock(phone,item,qty) VALUES (?,?,?) "
            "ON CONFLICT(phone,item) DO UPDATE SET qty=excluded.qty",
            (phone, item, qty),
        )


def stock_get(phone, item):
    """الكمية الحالية، أو None إذا الصنف غير مسجّل في المخزون."""
    with conn() as c:
        r = c.execute("SELECT qty FROM stock WHERE phone=? AND item=?", (phone, item)).fetchone()
    return r["qty"] if r else None


def stock_list(phone):
    with conn() as c:
        rows = c.execute("SELECT item, qty FROM stock WHERE phone=? ORDER BY qty ASC", (phone,)).fetchall()
    return [(r["item"], r["qty"]) for r in rows]
