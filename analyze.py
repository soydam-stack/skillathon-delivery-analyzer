import csv
from collections import Counter
from datetime import datetime

DAYS_KO = ["월", "화", "수", "목", "금", "토", "일"]


def load_orders(path="orders.csv"):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_order(row):
    dt = datetime.strptime(row["주문일시"], "%Y-%m-%d %H:%M")
    return {
        "dt": dt,
        "app": row["앱"],
        "restaurant": row["음식점"],
        "menu": row["메뉴"],
        "amount": int(row["금액"]),
        "day": DAYS_KO[dt.weekday()],
    }


def money_section(orders):
    total = sum(o["amount"] for o in orders)
    daily_avg = total // len(set(o["dt"].strftime("%Y-%m-%d") for o in orders))
    most_expensive = max(orders, key=lambda o: o["amount"])
    lines = [
        "## 💰 이번달 식비",
        "",
        "| 항목 | 금액 |",
        "|------|------|",
        f"| 총 식비 | {total:,}원 |",
        f"| 주문 횟수 | {len(orders)}회 |",
        f"| 1회 평균 | {total // len(orders):,}원 |",
        f"| 주문일 평균 | {daily_avg:,}원 |",
        f"| 최고가 주문 | {most_expensive['restaurant']} {most_expensive['menu']} ({most_expensive['amount']:,}원) |",
    ]
    return "\n".join(lines)


def habit_section(orders):
    restaurants = Counter(o["restaurant"] for o in orders)
    menus = Counter(o["menu"] for o in orders)
    apps = Counter(o["app"] for o in orders)

    rest_rows = "\n".join(
        f"| {i+1} | {name} | {cnt}회 |"
        for i, (name, cnt) in enumerate(restaurants.most_common(5))
    )
    app_rows = "\n".join(
        f"| {name} | {cnt}회 | {cnt*100//len(orders)}% |"
        for name, cnt in apps.most_common()
    )
    top_menu = menus.most_common(1)[0]

    lines = [
        "## 🍜 주문 습관",
        "",
        "### 자주 시킨 음식점 Top 5",
        "",
        "| 순위 | 음식점 | 횟수 |",
        "|------|--------|------|",
        rest_rows,
        "",
        "### 앱별 이용 현황",
        "",
        "| 앱 | 횟수 | 비율 |",
        "|----|------|------|",
        app_rows,
        "",
        f"### 최애 메뉴: **{top_menu[0]}** ({top_menu[1]}회)",
    ]
    return "\n".join(lines)


def pattern_section(orders):
    day_counter = Counter(o["day"] for o in orders)
    busiest_day = day_counter.most_common(1)[0]

    bar_rows = "\n".join(
        f"| {day} | {'█' * cnt} | {cnt}회 |"
        for day, cnt in sorted(day_counter.items(), key=lambda x: DAYS_KO.index(x[0]))
    )

    lines = [
        "## 📅 요일 패턴",
        "",
        "| 요일 | 빈도 | 횟수 |",
        "|------|------|------|",
        bar_rows,
        "",
        f"**가장 많이 주문한 요일: {busiest_day[0]}요일** ({busiest_day[1]}회)",
    ]
    return "\n".join(lines)


def summary_line(orders):
    restaurants = Counter(o["restaurant"] for o in orders)
    top_rest, top_cnt = restaurants.most_common(1)[0]
    total = sum(o["amount"] for o in orders)
    emoji_map = {"치킨": "🐔", "피자": "🍕", "중식": "🥡", "버거": "🍔", "분식": "🌶️"}
    emoji = next((e for k, e in emoji_map.items() if k in top_rest), "🛵")
    return f"> 이번달 **{top_rest}**을(를) {top_cnt}번 시켰고 총 **{total:,}원**을 배달앱에 썼습니다. {emoji}"


def main():
    raw = load_orders()
    orders = [parse_order(r) for r in raw]
    month = orders[0]["dt"].strftime("%Y년 %m월")

    sections = [
        f"# {month} 배달 주문 분석 리포트",
        "",
        summary_line(orders),
        "",
        "---",
        "",
        money_section(orders),
        "",
        habit_section(orders),
        "",
        pattern_section(orders),
        "",
        "---",
        "",
        "> ⚠️ 이 결과는 mock data 기반입니다. 실제 주문 내역이 아닙니다.",
    ]

    result = "\n".join(sections)
    with open("result.md", "w", encoding="utf-8") as f:
        f.write(result)

    print("result.md 생성 완료")
    print(result)


if __name__ == "__main__":
    main()
