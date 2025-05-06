import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

# ✅ 페이지 설정 (무조건 제일 위에!)
st.set_page_config(page_title="🚌 동탄2 버스 실시간 안내", layout="centered")

# ✅ 현재 한국 시각
KST = ZoneInfo("Asia/Seoul")
now = datetime.now(KST)
today = now.date()
weekday = now.weekday()  # 0:월 ~ 6:일
today_str = today.strftime("%Y-%m-%d")

# ✅ 공휴일 목록 (필요 시 갱신)
KOREAN_HOLIDAYS = {
    "2025-01-01", "2025-03-01", "2025-05-05", "2025-05-06",
    "2025-06-06", "2025-08-15", "2025-10-03", "2025-10-09", "2025-12-25"
}

# ✅ 요일 분기
if today_str in KOREAN_HOLIDAYS or weekday == 6:
    schedule_file = "downloads/holiday.json"
    day_type = "📅 일요일/공휴일"
elif weekday == 5:
    schedule_file = "downloads/saturday.json"
    day_type = "📅 토요일"
else:
    schedule_file = "downloads/weekday.json"
    day_type = "📅 평일"

# ✅ JSON 로드 함수
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(schedule_file)

# ✅ 노선 정렬 기준 함수
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# ✅ 노선 선택
routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox(f"🚌 {day_type} 노선을 선택하세요:", routes)

# ✅ 실시간 출력
if selected_route:
    st.markdown(f"### ⏱️ 현재 시각: {now.strftime('%H:%M:%S')}")
    times = bus_data[selected_route]
    upcoming = []

    for time_str in times:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=KST
            )
            if bus_time < now:
                bus_time += timedelta(days=1)

            diff = bus_time - now
            upcoming.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} → {e}")

    # 🚩 정렬 및 상위 3개
    upcoming = sorted(upcoming, key=lambda x: x[1])[:3]

    for time_str, diff in upcoming:
        total_sec = int(diff.total_seconds())
        minutes, seconds = divmod(total_sec, 60)

        if total_sec >= 3600:
            hours, minutes = divmod(minutes, 60)
            remain_str = f"{hours}시간 {minutes}분 {seconds}초 남음"
        else:
            remain_str = f"{minutes}분 {seconds}초 남음"

        icon = "⏰" if total_sec <= 600 else "⏳"
        st.markdown(f"- 🕒 **{time_str}** → {icon} **{remain_str}**")

    # 🚩 틱톡식 1초 갱신
    st.experimental_rerun()
