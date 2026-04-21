import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------
# 브라우저 설정
# -----------------------------
options = uc.ChromeOptions()
options.add_argument('--lang=ko_KR')
options.add_argument('--window-size=1920,1080')

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

all_chart_data = []

# -----------------------------
# 곡 추출 함수
# -----------------------------

def extract_songs(week_text, year):

    rows = driver.find_elements(By.CSS_SELECTOR, '#lst50, #lst100')
    week_range = week_text.split("~")

    week_start = week_range[0].strip()
    week_end = week_range[1].strip()

    for row in rows:
        try:
            rank = row.find_element(By.CSS_SELECTOR, ".rank").text
            title = row.find_element(By.CSS_SELECTOR, ".rank01 a").text
            artist = row.find_element(By.CSS_SELECTOR, ".rank02 a").text
            album = row.find_element(By.CSS_SELECTOR, ".rank03 a").text
            like_cnt = row.find_element(By.CSS_SELECTOR, ".cnt").text
            like_cnt = like_cnt.replace("총건수", "").replace(",", "").strip()
            like_cnt = int(like_cnt)

            if not rank or not title:
                continue

            all_chart_data.append({
                "year": year,
                "week": week_text,
                "week_start": week_start,
                "week_end": week_end,
                "rank": int(rank),
                "title": title,
                "artist": artist,
                "album": album,
                "like_cnt": like_cnt
            })

        except:
            continue


try:
    # -----------------------------
    # 1. 멜론 홈 진입 (필수)
    # -----------------------------
    driver.get("https://www.melon.com")
    time.sleep(1.5)

    # 멜론차트 클릭
    wait.until(EC.element_to_be_clickable(
        (By.LINK_TEXT, "멜론차트"))
    ).click()
    time.sleep(1)

    # 상세검색 열기
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span'))
    ).click()
    time.sleep(0.7)

    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="d_chart_search"]/div/h4[1]/a'))
    ).click()
    time.sleep(0.5)

    # -----------------------------
    # 연대 선택
    # -----------------------------
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[1]/span/label'))
    ).click()

    # year_list = ['2020','2021','2022','2023','2024','2025']
    year_list = ['2021']

    for year in year_list:
        print(f"\n===== {year} 시작 =====")

        # 연도 선택
        year_selector = f'input[name="year"][value="{year}"]'
        driver.execute_script(
            "arguments[0].click();",
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, year_selector)))
        )
        time.sleep(0.5)
        # 월 선택
        for month in range(9, 11):
            try:
                month_xpath = f'//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[{month}]/span/label'
                driver.execute_script(
                    "arguments[0].click();",
                    wait.until(EC.element_to_be_clickable((By.XPATH, month_xpath)))
                )
                time.sleep(0.5)
            except:
                continue

            weeks = driver.find_elements(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li')

            for w_idx in range(1, len(weeks)+1):

                retry = 0
                success = False

                while retry < 2 and not success:
                    try:
                        week_xpath = f'//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li[{w_idx}]/span/label'

                        week_element = wait.until(EC.element_to_be_clickable((By.XPATH, week_xpath)))
                        # week_text = week_element.text
                        # 주차 선택
                        driver.execute_script("arguments[0].click();", week_element)

                        # 주간차트 선택
                        driver.execute_script("arguments[0].click();",
                            wait.until(EC.element_to_be_clickable(
                                (By.XPATH, '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span/label')
                            ))
                        )

                        # 검색
                        driver.execute_script("arguments[0].click();",
                            wait.until(EC.element_to_be_clickable(
                                (By.XPATH, '//*[@id="d_srch_form"]/div[2]/button/span/span')
                            ))
                        )

                        time.sleep(0.8)
                        
                        week_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.datelk"))).text
                        
                        # 1~50위
                        extract_songs(week_text, year)

                        # 51~100위
                        driver.execute_script("movePage(2);")
                        time.sleep(0.8)

                        extract_songs(week_text, year)

                        print(f"✅ {year} {week_text} 완료 / 누적 {len(all_chart_data)}")

                        success = True

                    except Exception as e:
                        retry += 1
                        print(f"⚠️ 재시도 ({retry})")
                        time.sleep(1)

                if not success:
                    print(f"❌ 주차 스킵")
        # -----------------------------
        # ✅ 연도별 저장
        # -----------------------------
        df_year = pd.DataFrame(all_chart_data)
        df_year = df_year[df_year['year'] == year]

        df_year = df_year.dropna(subset=['rank','title'])
        df_year = df_year.drop_duplicates(subset=['week','rank','title'])

        df_year.to_csv(f"/Users/js/MMA/Melon_Music_Award/data/melon_{year}_ex.csv", index=False, encoding='utf-8-sig')
        print(f"🎉 {year} 저장 완료")

    # -----------------------------
    # 전체 저장
    # -----------------------------
    # df_all = pd.DataFrame(all_chart_data)
    # df_all = df_all.dropna(subset=['rank','title'])
    # df_all = df_all.drop_duplicates(subset=['year','week','rank'])

    # df_all.to_csv("/Users/js/MMA/Melon_Music_Award/data/melon_all_2020_2025.csv", index=False, encoding='utf-8-sig')
    # print("🔥 전체 데이터 저장 완료")

finally:
    driver.quit()