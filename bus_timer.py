from datetime import datetime, timedelta, timezone
import streamlit as st
import json
import holidays

# ✅ 한국 시간대
KST = timezone(timedelta(hours=9))

# ✅ Streamlit 페이지 설정 (맨 첫줄)
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ 한국 공휴일 처리
kr_holidays = holidays.KR()
today = datetime.now(KST).date()
weekday = today.weekday()

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

# ✅ 현재 시각 출력
now_kst = datetime.now(KST)
st.markdown(f"#### 🧑‍💻 현재 시각: <span style='color:green'>{now_kst.strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

# ✅ 버스 데이터 불러오기
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

# ✅ 정렬: M → G → 숫자순
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

# ✅ 남은 시간 계산 및 출력
if selected_route:
    now = datetime.now(KST)
    result = []

    for time_str in bus_data[selected_route]:
        try:
            t = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=KST
            )
            if t < now:
                continue  # 지나간 시간은 제외
            diff = t - now
            result.append((time_str, diff))
        except Exception as e:
            continue

    result.sort(key=lambda x: x[1])
    result = result[:3]  # 최대 3건 출력

    st.markdown(f"### 🕰️ <b>{selected_route}</b>번 버스 남은 시간", unsafe_allow_html=True)

    for time_str, diff in result:
        total_sec = int(diff.total_seconds())
        h, m = divmod(total_sec, 3600)
        m, s = divmod(m, 60)
        icon = "⏰" if total_sec <= 600 else "⏳"
        if h >= 1:
            msg = f"{h}시간 {m}분 {s}초"
        else:
            msg = f"{m}분 {s}초"
        st.markdown(f"- 🕒 <b>{time_str}</b> → {icon} <b>{msg} 남음</b>", unsafe_allow_html=True)
