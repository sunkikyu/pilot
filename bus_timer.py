import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# ✅ 페이지 설정 (맨 위에서 한 번만)
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ KST 기준 시간대 적용
tz_kst = pytz.timezone("Asia/Seoul")

# ✅ 타이틀
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

# ✅ 버스 스케줄 JSON 로드
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule("downloads/bus_schedule.json")

# ✅ 사용자 지정 정렬: M → G → 6 → 숫자순
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# ✅ 노선 선택
routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

# ✅ 현재 시각
now = datetime.now(tz=tz_kst).replace(microsecond=0)
st.markdown(f"🔑 현재 시간: `{now.strftime('%H:%M:%S')}`")

# ✅ 버스 시간 계산 및 필터링
if selected_route:
    times = bus_data[selected_route]
    result = []

    for time_str in times:
        try:
            time_str = time_str.strip()
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day,
                tzinfo=tz_kst
            )
            if bus_time < now:
                continue  # 이미 지난 버스는 제외

            diff = bus_time - now
            result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    # ✅ 남은 시간 기준 정렬 후 상위 3개만 출력
    result.sort(key=lambda x: x[1])
    result = result[:3]

    # ✅ 출력
    st.markdown(f"### 🕰️ **{selected_route}번 버스 남은 시간**")
    for time_str, diff in result:
        total_seconds = diff.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)

        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            formatted = f"{hours}시간 {minutes}분 {seconds}초 남음"
        else:
            formatted = f"{minutes}분 {seconds}초 남음"

        icon = "⏳" if diff.total_seconds() > 600 else "⏰"
        st.markdown(f"- 🕒 **{time_str}** → {icon} **{formatted}**")
