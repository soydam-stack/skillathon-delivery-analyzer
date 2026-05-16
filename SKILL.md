---
name: delivery-order-analyzer
description: Analyze delivery app order history CSV to report spending, habits, categories, monthly trends, and savings goals in Korean.
license: MIT
metadata:
  category: lifestyle
  locale: ko-KR
  phase: v1
---

# 배달 주문 내역 분석기

## What this skill does
배달 주문 내역 CSV(orders.csv)를 읽어 총 식비, 자주 시킨 음식점 Top 5,
앱별 이용 현황, 음식 카테고리, 요일/시간대 패턴, 월별 비교,
절약 목표 대비 상태를 분석하고 result.md로 출력한다.

## When to use
- "이번달 배달비 얼마나 썼지?" 궁금할 때
- 자주 시키는 음식점·메뉴 파악하고 싶을 때
- 치킨/피자/중식처럼 카테고리별 지출을 보고 싶을 때
- 월 예산을 정하고 초과 금액과 줄여야 할 주문 횟수를 보고 싶을 때
- 주문 습관을 돌아보고 싶을 때
- 예시: "4월 배달 주문 내역을 35만원 예산 기준으로 분석해줘"

## When not to use
- 실시간 배달앱 연동이 필요할 때 (이 스킬은 CSV 파일 기반)
- 배달앱 HTML을 자동으로 로그인해서 가져와야 할 때

## Prerequisites
- Python 3.8 이상
- 외부 패키지 설치 불필요

## Required environment variables
없음

## Inputs

| 항목 | 형식 | 필수 컬럼 |
|------|------|-----------|
| orders.csv | CSV (UTF-8) | 주문일시, 앱, 음식점, 메뉴, 금액 |

주문일시 형식: `YYYY-MM-DD HH:MM`
금액: 숫자만 (원 단위, 쉼표 없이)

## Workflow

1. orders.csv를 같은 폴더에 준비한다.
2. `python3 analyze.py`를 실행한다.
3. 필요하면 `python3 analyze.py --budget 350000 --output result.md`처럼 예산과 출력 파일명을 바꾼다.
4. result.md를 확인한다.
5. 검증 명령을 실행한다.

```bash
python3 - << 'EOF'
content = open("result.md").read()
assert "💰 이번달 식비" in content
assert "🍜 주문 습관" in content
assert "📅 요일 패턴" in content
assert "🏷️ 음식 카테고리 분석" in content
assert "📈 월별 비교" in content
assert "🎯 절약 목표" in content
print("검증 통과 ✅")
EOF
```

## Done when
- result.md 생성됨
- 💰/🍜/🏷️/📅/📈/🎯 섹션 모두 포함
- 검증 명령이 `검증 통과 ✅` 출력

## Failure modes

| 상황 | 원인 | 해결 |
|------|------|------|
| `FileNotFoundError` | orders.csv 없음 | analyze.py와 같은 폴더에 파일 위치 |
| `ValueError: time data...` | 날짜 형식 오류 | `YYYY-MM-DD HH:MM` 형식 확인 |
| `KeyError: '금액'` | 컬럼명 오류 | CSV 헤더가 정확히 `금액`인지 확인 |
| Top 5가 5개 미만 | 주문 건수 부족 | orders.csv에 5개 이상 다른 음식점 필요 |
| 월별 비교가 1행만 표시 | CSV에 한 달 데이터만 있음 | 여러 달 데이터를 넣으면 전월 대비 자동 계산 |
| 예산 결과가 기대와 다름 | 기본 예산 400000원 사용 | `--budget 350000`처럼 직접 입력 |

## Notes
- 금액 컬럼에 쉼표(,)가 있으면 파싱 오류 발생. 숫자만 입력할 것.
- 실제 배달앱 주문 내역을 쓸 경우 개인정보 삭제 후 사용.
- 카테고리는 음식점명과 메뉴명 키워드 기반으로 추정한다.
