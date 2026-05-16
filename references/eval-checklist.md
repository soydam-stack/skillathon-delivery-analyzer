# 평가 체크리스트

이 문서는 Skillathon 제출 전 `delivery-order-analyzer`가 재사용 가능한 Skill인지
검토하기 위한 기준입니다.

## 실행 가능성

- [ ] `python3 analyze.py` 실행 시 오류 없이 `result.md`가 생성된다.
- [ ] 외부 패키지 설치 없이 Python 표준 라이브러리만으로 실행된다.
- [ ] `orders.csv`가 UTF-8 CSV로 로드된다.
- [ ] 주문 데이터 25건이 정상적으로 읽힌다.

## 출력 품질

- [ ] `result.md`에 총 식비 섹션이 포함된다.
- [ ] `result.md`에 주문 습관 섹션이 포함된다.
- [ ] `result.md`에 요일 패턴 섹션이 포함된다.
- [ ] 가장 많이 주문한 음식점, 앱별 이용 현황, 최애 메뉴가 표시된다.
- [ ] mock data 기반 결과임을 명시한다.

## 제출 적합성

- [ ] `README.md`에 문제 정의, 대상 사용자, 실행 방법, 결과물 예시, 검증 결과, 한계가 있다.
- [ ] `SKILL.md`에 반복 실행 절차, 입력, 검증 기준, failure modes가 있다.
- [ ] `references/`에 데이터 스키마, 프롬프트 예시, 트러블슈팅, 평가 기준이 있다.
- [ ] 실제 개인정보, 내부 데이터, API key, token, webhook URL이 포함되지 않는다.

## 최종 검증 명령

```bash
python3 analyze.py && python3 - << 'EOF'
import os, csv

files = [
    "README.md",
    "SKILL.md",
    "orders.csv",
    "analyze.py",
    "result.md",
    "references/data-schema.md",
    "references/prompt-examples.md",
    "references/troubleshooting.md",
    "references/eval-checklist.md",
]

for path in files:
    assert os.path.exists(path), f"missing file: {path}"

rows = list(csv.DictReader(open("orders.csv", encoding="utf-8")))
assert len(rows) == 25
assert all(k in rows[0] for k in ["주문일시", "앱", "음식점", "메뉴", "금액"])

content = open("result.md", encoding="utf-8").read()
assert "💰 이번달 식비" in content
assert "🍜 주문 습관" in content
assert "📅 요일 패턴" in content
assert "mock data" in content

print("eval checklist passed")
EOF
```
