import streamlit as st
from streamlit_autorefresh import st_autorefresh
import json
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# 🚩 오토 리프레시 (매 10초)
st_autorefresh(interval=10 * 1000, key="auto_refresh")

# 🚩 오늘 요일 판단
today = datetime.now()
weekday = today.weekday()
if weekday == 5:
    schedule_file = "downloads/saturday.json"
    today_label = "📅 오늘은 토요일입니다"
elif weekday == 6:
    schedule_file = "downloads/holiday.json"
    today_label = "📅 오늘은 일요일입니다"
else:
    schedule_file = "downloads/weekday.json"
    today_label = "📅 오늘은 평일입니다"

st.markdown("## 🚌 실시간 버스 기점 출발 안내")
st.markdown(today_label)

# 🚩 버스 스케줄 JSON 파일 로드
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(schedule_file)

# 🚩 사용자 지정 정렬
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("", routes)

# 🚩 현재 시간 기준 정렬 및 필터링
if selected_route:
    times = bus_data[selected_route]
    now = datetime.now().replace(microsecond=0)

    result = []
    for time_str in times:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if bus_time < now:
                continue  # 지난 버스는 무시
            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    result.sort(key=lambda x: x[1])
    result = result[:3]  # 상위 3개만 표시

    for time_str, diff in result:
        total_minutes = diff.total_seconds() // 60
        minutes = int(diff.total_seconds() // 60)
        seconds = int(diff.total_seconds() % 60)
        icon = "⏳" if minutes > 10 else "⏰"

        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            st.markdown(f"- 🕒 **{time_str}** → {icon} **{int(hours)}시간 {int(mins)}분 {seconds}초 남음**")
        else:
            st.markdown(f"- 🕒 **{time_str}** → {icon} **{minutes}분 {seconds}초 남음**")
