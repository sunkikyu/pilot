import pandas as pd
import json
from datetime import datetime

# 📁 엑셀 파일 경로 (같은 폴더에 둘 것)
excel_path = "통합 문서1.xlsx"
output_path = "bus_schedule.json"

# 📥 엑셀 읽기 (A1~Q80 기준)
df = pd.read_excel(excel_path, header=None)

# A1~Q1: 노선명
route_names = df.iloc[0, :17]  # A~Q → 총 17열

# 2행~80행: 배차시간 데이터
time_data = df.iloc[1:80, :17]

# JSON 변환용 딕셔너리
result = {}

for col_idx, route in enumerate(route_names):
    if pd.isna(route):
        continue
    route_name = str(route).strip()
    times = []
    for val in time_data.iloc[:, col_idx]:
        if pd.notna(val):
            if isinstance(val, pd.Timestamp):
                t = val.time()
                times.append(f"{t.hour:02d}:{t.minute:02d}")
            elif hasattr(val, "hour") and hasattr(val, "minute"):
                times.append(f"{val.hour:02d}:{val.minute:02d}")
            elif isinstance(val, str):
                val = val.strip()
                try:
                    parsed = datetime.strptime(val, "%H:%M")
                    times.append(parsed.strftime("%H:%M"))
                except ValueError:
                    continue
    if times:
        cleaned = sorted(set(times), key=lambda x: datetime.strptime(x, "%H:%M"))
        result[route_name] = cleaned

# 💾 JSON 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ JSON 저장 완료 → {output_path}")
