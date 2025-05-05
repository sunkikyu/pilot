from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# 🚌 검색할 버스 번호
bus_number = "M4434"

# ✅ 자동으로 크롬드라이버 설치 및 실행
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 필요 시 사용
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://www.gbis.go.kr/gbis2022/schBusResult.do")
    time.sleep(2)

    # 버스번호 입력 및 검색
    search_input = driver.find_element(By.ID, "searchBusKeyword")
    search_input.send_keys(bus_number)
    search_input.send_keys(Keys.RETURN)
    time.sleep(2)

    # 첫 번째 검색 결과 클릭
    first_result = driver.find_element(By.CSS_SELECTOR, ".result-list ul li a")
    first_result.click()
    time.sleep(2)

    # 기점 방향 시간표 클릭
    direction_tab = driver.find_element(By.CSS_SELECTOR, ".time-table-direction ul li:nth-child(1) a")
    direction_tab.click()
    time.sleep(1)

    # 시간표 테이블 출력
    table = driver.find_element(By.CSS_SELECTOR, ".time-table-wrap tbody")
    rows = table.find_elements(By.TAG_NAME, "tr")

    print(f"\n🚌 [{bus_number}] 기점 시간표:")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        times = [col.text.strip() for col in cols if col.text.strip()]
        print(" | ".join(times))

finally:
    driver.quit()
