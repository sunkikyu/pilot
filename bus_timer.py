import streamlit as st
from streamlit_autorefresh import st_autorefresh
import json
from datetime import datetime, timedelta, date
import pytz
import holidays

# ✅ 반드시 제일 먼저 페이지 설정
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ 한국 시간 설정
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)

# ✅ 자동 새로고침 (5초 간격)
st_autorefresh(interval=5 * 1000, key="refresh")

# ✅ 오늘이 평일/토요일/일요일(공휴일)인지 판단
kr_holidays = holidays.KR()
is_weekend = now.weekday() >= 5  # 5 = 토요일, 6 = 일요일
is_holiday = date.today() in kr_holidays

if is_holiday or now.weekday() == 6:
    day_type = "holiday"
    label = "📅 오늘은 일요일/공휴일입니다"
elif now.weekday() == 5:
    day_type = "saturday"
    label = "📅 오늘은 토요일입니다"
else:
    day_type = "weekday"
    label = "📅 오늘은 평일입니다"

st.markdown(f"### {label}")

# ✅ JSON 파일 로드
def load_schedule(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

schedule = load_schedule(f"downloads/{day_type}.json")

# ✅ 노선 선택
route = st.selectbox("노선을 선택하세요:", sorted(schedule.keys()))

# ✅ 현재 시각 출력
st.markdown(f"#### 🕵️ 현재 시각: `{now.strftime('%H:%M:%S')}`")

# ✅ 남은 시간 계산 및 표시
if route:
    times = schedule[route]
    upcoming = []

    for time_str in times:
        try:
            # 문자열을 datetime 객체로 변환 후 tz 부여
            bus_time_naive = datetime.strptime(time_str, "%H:%M")
            bus_time = korea.localize(datetime.combine(now.date(), bus_time_naive.time()))

            # 이미 지난 버스는 건너뜀
            if bus_time < now:
                continue

            delta = bus_time - now
            minutes = delta.seconds // 60
            seconds = delta.seconds % 60

            if delta.total_seconds() > 3600:
                hours = minutes // 60
                minutes %= 60
                remain_str = f"{hours}시간 {minutes}분 {seconds}초"
            else:
                remain_str = f"{minutes}분 {seconds}초"

            icon = "⏰" if delta.total_seconds() <= 600 else "⏳"
            upcoming.append((time_str, remain_str, icon))

        except Exception as e:
            continue

    st.markdown(f"### 🕰️ {route}번 버스 남은 시간")
    for t, remain, icon in upcoming[:3]:
        st.markdown(f"- 🕒 **{t}** → {icon} **{remain} 남음**")
