import streamlit as st
import json
from datetime import datetime, timedelta, timezone
import holidays
import time

# ✅ 페이지 설정 (가장 위에 위치해야 함)
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ 한국 시간대
KST = timezone(timedelta(hours=9))

# ✅ 오늘 날짜 정보
now = datetime.now(KST)
today = now.date()
weekday = today.weekday()
kr_holidays = holidays.KR()

# ✅ 요일/공휴일 판단
if today in kr_holidays or weekday == 6:
    schedule_type = "holiday"
    st.markdown("📅 <b>오늘은 일요일/공휴일입니다</b>", unsafe_allow_html=True)
elif weekday == 5:
    schedule_type = "saturday"
    st.markdown("📅 <b>오늘은 토요일입니다</b>", unsafe_allow_html=True)
else:
    schedule_type = "weekday"
    st.markdown("📅 <b>오늘은 평일입니다</b>", unsafe_allow_html=True)

st.divider()

# ✅ 버스 데이터 로딩
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

path_map = {
    "weekday": "weekday.json",
    "saturday": "saturday.json",
    "holiday": "holiday.json"
}
bus_data = load_schedule(path_map[schedule_type])

# ✅ 사용자 정의 정렬 (M > G > 숫자)
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
selected_route = st.selectbox("노선을 선택하세요:", routes)

# ✅ 실시간 남은 시간 틱톡 업데이트
placeholder = st.empty()

while True:
    with placeholder.container():
        now = datetime.now(KST)
        st.markdown(f"#### 🧑‍💻 현재 시각: <span style='color:green'>{now.strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

        if selected_route:
            results = []
            for time_str in bus_data[selected_route]:
                try:
                    t = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day, tzinfo=KST)
                    if t < now:
                        continue  # 지나간 시간 제거
                    diff = t - now
                    results.append((time_str, diff))
                except:
                    continue

            results = sorted(results, key=lambda x: x[1])[:3]

            st.markdown(f"### ⏰ <b>{selected_route}</b>번 버스 남은 시간", unsafe_allow_html=True)

            for time_str, diff in results:
                total_sec = int(diff.total_seconds())
                h, m = divmod(total_sec, 3600)
                m, s = divmod(m, 60)
                icon = "⏰" if total_sec <= 600 else "⏳"
                if h >= 1:
                    msg = f"{h}시간 {m}분 {s}초"
                else:
                    msg = f"{m}분 {s}초"
                st.markdown(f"- 🕒 <b>{time_str}</b> → {icon} <b>{msg} 남음</b>", unsafe_allow_html=True)
    time.sleep(1)
