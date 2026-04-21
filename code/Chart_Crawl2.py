# 2019년 10~12월 데이터 추가 수집

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
# 곡 추출 함수 (기존 동일)
# -----------------------------
def extract_songs(week_text, year):
    rows = driver.find_elements(By.CSS_SELECTOR, '#lst50, #lst100')
    week_range = week_text.split("~")
    week_start = week_range[0].strip()
    week_end   = week_range[1].strip()

    for row in rows:
        try:
            rank     = row.find_element(By.CSS_SELECTOR, ".rank").text
            title    = row.find_element(By.CSS_SELECTOR, ".rank01 a").text
            artist   = row.find_element(By.CSS_SELECTOR, ".rank02 a").text
            album    = row.find_element(By.CSS_SELECTOR, ".rank03 a").text
            like_cnt = row.find_element(By.CSS_SELECTOR, ".cnt").text
            like_cnt = like_cnt.replace("총건수", "").replace(",", "").strip()
            like_cnt = int(like_cnt) if like_cnt.isdigit() else 0

            if not rank or not title:
                continue

            all_chart_data.append({
                "year":       year,
                "week":       week_text,
                "week_start": week_start,
                "week_end":   week_end,
                "rank":       int(rank),
                "title":      title,
                "artist":     artist,
                "album":      album,
                "like_cnt":   like_cnt
            })

        except Exception as e:
            print(f"  ⚠️ 파싱 실패: {e}")
            continue


try:
    # -----------------------------
    # 1. 멜론 홈 진입
    # -----------------------------
    driver.get("https://www.melon.com")
    time.sleep(1.5)

    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "멜론차트"))).click()
    time.sleep(1)

    # 상세검색 열기
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span')
    )).click()
    time.sleep(0.7)

    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="d_chart_search"]/div/h4[1]/a')
    )).click()
    time.sleep(0.5)

    # -----------------------------
    # 2. 연대 선택: 2010년대 (li:nth-child(2))
    # -----------------------------
    wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, '#d_chart_search div.box_chic.nth1 ul li:nth-child(2) label'))).click()
    time.sleep(0.5)

    # -----------------------------
    # 3. 연도 선택: 2019년 (li:nth-child(1))
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '#d_chart_search div.box_chic.nth2 ul li:nth-child(1) label')
    )).click()
    time.sleep(0.5)

    year = '2019'
    target_months = [10, 11, 12]  # 10월, 11월, 12월만

    print(f"\n===== {year} 시작 =====")

    # -----------------------------
    # 4. 월 선택 (10~12월)
    # -----------------------------
    for month in target_months:
        try:
            month_selector = f'#d_chart_search div.box_chic.nth3 ul li:nth-child({month}) label'

            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, month_selector)
            )).click()
            
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ {month}월 선택 실패: {e}")
            continue

        # -----------------------------
        # 5. 주차 목록 수집 후 순회
        # -----------------------------
        weeks = driver.find_elements(
            By.CSS_SELECTOR,
            '#d_chart_search > div > div > div.box_chic.nth4.view > div.list_value > ul > li'
        )

        for w_idx in range(1, len(weeks) + 1):

            retry   = 0
            success = False

            while retry < 2 and not success:
                try:
                    week_selector = f'#d_chart_search div.box_chic.nth4 ul li:nth-child({w_idx}) label'

                    week_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, week_selector)))

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

                    # span.datelk에서 week_text 가져오기
                    week_text = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "span.datelk"))
                    ).text

                    before_count = len(all_chart_data)  # 롤백용

                    # 1~50위
                    extract_songs(week_text, year)

                    # 51~100위
                    driver.execute_script("movePage(2);")
                    time.sleep(0.8)
                    extract_songs(week_text, year)

                    print(f"✅ {year} {week_text} 완료 / 누적 {len(all_chart_data)}")
                    success = True

                except Exception as e:
                    all_chart_data[before_count:] = []  # 중복 적재 롤백
                    retry += 1
                    print(f"⚠️ 재시도 ({retry}): {e}")
                    time.sleep(1)

            if not success:
                print(f"❌ {month}월 {w_idx}번째 주차 스킵")

    # -----------------------------
    # 6. 저장
    # -----------------------------
    df_2019 = pd.DataFrame(all_chart_data)
    df_2019 = df_2019.dropna(subset=['rank', 'title'])
    df_2019 = df_2019.drop_duplicates(subset=['week', 'rank', 'title'])

    df_2019.to_csv(
        "/Users/js/MMA/Melon_Music_Award/data/melon_2019.csv",
        index=False, encoding='utf-8-sig'
    )
    print("🎉 2019년 10~12월 저장 완료")

finally:
    driver.quit()