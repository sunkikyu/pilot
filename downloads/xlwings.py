import pandas as pd
import json
from datetime import datetime

# 📁 엑셀 파일 경로
excel_path = "통합 문서1.xlsx"

# 시트별 처리
sheet_names = ["weekday", "saturday", "holiday"]

for sheet in sheet_names:
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)

        route_names = df.iloc[0, :17]  # A~Q 열
        time_data = df.iloc[1:80, :17]

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

        # 💾 시트별로 저장
        output_file = f"{sheet}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ {sheet}.json 저장 완료")

    except Exception as e:
        print(f"❌ 시트 '{sheet}' 처리 중 오류 발생: {e}")
