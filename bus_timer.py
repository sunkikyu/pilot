import streamlit as st
import json
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ⏱️ 페이지 새로고침 주기 (ms 단위) → 1000ms = 1초
st_autorefresh(interval=1000, limit=None, key="refresh")

st.set_page_config(page_title="버스 실시간 안내", layout="centered")
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

# ✅ 요일 기준 JSON 파일 결정
def get_schedule_filename():
    today = datetime.now()
    weekday = today.weekday()
    if weekday == 5:
        return "downloads/saturday.json"
    elif weekday == 6:
        return "downloads/holiday.json"
    else:
        return "downloads/weekday.json"

@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(get_schedule_filename())

# ✅ 사용자 지정 정렬 우선순위
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
selected_route = st.selectbox("노선을 선택하세요:", routes, label_visibility="collapsed")

# ✅ 현재 시각 기준 정렬된 버스 시간 리스트
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
                continue  # 지난 버스는 건너뜀
            diff = bus_time - now
            result.append((time_str, diff))
        except Exception:
            continue

    # 남은 시간 기준으로 정렬 후 상위 3개만 표시
    result = sorted(result, key=lambda x: x[1])[:3]

    st.markdown("### ⏱️ 다음 버스 시간")
    for time_str, diff in result:
        total_seconds = int(diff.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        if total_seconds >= 3600:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            display = f"{hours}시간 {minutes}분 {seconds}초 남음"
        else:
            display = f"{minutes}분 {seconds}초 남음"

        icon = "⏳" if minutes > 10 else "⏰"
        st.markdown(f"- 🕒 **{time_str}** → {icon} **{display}**")
