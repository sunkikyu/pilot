import streamlit as st
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

import json
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh
import holidays

# ⏱ 자동 새로고침 (60초 간격)
st_autorefresh(interval=60 * 1000, key="refresh")

# 🛠 한국 시간 기준
KST = pytz.timezone("Asia/Seoul")
now = datetime.now(KST)

# 📅 오늘 날짜 기준 요일 및 공휴일 판단
kr_holidays = holidays.KR()
if now.date() in kr_holidays or now.weekday() == 6:
    day_type = "holiday"
    label = "일요일/공휴일"
elif now.weekday() == 5:
    day_type = "saturday"
    label = "토요일"
else:
    day_type = "weekday"
    label = "평일"

# 🧾 제목 및 요일 정보
st.markdown("## 🚌 실시간 버스 기점 출발 안내")
st.markdown(f"🗓️ 오늘은 **{label}**입니다")

# 📂 요일별 JSON 로딩
def load_schedule(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

filename_map = {
    "weekday": "downloads/weekday.json",
    "saturday": "downloads/saturday.json",
    "holiday": "downloads/holiday.json"
}
bus_data = load_schedule(filename_map[day_type])

# 🧩 노선 정렬 함수
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# 🚏 노선 선택
routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

# 🕓 현재 시간
st.markdown(f"🔑 현재 시간: `{now.strftime('%H:%M:%S')}`")

# 🚌 남은 시간 계산 및 출력
if selected_route:
    result = []
    for time_str in bus_data[selected_route]:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=KST
            )
            if bus_time < now:
                continue  # 지난 시간 제외
            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    result.sort(key=lambda x: x[1])

    for time_str, diff in result[:3]:
        seconds = diff.seconds
        minutes = seconds // 60
        secs = seconds % 60

        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            display = f"{hours}시간 {minutes}분 {secs}초 남음"
        else:
            display = f"{minutes}분 {secs}초 남음"

        icon = "⏰" if seconds <= 600 else "⏳"
        st.markdown(f"- 🕒 **{time_str}** → {icon} **{display}**")
