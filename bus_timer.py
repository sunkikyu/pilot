import streamlit as st
import json
from datetime import datetime, timedelta
from pytz import timezone

tz_kst = timezone("Asia/Seoul")
now = datetime.now(tz_kst).replace(microsecond=0)

st.set_page_config(page_title="버스 실시간 안내", layout="centered")
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule("downloads/bus_schedule.json")

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

st.markdown(f"🔑 현재 시간: <span style='color:green;'>{now.strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

if selected_route:
    result = []

    for time_str in bus_data[selected_route]:
        try:
            # 문자열 → 시간 (naive)
            bus_time_naive = datetime.strptime(time_str.strip(), "%H:%M").time()
            # 오늘 날짜 기준 datetime 객체 생성
            bus_datetime = datetime.combine(now.date(), bus_time_naive)
            bus_datetime = tz_kst.localize(bus_datetime)

            # 이미 지난 버스는 제외
            if bus_datetime <= now:
                continue

            diff = bus_datetime - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    result.sort(key=lambda x: x[1])
    result = result[:3]

    st.markdown(f"🕰 **{selected_route}번 버스 남은 시간**")

    for time_str, diff in result:
        total_seconds = int(diff.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            icon = "⏳"
            display = f"{hours}시간 {mins}분 {seconds}초 남음"
        else:
            icon = "⏰" if minutes <= 10 else "⏳"
            display = f"{minutes}분 {seconds}초 남음"

        st.markdown(f"- 🕒 **{time_str}** → {icon} **{display}**")
