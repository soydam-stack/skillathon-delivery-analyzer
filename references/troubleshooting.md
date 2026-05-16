# 트러블슈팅 가이드

### FileNotFoundError: orders.csv

```bash
ls *.csv    # 파일 존재 확인
pwd         # 현재 경로 확인
```
analyze.py와 같은 폴더에서 실행하는지 확인한다.

---

### ValueError: time data '...' does not match format '%Y-%m-%d %H:%M'

주문일시 형식이 맞지 않는 경우.

```bash
python3 -c "
import csv
for i, row in enumerate(csv.DictReader(open('orders.csv', encoding='utf-8')), 1):
    print(i, repr(row['주문일시']))
"
```
형식이 다른 행을 찾아 `YYYY-MM-DD HH:MM`으로 수정한다.

---

### KeyError: '금액'

CSV 헤더 컬럼명이 다른 경우.

```bash
python3 -c "
import csv
print(list(csv.DictReader(open('orders.csv', encoding='utf-8')))[0].keys())
"
```
헤더가 정확히 `주문일시,앱,음식점,메뉴,금액`인지 확인한다.

---

### 금액 합계가 이상하게 큰 경우

금액 컬럼에 쉼표가 포함된 경우 (예: `22,000`).

```bash
python3 -c "
import csv
for row in csv.DictReader(open('orders.csv', encoding='utf-8')):
    if ',' in row['금액']:
        print('쉼표 발견:', row)
"
```
쉼표를 제거하고 숫자만 남긴다.
