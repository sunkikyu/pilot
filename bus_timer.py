import streamlit as st
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="버스 실시간 안내", layout="centered")
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

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
selected_route = st.selectbox("노선을 선택하세요", routes)

# 🚩 시간 계산 및 표시
if selected_route:
    st.markdown(f"### 🕒 **{selected_route}번 버스 남은 시간**")
    now = datetime.now().replace(microsecond=0)
    result = []

    for time_str in bus_data[selected_route]:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )

            # 이미 지난 시간 또는 지금 시각은 제외
            if bus_time <= now:
                continue

            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    # 남은 시간 기준 정렬 후 상위 3개만 표시
    result.sort(key=lambda x: x[1])
    result = result[:3]

    for time_str, diff in result:
        total_seconds = diff.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        icon = "⏳" if minutes > 10 else "⏰"

        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            st.markdown(f"- 🕒 **{time_str}** → {icon} **{hours}시간 {minutes}분 {seconds}초 남음**")
        else:
            st.markdown(f"- 🕒 **{time_str}** → {icon} **{minutes}분 {seconds}초 남음**")
