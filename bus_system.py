from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
import time
import os
import urllib.request
import urllib.parse
import re

# 파일 저장 폴더 설정
download_dir = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_dir, exist_ok=True)

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
}
options.add_experimental_option("prefs", prefs)

# Selenium 드라이버 개인조금
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# 시작 URL
driver.get("https://cafe.daum.net/kd4266/FJlw")
time.sleep(2)

# 목록 iframe 접속
wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "down")))
print("✅ iframe 전환 성공")

current_page = 1

while current_page <= 20:
    print(f"\n📄 {current_page}페이지 회복")

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.txt_item")))
        post_elements = driver.find_elements(By.CSS_SELECTOR, "a.txt_item")
        links = [elem.get_attribute("href") for elem in post_elements if elem.get_attribute("href")]

        for link in links:
            print(f"\n👉 게시글 방문: {link}")
            try:
                driver.get(link)
                time.sleep(2)

                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "down")))
                print("🔁 게시글 iframe 전환 성공")

                title_elem = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "article_title"))
                )
                title = title_elem.text.strip().replace("/", "_").replace(":", "-")
                print(f"📌 제목: {title}")

                virus_links = driver.find_elements(By.CSS_SELECTOR, 'a[href^="javascript:checkVirus"]')
                print(f"📎 첨부파일 수: {len(virus_links)}")

                downloaded_urls = set()

                for vlink in virus_links:
                    href = vlink.get_attribute("href")
                    if "url=" in href:
                        encoded_url = href.split("url=")[-1]
                        decoded_url = urllib.parse.unquote(encoded_url)
                        decoded_url = re.sub(r"[\'\);]+$", "", decoded_url.strip())

                        if decoded_url in downloaded_urls:
                            print(f"🔁 중복 URL 스킵: {decoded_url}")
                            continue

                        downloaded_urls.add(decoded_url)
                        filename = f"{title}_{len(downloaded_urls)}.xlsx"
                        filepath = os.path.join(download_dir, filename)

                        try:
                            urllib.request.urlretrieve(decoded_url, filepath)
                            print(f"✅ 다운로드 완료: {filename}")
                        except Exception as e:
                            print(f"❌ 다운로드 실패: {decoded_url} - {e}")
                    else:
                        print(f"⚠️ URL 파라미터 없음: {href}")

            except Exception as e:
                print(f"⚠️ 게시글 오류: {e}")
                continue

        # 다시 게시판 목록 페이지로 이동
        driver.get("https://cafe.daum.net/kd4266/FJlw")
        time.sleep(2)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "down")))

        pagination_buttons = driver.find_elements(By.CSS_SELECTOR, "a.link_num")
        if current_page < len(pagination_buttons):
            pagination_buttons[current_page].click()  # 0-based index
            time.sleep(2)
            driver.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "down")))
        else:
            print("🚫 다음 페이지 버튼 없음")
            break

        current_page += 1

    except TimeoutException:
        print("⚠️ 페이지 로딩 시 피함")
        break

print("\n🎉 전체 크롤링 완료!")
driver.quit()
