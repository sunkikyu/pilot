import streamlit as st
import json
from datetime import datetime, timedelta

# ✅ 가장 먼저 페이지 설정
st.set_page_config(page_title="버스 실시간 안내", layout="centered")

# ✅ JSON 로딩 함수
@st.cache_data
def load_schedule(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_schedule("bus_schedule.json")

# ✅ 타이틀
st.markdown("## 🚌 실시간 버스 기점 출발 안내")

# ✅ 사용자 정의 정렬 기준 함수
def custom_sort(key):
    if key.startswith("M"):
        return (0, key)
    elif key.startswith("G"):
        return (1, key)
    elif key.startswith("6"):
        return (2, key)
    else:
        return (3, key)

sorted_routes = sorted(bus_data.keys(), key=custom_sort)

# ✅ 노선 선택
route = st.selectbox("노선을 선택하세요:", options=sorted_routes)

# ✅ 현재 시간
now = datetime.now().time()

# ✅ 현재 시간보다 이후 출발만 필터링
upcoming = []
for t_str in bus_data[route]:
    try:
        t = datetime.strptime(t_str.strip(), "%H:%M").time()
        remaining = (
            datetime.combine(datetime.today(), t) - datetime.combine(datetime.today(), now)
        ).total_seconds()

        if remaining >= 0:
            upcoming.append((t_str, int(remaining)))
    except ValueError:
        st.error(f"시간 파싱 오류: {t_str} | time data '{t_str}' does not match format '%H:%M'")

# ✅ 정렬
upcoming.sort(key=lambda x: x[1])

# ✅ 표시
if not upcoming:
    st.info("오늘 남은 출발 시간이 없습니다.")
else:
    for t_str, sec in upcoming:
        m, s = divmod(sec, 60)
        emoji = "⏰" if sec < 600 else "🕒"
        st.markdown(f"- {emoji} **{t_str}** → ⏳ **{int(m)}분 {int(s)}초 남음**")