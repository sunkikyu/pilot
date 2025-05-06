import streamlit as st
import json
from datetime import datetime, timedelta
from pytz import timezone
import holidays
import time

# ✅ 한국 시간으로 현재 시간
kst = timezone("Asia/Seoul")
now = datetime.now(kst)
today_date = now.date()

# ✅ 한국 공휴일 확인
kr_holidays = holidays.KR()
is_holiday = today_date in kr_holidays
weekday = now.weekday()  # 월:0, 일:6

if weekday == 5:
    schedule_file = "downloads/saturday.json"
elif weekday == 6 or is_holiday:
    schedule_file = "downloads/holiday.json"
else:
    schedule_file = "downloads/weekday.json"

# ✅ Streamlit 설정은 반드시 제일 위
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

st.title("🚌 실시간 버스 기점 출발 안내")

st.markdown(
    f"#### 오늘은 `{today_date.strftime('%Y-%m-%d')} ({'공휴일' if is_holiday else ['월','화','수','목','금','토','일'][weekday]})` 기준으로 시간표가 적용됩니다."
)

# ✅ JSON 로딩
@st.cache_data
def load_schedule(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(schedule_file)

# ✅ 사용자 지정 노선 정렬
def custom_sort(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

routes = sorted(bus_data.keys(), key=custom_sort)
selected_route = st.selectbox("노선을 선택하세요:", routes)

# ✅ 실시간 갱신
placeholder = st.empty()

while True:
    now = datetime.now(kst)
    if selected_route:
        times = bus_data[selected_route]
        results = []

        for time_str in times:
            try:
                bus_time = datetime.strptime(time_str, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=kst
                )
                if bus_time < now:
                    bus_time += timedelta(days=1)

                diff = bus_time - now
                results.append((time_str, diff))
            except Exception as e:
                st.error(f"시간 파싱 오류: {time_str} | {e}")

        # ⏳ 남은 시간 기준 정렬
        results = sorted(results, key=lambda x: x[1])[:3]

        # ✅ 시간 출력
        markdowns = []
        for time_str, diff in results:
            total_seconds = int(diff.total_seconds())
            if total_seconds < 60 * 60:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                icon = "⏰" if minutes <= 10 else "⏳"
                markdowns.append(f"- **{time_str}** → {icon} **{minutes}분 {seconds}초 남음**")
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                markdowns.append(f"- **{time_str}** → 🕓 **{hours}시간 {minutes}분 {seconds}초 남음**")

        placeholder.markdown("\n".join(markdowns))

    time.sleep(1)  # 1초마다 틱톡 갱신
