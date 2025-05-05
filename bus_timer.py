import streamlit as st
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="버스 실시간 안내", layout="centered")
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

# 🚩 버스 스케줄 JSON 로드
@st.cache_data
def load_schedule(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule("downloads/bus_schedule.json")

# 🚩 사용자 지정 정렬 로직
def custom_sort_key(route):
    if route.startswith("M"):
        return (0, route)
    elif route.startswith("G"):
        return (1, route)
    elif route.startswith("6"):
        return (2, route)
    else:
        return (3, route)

# 🚩 노선 선택 UI
routes = sorted(bus_data.keys(), key=custom_sort_key)
selected_route = st.selectbox("노선을 선택하세요:", routes)

# 🚩 JS로 모바일 키보드 자동 최소화
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

# 🚩 시간 필터링 및 출력
if selected_route:
    times = bus_data[selected_route]
    now = datetime.now().replace(microsecond=0)

    result = []
    for time_str in times:
        try:
            bus_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
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
