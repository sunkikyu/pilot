import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
from pathlib import Path
import json
import pytz
import holidays

# ⏱ 페이지 설정은 가장 먼저 실행되어야 함
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# 🔁 자동 새로고침 (5초마다 리프레시)
st_autorefresh(interval=5 * 1000, key="datarefresh")

# 🇰🇷 한국 시간 설정
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)

# 📅 오늘 요일 및 공휴일 판단
weekday = now.weekday()
kr_holidays = holidays.KR()
today_type = (
    "holiday"
    if now.date() in kr_holidays or weekday == 6
    else "saturday" if weekday == 5
    else "weekday"
)

# 📁 JSON 파일 경로
json_paths = {
    "weekday": "downloads/weekday.json",
    "saturday": "downloads/saturday.json",
    "holiday": "downloads/holiday.json",
}

# 🧾 JSON 로딩 함수
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(json_paths[today_type])

# 📌 날짜 설명 표시
day_label = {"weekday": "평일", "saturday": "토요일", "holiday": "일요일/공휴일"}
st.markdown(f"### 🗓️ 오늘은 **{day_label[today_type]}**입니다")

# 🚌 사용자 지정 노선 정렬
def custom_sort(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    return (3, route)

routes = sorted(bus_data.keys(), key=custom_sort)
selected = st.selectbox("노선을 선택하세요:", routes)

# 🕒 현재 시간 표시
st.markdown(f"#### 🕵️ 현재 시각: `{now.strftime('%H:%M:%S')}`")

# 🧮 남은 시간 계산 및 출력
if selected:
    times = bus_data[selected]
    upcoming = []

    for time_str in times:
        try:
            target = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=korea
            )
            if target < now:
                continue  # 이미 지난 시간은 제외

            delta = target - now
            minutes = delta.seconds // 60
            seconds = delta.seconds % 60

            if delta.total_seconds() > 3600:
                hours = minutes // 60
                minutes = minutes % 60
                remain_str = f"{hours}시간 {minutes}분 {seconds}초"
            else:
                remain_str = f"{minutes}분 {seconds}초"

            icon = "⏰" if minutes <= 10 else "⏳"
            upcoming.append((time_str, remain_str, icon))
        except Exception as e:
            continue

    if upcoming:
        st.markdown(f"### 🕰️ **{selected}번 버스 남은 시간**")
        for time_str, remain, icon in upcoming[:3]:  # 3개만 표시
            st.markdown(f"- 🕒 **{time_str}** → {icon} **{remain} 남음**")
    else:
        st.info("오늘 이후 남은 버스가 없습니다.")
