"""
スクリーンショット撮影用のデモデータ（架空）を作る。

使い方:
  python make_demo_db.py <アプリのソースの V1__init.sql> <出力する .db>
アプリは -PkakeiboDb=<出力した .db> を付けて起動する（本番のデータには触れない）。
"""
import sqlite3
import sys
from datetime import date, timedelta

schema, out = sys.argv[1], sys.argv[2]
db = sqlite3.connect(out)
db.executescript(open(schema, encoding="utf-8").read())
now = "2026-10-20T10:00:00"
db.execute("INSERT INTO schema_version VALUES (1, '初期スキーマ', ?)", (now,))
db.execute("INSERT INTO app_setting VALUES ('regular_payday', '25', ?)", (now,))

# 給料日（土日は直前の金曜）を期間の開始日にする
paydays = ["2026-01-23", "2026-02-25", "2026-03-25", "2026-04-24", "2026-05-25", "2026-06-25",
           "2026-07-24", "2026-08-25", "2026-09-25"]
# 画面上の期間は直近の2つだけにする（1〜7月の明細は「年間の収支」の画面にだけ表示される）
for d, carry in [("2026-08-25", 32000), ("2026-09-25", None)]:
    db.execute("INSERT INTO budget_period(start_date, carry_over_override, created_at, updated_at) "
               "VALUES (?, ?, ?, ?)", (d, carry, now, now))


def cat(t, n):
    return db.execute("SELECT id FROM category WHERE entry_type=? AND name=?", (t, n)).fetchone()[0]


def pm(n):
    return None if n is None else db.execute("SELECT id FROM payment_method WHERE name=?", (n,)).fetchone()[0]


def add(t, fixed, date, title, amount, category, payment=None, memo=None):
    db.execute("INSERT INTO entry(entry_type, is_fixed, entry_date, title, amount, category_id, payment_method_id,"
               " memo, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
               (t, fixed, date, title, amount, cat(t, category), pm(payment), memo, now, now))


variable = [
    ("食費", "スーパー", 4200), ("食費", "ランチ", 1100), ("交通費", "ICカードチャージ", 3000),
    ("買い物", "日用品", 2380), ("娯楽", "映画", 1900), ("交際費", "飲み会", 4500), ("食費", "スーパー", 3650),
]
for i, d in enumerate(paydays):
    y, m, day = d.split("-")
    add("INCOME", 1, d, "給与", 250000, "給与", None, None)
    add("EXPENSE", 1, f"{y}-{m}-27", "家賃", 65000, "家賃", "銀行振込")
    add("EXPENSE", 1, f"{y}-{m}-28", "スマホ代", 4980, "通信費", "クレジットカード")
    add("EXPENSE", 1, f"{y}-{m}-28", "動画配信サービス", 1490, "サブスク", "クレジットカード")
    add("INVESTMENT", 1, f"{y}-{m}-27", "つみたて投資", 30000, "積立", "銀行振込")
    for j, (c, title, amount) in enumerate(variable):
        dd = (date.fromisoformat(d) + timedelta(days=j * 4 + 1)).isoformat()
        if dd > "2026-10-20":
            continue
        add("EXPENSE", 0, dd, title, amount + (i * 170) % 900, c, "クレジットカード" if j % 3 else "現金")
    if m == "08":
        add("EXPENSE", 0, "2026-08-14", "旅行", 48000, "娯楽", "クレジットカード", "夏休み")

# 表示中の期間（9/25〜）の変動費を少し足す
add("EXPENSE", 0, "2026-10-12", "書籍", 1760, "買い物", "クレジットカード")
add("INCOME", 0, "2026-10-15", "副業", 15000, "副業")
db.commit()
print("entries:", db.execute("SELECT COUNT(*) FROM entry").fetchone()[0])
