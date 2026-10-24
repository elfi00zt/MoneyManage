"""
スクリーンショット撮影用のデモデータ（架空）を作る。

使い方:
  python make_demo_db.py <アプリのソースの V1__init.sql> <出力する .db> [<V2__savings.sql> [<V3__merge_investment.sql> [<V4__point_payment.sql> [<V5__savings_opening_balance.sql>]]]]
  V2 を指定すると、貯金・積立のデータ（口座・積立の目的・入金・貯金からの支出）も入れる。
  V3 を指定すると、投資・積立の明細と固定費が「投資口座」への積立に移る（アプリの更新と同じ処理）。
  V4 を指定すると、ポイント払いの明細も入れる。
  V5 を指定すると、貯金口座に最初の残高（アプリを使い始める前からあったお金）を入れる。
アプリは -PkakeiboDb=<出力した .db> を付けて起動する（本番のデータには触れない）。
"""
import sqlite3
import sys
from datetime import date, timedelta

schema, out = sys.argv[1], sys.argv[2]
savings_schema = sys.argv[3] if len(sys.argv) > 3 else None
merge_schema = sys.argv[4] if len(sys.argv) > 4 else None
points_schema = sys.argv[5] if len(sys.argv) > 5 else None
opening_schema = sys.argv[6] if len(sys.argv) > 6 else None
db = sqlite3.connect(out)
db.executescript(open(schema, encoding="utf-8").read())
now = "2026-10-20T10:00:00"
db.execute("INSERT INTO schema_version VALUES (1, '初期スキーマ', ?)", (now,))
db.execute("INSERT INTO app_setting VALUES ('regular_payday', '25', ?)", (now,))

# 給料日（土日は直前の金曜）を期間の開始日にする
paydays = ["2026-01-23", "2026-02-25", "2026-03-25", "2026-04-24", "2026-05-25", "2026-06-25",
           "2026-07-24", "2026-08-25", "2026-09-25"]
# 画面上の期間は直近の2つだけにする（1〜7月の明細は「年間の収支」の画面にだけ表示される）
periods = [("2026-08-25", 32000), ("2026-09-25", None)]
if savings_schema:
    # 撮影日（10/23）が新しい期間に入るため、10/23 からの期間も作る（画面は「前の期間」に戻して撮る）
    periods.append(("2026-10-23", None))
for d, carry in periods:
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

if savings_schema:
    db.executescript(open(savings_schema, encoding="utf-8").read())
    db.execute("INSERT INTO schema_version VALUES (2, '貯金・積立', ?)", (now,))
    db.execute("INSERT INTO savings_account (name, sort_order, created_at, updated_at) VALUES ('ネット銀行', 20, ?, ?)",
               (now, now))
    for name, target, order in [("旅行", 20000, 10), ("生活防衛資金", 10000, 20)]:
        gid = db.execute("INSERT INTO savings_goal (name, sort_order, created_at, updated_at) VALUES (?, ?, ?, ?)",
                         (name, order, now, now)).lastrowid
        db.execute("INSERT INTO savings_goal_target VALUES (?, '2026-08-25', ?, ?)", (gid, target, now))

    def account(n):
        return db.execute("SELECT id FROM savings_account WHERE name=?", (n,)).fetchone()[0]

    def goal(n):
        return None if n is None else db.execute("SELECT id FROM savings_goal WHERE name=?", (n,)).fetchone()[0]

    def save(date_, amount, acc, goal_name=None):
        db.execute("INSERT INTO entry(entry_type, is_fixed, entry_date, title, amount, category_id, savings_account_id,"
                   " savings_goal_id, created_at, updated_at) VALUES ('SAVINGS', 0, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (date_, goal_name or "貯金", amount, cat("SAVINGS", "貯金"), account(acc), goal(goal_name), now, now))

    save("2026-08-26", 20000, "貯金口座")
    save("2026-08-27", 20000, "ネット銀行", "旅行")
    save("2026-08-27", 10000, "貯金口座", "生活防衛資金")
    save("2026-09-26", 20000, "ネット銀行", "旅行")
    save("2026-09-26", 5000, "貯金口座", "生活防衛資金")
    # 貯金から支払った支出（家計の残額は減らさず、貯金口座の残高が減る）
    db.execute("INSERT INTO entry(entry_type, is_fixed, entry_date, title, amount, category_id, payment_method_id,"
               " savings_account_id, created_at, updated_at) VALUES ('EXPENSE', 0, '2026-10-03', '電子レンジ', 12000, ?, ?,"
               " ?, ?, ?)", (cat("EXPENSE", "買い物"), pm("銀行振込"), account("貯金口座"), now, now))
    add("INCOME", 1, "2026-10-23", "給与", 250000, "給与")
    save("2026-10-23", 20000, "ネット銀行", "旅行")
    save("2026-10-23", 10000, "貯金口座", "生活防衛資金")

if merge_schema:
    # 毎月の投資・積立の固定費（V3 で「投資口座」への「貯金」の固定費になる）
    db.execute("INSERT INTO fixed_cost(name, entry_type, amount, pay_day, category_id, payment_method_id, created_at,"
               " updated_at) VALUES ('つみたて投資', 'INVESTMENT', 30000, 27, ?, ?, ?, ?)",
               (cat("INVESTMENT", "積立"), pm("銀行振込"), now, now))
    db.executescript(open(merge_schema, encoding="utf-8").read())
    db.execute("INSERT INTO schema_version VALUES (3, '投資・積立を貯金に統合', ?)", (now,))

if points_schema:
    db.executescript(open(points_schema, encoding="utf-8").read())
    db.execute("INSERT INTO schema_version VALUES (4, 'ポイント払い', ?)", (now,))
    # ポイントで支払った支出（家計の残額は減らさない）
    for d, title, amount, category in [("2026-08-30", "カフェ", 650, "食費"), ("2026-09-10", "日用品", 1200, "買い物"),
                                       ("2026-10-06", "コンビニ", 540, "食費"),
                                       ("2026-10-09", "ドラッグストア", 880, "買い物")]:
        db.execute("INSERT INTO entry(entry_type, is_fixed, entry_date, title, amount, category_id, paid_with_points,"
                   " created_at, updated_at) VALUES ('EXPENSE', 0, ?, ?, ?, ?, 1, ?, ?)",
                   (d, title, amount, cat("EXPENSE", category), now, now))

if opening_schema:
    db.executescript(open(opening_schema, encoding="utf-8").read())
    db.execute("INSERT INTO schema_version VALUES (5, '貯金口座の最初の残高', ?)", (now,))
    db.execute("UPDATE savings_account SET opening_balance = 150000 WHERE name = '貯金口座'")
    # アドバイスの例が出るよう、サブスクの固定費と、9/25〜の期間の娯楽の出費を足す
    for name, amount in [("動画配信サービス", 1490), ("音楽配信", 980)]:
        db.execute("INSERT INTO fixed_cost(name, entry_type, amount, pay_day, category_id, payment_method_id,"
                   " created_at, updated_at) VALUES (?, 'EXPENSE', ?, 28, ?, ?, ?, ?)",
                   (name, amount, cat("EXPENSE", "サブスク"), pm("クレジットカード"), now, now))
    add("EXPENSE", 0, "2026-10-10", "ライブ", 8800, "娯楽", "クレジットカード")
db.commit()
print("entries:", db.execute("SELECT COUNT(*) FROM entry").fetchone()[0])
