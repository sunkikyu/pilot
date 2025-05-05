import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import pytz

st.set_page_config(page_title="버스 실시간 안내", layout="centered")
tz_kst = pytz.timezone("Asia/Seoul")

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

now = datetime.now(tz=tz_kst).replace(microsecond=0)
st.markdown(f"🔑 현재 시간: `{now.strftime('%H:%M:%S')}`")

if selected_route:
    times = bus_data[selected_route]
    result = []

    for time_str in times:
        try:
            # 현재 날짜와 조합해 datetime 생성 후, KST 적용
            time_obj = datetime.strptime(time_str.strip(), "%H:%M").time()
            bus_time = tz_kst.localize(datetime.combine(now.date(), time_obj))

            if bus_time <= now:
                continue

            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    result.sort(key=lambda x: x[1])
    result = result[:3]

    st.markdown(f"### 🕰️ **{selected_route}번 버스 남은 시간**")
    for time_str, diff in result:
        total_seconds = int(diff.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            formatted = f"{hours}시간 {minutes}분 {seconds}초 남음"
        else:
            formatted = f"{minutes}분 {seconds}초 남음"

        icon = "⏳" if total_seconds > 600 else "⏰"
        st.markdown(f"- 🕒 **{time_str}** → {icon} **{formatted}**")
