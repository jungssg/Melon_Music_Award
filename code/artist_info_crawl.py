import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# 1. 크롬 드라이버 실행
options = uc.ChromeOptions()
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# 2. 멜론 접속
driver.get("https://www.melon.com")

time.sleep(2)

# 아티스트 리스트 (예시)

artists_df = pd.read_csv('/Users/js/MMA/Melon_Music_Award/code/missing_artists.csv')
artists = artists_df['artist']

results = []
for artist in artists:
    try:
        driver.get("https://www.melon.com")
        time.sleep(0.5)
        search_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#top_search"))
        )
        search_box.clear()
        search_box.send_keys(artist)
        search_box.send_keys(Keys.ENTER)  # 🔥 핵심
        time.sleep(1)

    # 이후 데이터 크롤링
    # 검색을 실행하면 다음 페이지 구성이 바뀜(반복으로 버튼 클릭불가) => 위 enter로 수정
# for artist in artists:
#     try:
#         # 3. 검색창 입력
#         time.sleep(1)
#         search_box = wait.until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "#top_search"))
#         )
#         search_box.clear()
#         search_box.send_keys(artist)

#         # 4. 검색 버튼 클릭
#         search_btn = driver.find_element(By.CSS_SELECTOR, "#gnb > div.header-utils > fieldset > button.btn_icon.search_m")
#         search_btn.click()

#         time.sleep(1.5)
        # 5. 아티스트 상세 정보 dl 가져오기
        dl_element = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#conts div.atist_dtl_info dl")
            )
        )

        # dt / dd 구조 전부 파싱
        dt_list = dl_element.find_elements(By.TAG_NAME, "dt")
        dd_list = dl_element.find_elements(By.TAG_NAME, "dd")

        artist_data = {"artist": artist}

        for dt, dd in zip(dt_list, dd_list):
            key = dt.text.strip()
            value = dd.text.strip()
            artist_data[key] = value

        results.append(artist_data)

        print(f"✅ 완료: {artist}")

        time.sleep(1)  # 너무 빠르면 차단됨
        
    except Exception as e:
        print(f"❌ 실패: {artist} / {e}")
        continue

# DataFrame 저장
df = pd.DataFrame(results)
df.to_csv("artist_info_crawled.csv", index=False)

driver.quit()