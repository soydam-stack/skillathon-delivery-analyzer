import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime

DAYS_KO = ["월", "화", "수", "목", "금", "토", "일"]
DEFAULT_BUDGET = 400_000

CATEGORY_RULES = [
    ("치킨", ["치킨", "BBQ", "굽네", "통다리"]),
    ("피자", ["피자", "피자헛", "피자알볼로"]),
    ("중식", ["짜장", "짬뽕", "탕수육", "군만두", "홍콩반점"]),
    ("버거", ["버거", "와퍼", "맥도날드", "버거킹", "빅맥"]),
    ("한식/분식", ["김밥", "찌개", "백반", "떡볶이", "제육"]),
    ("샌드위치", ["서브웨이", "이탈리안비엠티"]),
]


def load_orders(path="orders.csv"):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def format_won(amount):
    return f"{amount:,}원"


def infer_category(restaurant, menu):
    text = f"{restaurant} {menu}".lower()
    for category, keywords in CATEGORY_RULES:
        if any(keyword.lower() in text for keyword in keywords):
            return category
    return "기타"


def meal_time(dt):
    hour = dt.hour
    if 5 <= hour < 11:
        return "아침"
    if 11 <= hour < 15:
        return "점심"
    if 15 <= hour < 18:
        return "오후간식"
    if 18 <= hour < 22:
        return "저녁"
    return "야식"


def parse_order(row):
    dt = datetime.strptime(row["주문일시"], "%Y-%m-%d %H:%M")
    restaurant = row["음식점"]
    menu = row["메뉴"]
    return {
        "dt": dt,
        "app": row["앱"],
        "restaurant": restaurant,
        "menu": menu,
        "amount": int(row["금액"]),
        "day": DAYS_KO[dt.weekday()],
        "month": dt.strftime("%Y-%m"),
        "category": infer_category(restaurant, menu),
        "meal_time": meal_time(dt),
    }


def money_section(orders):
    total = sum(o["amount"] for o in orders)
    daily_avg = total // len(set(o["dt"].strftime("%Y-%m-%d") for o in orders))
    most_expensive = max(orders, key=lambda o: o["amount"])
    cheapest = min(orders, key=lambda o: o["amount"])
    lines = [
        "## 💰 이번달 식비",
        "",
        "| 항목 | 금액 |",
        "|------|------|",
        f"| 총 식비 | {format_won(total)} |",
        f"| 주문 횟수 | {len(orders)}회 |",
        f"| 1회 평균 | {format_won(total // len(orders))} |",
        f"| 주문일 평균 | {format_won(daily_avg)} |",
        f"| 최고가 주문 | {most_expensive['restaurant']} {most_expensive['menu']} ({format_won(most_expensive['amount'])}) |",
        f"| 최저가 주문 | {cheapest['restaurant']} {cheapest['menu']} ({format_won(cheapest['amount'])}) |",
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


def category_section(orders):
    by_category = defaultdict(lambda: {"count": 0, "amount": 0})
    total = sum(o["amount"] for o in orders)
    for order in orders:
        row = by_category[order["category"]]
        row["count"] += 1
        row["amount"] += order["amount"]

    rows = "\n".join(
        f"| {category} | {data['count']}회 | {format_won(data['amount'])} | {data['amount'] * 100 // total}% |"
        for category, data in sorted(
            by_category.items(), key=lambda item: item[1]["amount"], reverse=True
        )
    )
    top_category, top_data = max(by_category.items(), key=lambda item: item[1]["amount"])

    return "\n".join(
        [
            "## 🏷️ 음식 카테고리 분석",
            "",
            "| 카테고리 | 주문 횟수 | 지출 | 비율 |",
            "|----------|-----------|------|------|",
            rows,
            "",
            f"**가장 돈을 많이 쓴 카테고리: {top_category}** ({format_won(top_data['amount'])})",
        ]
    )


def pattern_section(orders):
    day_counter = Counter(o["day"] for o in orders)
    busiest_day = day_counter.most_common(1)[0]
    time_counter = Counter(o["meal_time"] for o in orders)

    bar_rows = "\n".join(
        f"| {day} | {'█' * cnt} | {cnt}회 |"
        for day, cnt in sorted(day_counter.items(), key=lambda x: DAYS_KO.index(x[0]))
    )
    time_rows = "\n".join(
        f"| {name} | {'█' * cnt} | {cnt}회 |"
        for name, cnt in sorted(time_counter.items(), key=lambda x: ["아침", "점심", "오후간식", "저녁", "야식"].index(x[0]))
    )
    busiest_time = time_counter.most_common(1)[0]

    lines = [
        "## 📅 요일 패턴",
        "",
        "### 요일별 주문",
        "",
        "| 요일 | 빈도 | 횟수 |",
        "|------|------|------|",
        bar_rows,
        "",
        f"**가장 많이 주문한 요일: {busiest_day[0]}요일** ({busiest_day[1]}회)",
        "",
        "### 시간대별 주문",
        "",
        "| 시간대 | 빈도 | 횟수 |",
        "|--------|------|------|",
        time_rows,
        "",
        f"**가장 자주 주문한 시간대: {busiest_time[0]}** ({busiest_time[1]}회)",
    ]
    return "\n".join(lines)


def monthly_comparison_section(orders):
    by_month = defaultdict(lambda: {"count": 0, "amount": 0})
    for order in orders:
        row = by_month[order["month"]]
        row["count"] += 1
        row["amount"] += order["amount"]

    rows = []
    previous_amount = None
    for month in sorted(by_month):
        data = by_month[month]
        if previous_amount is None:
            change = "-"
        else:
            diff = data["amount"] - previous_amount
            sign = "+" if diff > 0 else ""
            change = f"{sign}{format_won(diff)}"
        rows.append(
            f"| {month} | {data['count']}회 | {format_won(data['amount'])} | {change} |"
        )
        previous_amount = data["amount"]

    note = "비교할 이전 달 데이터가 있으면 증감액을 자동 계산합니다."
    if len(by_month) > 1:
        months = sorted(by_month)
        diff = by_month[months[-1]]["amount"] - by_month[months[-2]]["amount"]
        direction = "증가" if diff > 0 else "감소" if diff < 0 else "동일"
        note = f"최근 월은 직전 월 대비 **{format_won(abs(diff))} {direction}**했습니다."

    return "\n".join(
        [
            "## 📈 월별 비교",
            "",
            "| 월 | 주문 횟수 | 총 지출 | 전월 대비 |",
            "|----|-----------|---------|-----------|",
            "\n".join(rows),
            "",
            note,
        ]
    )


def budget_section(orders, budget):
    total = sum(o["amount"] for o in orders)
    diff = budget - total
    status = "목표 안쪽" if diff >= 0 else "목표 초과"
    abs_diff = abs(diff)
    avg_order = total // len(orders)
    needed_cuts = (abs_diff + avg_order - 1) // avg_order if diff < 0 else 0
    top_restaurant, top_count = Counter(o["restaurant"] for o in orders).most_common(1)[0]

    lines = [
        "## 🎯 절약 목표",
        "",
        "| 항목 | 값 |",
        "|------|----|",
        f"| 월 예산 | {format_won(budget)} |",
        f"| 현재 지출 | {format_won(total)} |",
        f"| 상태 | {status} |",
    ]
    if diff >= 0:
        lines.append(f"| 남은 예산 | {format_won(diff)} |")
        lines.extend(["", f"현재 페이스라면 목표 예산보다 **{format_won(diff)}** 여유가 있습니다."])
    else:
        lines.append(f"| 초과 금액 | {format_won(abs_diff)} |")
        lines.extend(
            [
                "",
                f"평균 주문액 기준으로 약 **{needed_cuts}회**만 줄이면 목표 예산에 들어옵니다.",
                f"가장 자주 주문한 **{top_restaurant}** 주문({top_count}회)을 1~2회 줄이는 것이 가장 빠른 절약 포인트입니다.",
            ]
        )
    return "\n".join(lines)


def insight_section(orders):
    restaurants = Counter(o["restaurant"] for o in orders)
    categories = Counter(o["category"] for o in orders)
    days = Counter(o["day"] for o in orders)
    apps = Counter(o["app"] for o in orders)
    total = sum(o["amount"] for o in orders)
    top_restaurant, top_restaurant_count = restaurants.most_common(1)[0]
    top_category, top_category_count = categories.most_common(1)[0]
    busiest_day, busiest_day_count = days.most_common(1)[0]
    main_app, main_app_count = apps.most_common(1)[0]

    return "\n".join(
        [
            "## 🧭 절약 인사이트",
            "",
            f"- **반복 주문 관리**: {top_restaurant} 주문이 {top_restaurant_count}회입니다. 같은 음식점 반복 주문을 1회만 줄여도 체감 절약이 큽니다.",
            f"- **카테고리 관리**: {top_category} 주문이 {top_category_count}회로 가장 많습니다. 다음 달에는 이 카테고리에 주간 횟수 제한을 두면 좋습니다.",
            f"- **요일 관리**: {busiest_day}요일 주문이 {busiest_day_count}회입니다. 해당 요일에 미리 식사 계획을 잡으면 충동 주문을 줄일 수 있습니다.",
            f"- **앱 사용 습관**: {main_app} 비중이 {main_app_count * 100 // len(orders)}%입니다. 쿠폰이 없는 날에는 장바구니 단계에서 한 번 더 비교해보세요.",
            f"- **총평**: 이번 분석 대상 지출은 {format_won(total)}입니다. 목표 예산을 정하고 가장 비싼 주문부터 줄이면 효과가 빠릅니다.",
        ]
    )


def summary_line(orders):
    restaurants = Counter(o["restaurant"] for o in orders)
    top_rest, top_cnt = restaurants.most_common(1)[0]
    total = sum(o["amount"] for o in orders)
    emoji_map = {"치킨": "🐔", "피자": "🍕", "중식": "🥡", "버거": "🍔", "분식": "🌶️"}
    emoji = next((e for k, e in emoji_map.items() if k in top_rest), "🛵")
    return f"> 이번달 **{top_rest}**을(를) {top_cnt}번 시켰고 총 **{format_won(total)}**을 배달앱에 썼습니다. {emoji}"


def parse_args():
    parser = argparse.ArgumentParser(description="배달 주문 CSV를 분석해 Markdown 리포트를 생성합니다.")
    parser.add_argument("--input", default="orders.csv", help="분석할 CSV 파일 경로")
    parser.add_argument("--output", default="result.md", help="생성할 Markdown 리포트 경로")
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="월 식비 목표 예산(원)")
    return parser.parse_args()


def report_title(orders):
    months = sorted(set(o["month"] for o in orders))
    if len(months) == 1:
        return f"{orders[0]['dt'].strftime('%Y년 %m월')} 배달 주문 분석 리포트"
    return f"{months[0]} ~ {months[-1]} 배달 주문 분석 리포트"


def main():
    args = parse_args()
    raw = load_orders(args.input)
    orders = [parse_order(r) for r in raw]

    sections = [
        f"# {report_title(orders)}",
        "",
        summary_line(orders),
        "",
        "---",
        "",
        money_section(orders),
        "",
        habit_section(orders),
        "",
        category_section(orders),
        "",
        pattern_section(orders),
        "",
        monthly_comparison_section(orders),
        "",
        budget_section(orders, args.budget),
        "",
        insight_section(orders),
        "",
        "---",
        "",
        "> ⚠️ 이 결과는 mock data 기반입니다. 실제 주문 내역이 아닙니다.",
    ]

    result = "\n".join(sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"{args.output} 생성 완료")
    print(result)


if __name__ == "__main__":
    main()
