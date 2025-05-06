import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import json
import holidays
import pytz

# ✅ 페이지 설정 (맨 첫 줄에서 설정)
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ 한국 시간대
KST = pytz.timezone("Asia/Seoul")
now = datetime.now(KST)

# ✅ 자동 새로고침 (60초 간격)
st_autorefresh(interval=60 * 1000, key="refresh")

# ✅ 오늘이 평일 / 토요일 / 일요일 or 공휴일 인지 판별
ko_holidays = holidays.KR()
is_holiday = now.date() in ko_holidays
weekday = now.weekday()

if is_holiday or weekday == 6:
    schedule_file = "downloads/holiday.json"
    label = "📅 오늘은 일요일/공휴일입니다"
elif weekday == 5:
    schedule_file = "downloads/saturday.json"
    label = "📅 오늘은 토요일입니다"
else:
    schedule_file = "downloads/weekday.json"
    label = "📅 오늘은 평일입니다"

st.title("🚌 실시간 버스 기점 출발 안내")
st.markdown(f"**{label}**")
st.markdown("---")

# ✅ 현재 시각 표시
st.markdown(f"🧑‍💻 **현재 시각:**  `{now.strftime('%H:%M:%S')}`")

# ✅ JSON 로드 함수
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

schedule_data = load_schedule(schedule_file)

# ✅ 사용자 지정 정렬 기준 (M → G → 6 → 기타)
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

routes = sorted(schedule_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

if selected_route:
    st.markdown(f"## 🕰️ **{selected_route}번 버스 남은 시간**")
    now = datetime.now(KST)

    times = schedule_data[selected_route]
    upcoming = []
    for t in times:
        try:
            bus_time = datetime.strptime(t, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=KST
            )
            if bus_time < now:
                continue  # 지난 시간은 제외

            diff = bus_time - now
            upcoming.append((t, diff))
        except Exception as e:
            st.error(f"{t} 시간 오류: {e}")

    upcoming = sorted(upcoming, key=lambda x: x[1])[:3]  # 상위 3개만 출력

    for t, diff in upcoming:
        total_seconds = int(diff.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            formatted = f"{hours}시간 {mins}분 {seconds}초"
        else:
            formatted = f"{minutes}분 {seconds}초"

        icon = "⏰" if minutes <= 10 else "⏳"
        st.markdown(f"- 🕒 **{t}** → {icon} **{formatted} 남음**")
