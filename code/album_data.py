from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random

import undetected_chromedriver as uc

# 크롬 드라이버 실행
options = uc.ChromeOptions()
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# 🔥 1. 최초 1회 접속 (세션 확보)
driver.get("https://www.melon.com")
time.sleep(3)

# 🔥 2. 크롤링 함수
def get_album_release_date(artist, album):
    # try:
    #     # 검색창
    #     search_box = wait.until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, "#top_search"))
    #     )
    #     search_box.clear()
    #     search_box.send_keys(f"{artist} {album}")

    try:
        search_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#top_search"))
        )
        search_box.clear()
        search_box.send_keys(f"{artist} {album}")
        search_box.send_keys(Keys.ENTER)
        time.sleep(0.8)
        
        # 🔥 차단 감지
        if "페이지를 찾을 수 없습니다" in driver.page_source:
            print("⚠️ 차단 감지 → 재접속")
            driver.get("https://www.melon.com")
            time.sleep(3)
            return None, False

        # 앨범 섹션
        album_section = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#conts > div.section_album")
            )
        )

        # 첫 번째 앨범
        first_album = album_section.find_element(
            By.CSS_SELECTOR, "ul > li:nth-child(1)"
        )

        # 🔥 발매일 추출
        release_date = first_album.find_element(
            By.CSS_SELECTOR, "span.cnt_view"
        ).text

        # 🔥 날짜 검증
        if not release_date.startswith("20"):
            return None, False

        return release_date, True

    except Exception as e:
        print(f"❌ 실패: {artist} - {album}", e)
        return None, False

# #============================================================================#
# # 데이터 로드
# df = pd.read_csv('/Users/js/MMA/Melon_Music_Award/data/주간차트/melon_total.csv')

# # 앨범 목록
# album_list = df[['artist', 'album']].drop_duplicates()

# # 결과 저장용
# results = []
# except_list = []

# # 🔥 3. 크롤링 실행
# for i, row in album_list.iterrows():
#     artist = row['artist']
#     album = row['album']
    
#     date, success = get_album_release_date(artist, album)
    
#     if success:
#         results.append({
#             'artist': artist,
#             'album': album,
#             'release_date': date
#         })
#     else:
#         except_list.append({
#             'artist': artist,
#             'album': album
#         })

#     print(f"[{i}] 아티스트: {artist}, 앨범: {album}, 발매일: {date}")

#     # 🔥 랜덤 딜레이
#     time.sleep(random.uniform(1, 3))

#     # 🔥 중간 저장 (100개마다)
#     if i % 100 == 0 and i != 0:
#         pd.DataFrame(results).to_csv("album_release_dates_temp.csv", index=False)
#         pd.DataFrame(except_list).to_csv("album_release_failures_temp.csv", index=False)
#         print("💾 중간 저장 완료")


# # 🔥 4. 최종 저장
# result_df = pd.DataFrame(results)
# result_df.to_csv("album_release_dates.csv", index=False)

# except_df = pd.DataFrame(except_list)
# except_df.to_csv("album_release_failures.csv", index=False)

# print("✅ 크롤링 완료")

#============================================================================#
# 데이터 로드 2차로 실패 데이터 수집
df = pd.read_csv('/Users/js/MMA/Melon_Music_Award/code/album_release_failures.csv')

# 앨범 목록
album_list = df.copy()

# 결과 저장용
results = []
except_list = []

# 🔥 3. 크롤링 실행
for i, row in album_list.iterrows():
    artist = row['artist']
    album = row['album']
    
    date, success = get_album_release_date(artist, album)
    
    if success:
        results.append({
            'artist': artist,
            'album': album,
            'release_date': date
        })
    else:
        except_list.append({
            'artist': artist,
            'album': album
        })

    print(f"[{i}] 아티스트: {artist}, 앨범: {album}, 발매일: {date}")

    # 🔥 랜덤 딜레이
    time.sleep(random.uniform(1, 3))

    # 🔥 중간 저장 (100개마다)
    if i % 100 == 0 and i != 0:
        pd.DataFrame(results).to_csv("album_release_dates_temp.csv", index=False)
        pd.DataFrame(except_list).to_csv("album_release_failures_temp.csv", index=False)
        print("💾 중간 저장 완료")


# 🔥 4. 최종 저장
result_df = pd.DataFrame(results)
result_df.to_csv("album_release_dates2.csv", index=False)

except_df = pd.DataFrame(except_list)
except_df.to_csv("album_release_failures2.csv", index=False)

print("✅ 크롤링 완료")


# 폴킴 - 마음 잘못됨