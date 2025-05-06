import json
import pytz
import time
from datetime import datetime, timedelta
import streamlit as st

# ✅ 반드시 최상단에 있어야 함
st.set_page_config(page_title="🚌 동탄2 버스 실시간 안내", layout="centered")

KST = pytz.timezone("Asia/Seoul")

# ✅ JSON 파일 경로
HOLIDAYS = {
    "2025-01-01", "2025-03-01", "2025-05-05", "2025-05-06",
    "2025-06-06", "2025-08-15", "2025-10-03", "2025-10-09", "2025-12-25"
}

# ✅ 실시간 처리
def get_now_kst():
    return datetime.now(KST)

def get_day_type(now):
    today_str = now.strftime("%Y-%m-%d")
    weekday = now.weekday()
    if today_str in HOLIDAYS or weekday == 6:
        return "holiday.json", "📅 일요일/공휴일"
    elif weekday == 5:
        return "saturday.json", "📅 토요일"
    else:
        return "weekday.json", "📅 평일"

# ✅ 캐시된 JSON 불러오기
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ 노선 정렬 기준
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# ✅ 실시간 틱톡 박스
placeholder = st.empty()

# ✅ 사용자 인터페이스
schedule_file, day_type = get_day_type(get_now_kst())
bus_data = load_schedule(f"downloads/{schedule_file}")
routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox(f"🚌 {day_type} 노선을 선택하세요:", routes)

# ✅ 실시간 갱신 루프
while True:
    now = get_now_kst()
    result_md = f"### ⏱️ 현재 시각: {now.strftime('%H:%M:%S')}\n\n"
    if selected_route:
        times = bus_data[selected_route]
        result = []
        for time_str in times:
            try:
                bus_time = datetime.strptime(time_str, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=KST
                )
                if bus_time < now:
                    bus_time += timedelta(days=1)
                diff = bus_time - now
                result.append((time_str, diff))
            except Exception as e:
                st.error(f"시간 파싱 오류: {time_str} → {e}")

        result = sorted(result, key=lambda x: x[1])[:3]
        for time_str, diff in result:
            total_sec = int(diff.total_seconds())
            minutes, seconds = divmod(total_sec, 60)
            if total_sec >= 3600:
                hours, minutes = divmod(minutes, 60)
                remain_str = f"{hours}시간 {minutes}분 {seconds}초 남음"
            else:
                remain_str = f"{minutes}분 {seconds}초 남음"
            icon = "⏰" if total_sec <= 600 else "⏳"
            result_md += f"- 🕒 **{time_str}** → {icon} **{remain_str}**\n"

    placeholder.markdown(result_md)
    time.sleep(1)
