import streamlit as st
import json
from datetime import datetime, timedelta
import pandas as pd
import platform

st.set_page_config(page_title="버스 실시간 안내", layout="centered")

st.markdown("## 🚌 실시간 버스 기점 출발 안내")

# ✅ 요일에 따라 파일명 결정
def get_schedule_filename():
    today = datetime.now()
    weekday = today.weekday()
    if weekday == 5:  # 토요일
        return "downloads/saturday.json"
    elif weekday == 6:  # 일요일
        return "downloads/holiday.json"
    else:
        return "downloads/weekday.json"

# ✅ JSON 불러오기
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(get_schedule_filename())

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

routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

if selected_route:
    times = bus_data[selected_route]
    now = datetime.now().replace(second=0, microsecond=0)
    result = []

    for time_str in times:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if bus_time < now:
                continue  # 이미 지난 시간은 제외

            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    # 가까운 시간 순으로 정렬 후 상위 3개만 출력
    result = sorted(result, key=lambda x: x[1])[:3]

    for time_str, diff in result:
        total_minutes = diff.total_seconds() // 60
        seconds = int(diff.total_seconds() % 60)

        if total_minutes > 60:
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            display = f"{hours}시간 {minutes}분 {seconds}초 남음"
        else:
            minutes = int(total_minutes)
            display = f"{minutes}분 {seconds}초 남음"

        icon = "⏳" if total_minutes > 10 else "⏰"
        st.markdown(f"- 🕒 **{time_str}** → {icon} **{display}**")
