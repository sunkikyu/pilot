import streamlit as st
import json
from datetime import datetime, timedelta
import pytz
from korean_holidays import is_korean_holiday
import time

# ✅ 페이지 설정 (최상단에서 실행)
st.set_page_config(page_title="실시간 버스 기점 출발 안내", layout="centered")

# ✅ 현재 시각 (KST)
kst = pytz.timezone("Asia/Seoul")
now = datetime.now(kst)

# ✅ 요일 판단 및 공휴일 확인
weekday = now.weekday()  # 0: 월요일 ~ 6: 일요일
today = now.date()

if is_korean_holiday(today) or weekday == 6:
    mode = "holiday"
    label = "📅 오늘은 일요일/공휴일입니다"
elif weekday == 5:
    mode = "saturday"
    label = "📅 오늘은 토요일입니다"
else:
    mode = "weekday"
    label = "📅 오늘은 평일입니다"

st.title("🚌 실시간 버스 기점 출발 안내")
st.markdown(f"### {label}")
st.markdown(f"#### 👨‍💻 현재 시각: <span style='color:green'>{now.strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

# ✅ JSON 로드 함수
@st.cache_data
def load_schedule(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule(f"downloads/{mode}.json")

# ✅ 사용자 지정 정렬
def sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# ✅ 노선 선택
routes = sorted(bus_data.keys(), key=sort_key)
selected = st.selectbox("🚌 " + label + " 노선을 선택하세요:", routes)

# ✅ 실시간 남은 시간 계산 및 출력
if selected:
    now = datetime.now(kst).replace(microsecond=0)
    times = bus_data[selected]
    future_times = []

    for t in times:
        try:
            h, m = map(int, t.strip().split(":"))
            bus_time = now.replace(hour=h, minute=m, second=0)

            if bus_time < now:
                continue  # 지나간 시간은 제외

            diff = bus_time - now
            future_times.append((t, diff))

        except Exception as e:
            continue

    future_times = sorted(future_times, key=lambda x: x[1])[:3]

    st.markdown(f"### 🕰️ {selected}번 버스 남은 시간")
    for time_str, diff in future_times:
        total_sec = int(diff.total_seconds())
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        seconds = total_sec % 60

        if total_sec <= 600:
            icon = "⏰"
        else:
            icon = "⏳"

        if hours >= 1:
            st.markdown(f"- 🕒 {time_str} → {icon} **{hours}시간 {minutes}분 {seconds}초 남음**")
        else:
            st.markdown(f"- 🕒 {time_str} → {icon} **{minutes}분 {seconds}초 남음**")

    # ✅ 틱톡식 실시간 업데이트
    time.sleep(1)
    st.experimental_rerun()
