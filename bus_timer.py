import streamlit as st
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time
import holidays

# ✅ 한국 시간대 설정
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)

# ✅ 한국 공휴일 체크 함수
def is_korean_holiday(date):
    kr_holidays = holidays.KR(years=date.year)
    return date.weekday() == 6 or date in kr_holidays

# ✅ 날짜별 JSON 파일 경로 결정
def get_schedule_file():
    today = datetime.now(KST).date()
    weekday = today.weekday()
    if is_korean_holiday(today):
        return "downloads/holiday.json", "📅 오늘은 일요일/공휴일입니다"
    elif weekday == 5:
        return "downloads/saturday.json", "📅 오늘은 토요일입니다"
    else:
        return "downloads/weekday.json", "📅 오늘은 평일입니다"

# ✅ JSON 파일 로드 함수
@st.cache_data
def load_schedule(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ Streamlit 설정은 맨 처음에 위치해야 함
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ 오늘 날짜 기준 정보
file_path, today_label = get_schedule_file()
bus_data = load_schedule(file_path)

# ✅ 노선 정렬 기준 설정
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

# ✅ Streamlit UI
st.markdown("""
    <h1 style='font-size: 36px;'>🚌 실시간 버스 기점 출발 안내</h1>
""", unsafe_allow_html=True)

st.markdown(f"### {today_label}")

# ✅ 실시간 시간 표시
current_time_placeholder = st.empty()

# ✅ 노선 선택
selected_route = st.selectbox("🚌 노선을 선택하세요:", routes)

# ✅ 실시간 남은 시간 틱톡 방식으로 업데이트
time_placeholder = st.empty()

while True:
    now = datetime.now(KST)
    current_time_placeholder.markdown(f"### 👨\u200d💻 현재 시각: <span style='color:green'>{now.strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

    result = []
    for time_str in bus_data[selected_route]:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=KST
            )
            if bus_time < now:
                bus_time += timedelta(days=1)
            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            continue

    result.sort(key=lambda x: x[1])
    display = ""
    for time_str, diff in result[:3]:
        total_seconds = int(diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        icon = "⏰" if total_seconds <= 600 else "⏳"
        if total_seconds >= 3600:
            remain = f"{hours}시간 {minutes}분 {seconds}초 남음"
        else:
            remain = f"{minutes}분 {seconds}초 남음"
        display += f"- 🕒 <b>{time_str}</b> → {icon} <b>{remain}</b><br>"

    time_placeholder.markdown(f"### 🕰️ <b>{selected_route}</b>번 버스 남은 시간\n<br>{display}", unsafe_allow_html=True)
    time.sleep(1)
