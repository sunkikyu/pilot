import streamlit as st
import json
from datetime import datetime, timedelta
from pytz import timezone
from pathlib import Path

# 📌 페이지 설정 (가장 먼저 호출)
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ⏰ 한국 시간대 설정
tz_kst = timezone("Asia/Seoul")
now = datetime.now(tz_kst).replace(microsecond=0)

# 🚩 JSON 로드 (캐시 사용)
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule("downloads/bus_schedule.json")

# 🧭 사용자 정의 정렬 함수
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# 🔽 노선 선택
routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

# 🕐 현재 시각 표시
st.markdown(f"🔑 현재 시간: <span style='color:green;'>{now.strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

# 🚍 선택된 노선 처리
if selected_route:
    times = bus_data[selected_route]
    result = []

    for time_str in times:
        try:
            # 시간 문자열 → datetime 객체로 변환 (오늘 날짜 기준)
            time_obj = datetime.strptime(time_str.strip(), "%H:%M").time()
            bus_time = tz_kst.localize(datetime.combine(now.date(), time_obj))

            # 이미 지난 버스는 무시
            diff = bus_time - now
            if diff.total_seconds() < 0:
                continue

            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    # 남은 시간 기준 정렬 & 상위 3개만 표시
    result.sort(key=lambda x: x[1])
    result = result[:3]

    # 결과 출력
    st.markdown(f"🕰️ **{selected_route}번 버스 남은 시간**")

    for time_str, diff in result:
        total_seconds = int(diff.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        # 60분 이상일 경우: 시간 단위로 표시
        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            icon = "⏳"
            remaining = f"{hours}시간 {mins}분 {seconds}초 남음"
        else:
            icon = "⏰" if minutes <= 10 else "⏳"
            remaining = f"{minutes}분 {seconds}초 남음"

        st.markdown(f"- 🕒 **{time_str}** → {icon} **{remaining}**")
