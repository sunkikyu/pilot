from pytz import timezone
import streamlit as st
import json
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="버스 실시간 안내", layout="centered")
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule("downloads/bus_schedule.json")

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
selected_route = st.selectbox("노선을 선택하세요:", routes)

# 모바일 키보드 최소화
st.components.v1.html("""
<script>
const dropdown = window.parent.document.querySelector('select');
if (dropdown) {
  dropdown.addEventListener('change', () => {
    document.activeElement.blur();
  });
}
</script>
""", height=0)

if selected_route:
    times = bus_data[selected_route]

    # 한국 시간 기준으로 now 설정
    tz_kst = timezone("Asia/Seoul")
    now = datetime.now(tz_kst).replace(microsecond=0)
    st.caption(f"📍 현재 시간: {now.strftime('%H:%M:%S')}")

    result = []
    for time_str in times:
        try:
            time_str = time_str.strip()  # ← 공백 제거
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day,
                tzinfo=tz_kst  # ← 반드시 KST로 맞추기
            )
            if bus_time >= now:
                diff = bus_time - now
                result.append((time_str, diff))
        except Exception as e:
            st.error(f"시간 파싱 오류: {time_str} | {e}")

    result.sort(key=lambda x: x[1])
    top_three = result[:3]

    for time_str, diff in top_three:
        total_sec = int(diff.total_seconds())
        if total_sec >= 3600:
            hours = total_sec // 3600
            minutes = (total_sec % 3600) // 60
            seconds = total_sec % 60
            icon = "🕰️"
            st.markdown(f"- **{time_str}** → {icon} **{hours}시간 {minutes}분 {seconds}초 남음**")
        else:
            minutes = total_sec // 60
            seconds = total_sec % 60
            icon = "⏰" if minutes <= 10 else "⏳"
            st.markdown(f"- **{time_str}** → {icon} **{minutes}분 {seconds}초 남음**")
