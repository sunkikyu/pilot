import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(page_title="버스 실시간 안내", layout="centered")

st.markdown("## 🚌 실시간 버스 기점 출발 안내")
st.write("노선을 선택하세요:")

# 🚩 버스 스케줄 JSON 파일 로드
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule("downloads/bus_schedule.json")

# 🚩 사용자 지정 정렬 로직
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# 🚩 노선 목록 표시 및 선택
routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

# 🚩 현재 시각 기준 정렬된 시간 리스트
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
                bus_time += timedelta(days=1)  # 이미 지난 시간은 다음날로
            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    # 🚩 남은 시간 기준 정렬
    result.sort(key=lambda x: x[1])

    # 🚩 시각별 출력
    for time_str, diff in result:
        minutes = diff.seconds // 60
        seconds = diff.seconds % 60
        icon = "⏳" if minutes > 10 else "⏰"
        st.markdown(f"- 🕒 **{time_str}** → {icon} **{minutes}분 {seconds}초 남음**")
