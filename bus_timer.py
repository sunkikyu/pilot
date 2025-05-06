import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from korean_holidays import is_korean_holiday
import time

# ✅ 페이지 구성은 제일 위에!
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ 타이틀 및 현재 요일/공휴일 여부
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

# ✅ 한국 시간으로 현재 시각
kst = pytz.timezone("Asia/Seoul")
now = datetime.now(kst)
today = now.date()
weekday = now.weekday()

# ✅ 평일/토/일공휴일 구분
if is_korean_holiday(today):
    day_type = "holiday"
    st.markdown("📅 **오늘은 일요일/공휴일입니다**")
elif weekday == 5:
    day_type = "saturday"
    st.markdown("📅 **오늘은 토요일입니다**")
else:
    day_type = "weekday"
    st.markdown("📅 **오늘은 평일입니다**")

# ✅ 현재 시각 표시 (틱톡)
st.markdown("### 🧑‍💻 현재 시각: " + f"🟢 `{now.strftime('%H:%M:%S')}`")
time.sleep(1)

# ✅ JSON 파일 로드
file_map = {
    "weekday": "downloads/weekday.json",
    "saturday": "downloads/saturday.json",
    "holiday": "downloads/holiday.json"
}

@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(file_map[day_type])

# ✅ 노선 정렬 기준 (M, G, 숫자 순서)
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route[0].isdigit():
        return (2, route)
    else:
        return (3, route)

routes = sorted(bus_data.keys(), key=custom_sort_key)

# ✅ 노선 선택
selected_route = st.selectbox(f"🚌 { '일요일/공휴일' if day_type == 'holiday' else '토요일' if day_type == 'saturday' else '평일' } 노선을 선택하세요:", routes)

# ✅ 시간 계산 및 표시
if selected_route:
    times = bus_data[selected_route]
    now = datetime.now(kst).replace(microsecond=0)
    result = []

    for time_str in times:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=kst
            )
            if bus_time < now:
                continue  # 이미 지난 시간 제외
            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    # ⏱ 상위 3개만 표시
    result = sorted(result, key=lambda x: x[1])[:3]

    # ✅ 출력
    st.markdown(f"### 🕰 **{selected_route}번 버스 남은 시간**")
    for time_str, diff in result:
        total_seconds = diff.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        icon = "⏰" if hours == 0 and minutes <= 10 else "⏳"
        if hours >= 1:
            remain_str = f"{hours}시간 {minutes}분 {seconds}초 남음"
        else:
            remain_str = f"{minutes}분 {seconds}초 남음"

        st.markdown(f"- 🕒 **{time_str}** → {icon} **{remain_str}**")
