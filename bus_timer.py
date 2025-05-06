import streamlit as st
import json
from datetime import datetime, timedelta, date
import time
import platform
import holidays

# ✅ 페이지 설정 (최상단에 위치해야 함)
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ 한글 공휴일 설정
kr_holidays = holidays.KR()

def get_today_type():
    today = date.today()
    if today in kr_holidays or today.weekday() == 6:
        return "holiday"
    elif today.weekday() == 5:
        return "saturday"
    else:
        return "weekday"

# ✅ 요일 표시
today_type = get_today_type()
today_text = {
    "weekday": "📅 오늘은 평일입니다",
    "saturday": "📅 오늘은 토요일입니다",
    "holiday": "📅 오늘은 일요일/공휴일입니다"
}
st.markdown(f"### {today_text[today_type]}")

# ✅ 현재 시간 표시
with st.container():
    current_time_placeholder = st.empty()

# ✅ JSON 경로 지정
json_path = {
    "weekday": "downloads/weekday.json",
    "saturday": "downloads/saturday.json",
    "holiday": "downloads/holiday.json"
}
with open(json_path[today_type], "r", encoding="utf-8") as f:
    bus_data = json.load(f)

# ✅ 사용자 지정 정렬 (M → G → 숫자)
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route[0].isdigit():
        return (2, route)
    return (3, route)

routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

# ✅ 실시간 남은 시간 계산 함수
def get_remaining_times(times):
    now = datetime.now()
    upcoming = []
    for t_str in times:
        try:
            t = datetime.strptime(t_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if t < now:
                continue  # 이미 지난 시간은 제외
            delta = t - now
            upcoming.append((t_str, delta))
        except:
            continue
    return upcoming[:3]  # 상위 3개만

# ✅ 출력 루프 (틱톡)
if selected_route:
    st.markdown(f"### 🕰️ {selected_route}번 버스 남은 시간")
    slot = st.empty()

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        current_time_placeholder.markdown(f"#### 🧑‍💻 현재 시각: <span style='color:green'>{now}</span>", unsafe_allow_html=True)

        upcoming = get_remaining_times(bus_data[selected_route])
        with slot.container():
            for time_str, diff in upcoming:
                seconds = diff.seconds
                if seconds >= 3600:
                    h = seconds // 3600
                    m = (seconds % 3600) // 60
                    s = seconds % 60
                    remaining = f"{h}시간 {m}분 {s}초 남음"
                else:
                    m = seconds // 60
                    s = seconds % 60
                    remaining = f"{m}분 {s}초 남음"
                icon = "⏳" if seconds > 600 else "⏰"
                st.markdown(f"- 🕒 **{time_str}** → {icon} **{remaining}**")
        time.sleep(1)
