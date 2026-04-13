import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = uc.ChromeOptions()
options.add_argument('--lang=ko_KR')
options.add_argument('--window-size=1920,1080')

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

all_chart_data = []

# ✅ 곡 추출 함수
def extract_songs(current_week_text, year):
    try:
        start_str, end_str = current_week_text.split(" ~ ")

        # 🔥 연도 없는 경우 보완
        if len(start_str) <= 5:  # 예: 01.06
            start_str = f"{year}.{start_str}"
            end_str = f"{year}.{end_str}"

        start_date = pd.to_datetime(start_str.strip())
        end_date = pd.to_datetime(end_str.strip())

    except:
        start_date, end_date = None, None

    # ✅ 1~100위 한 번에 가져오기
    rows = driver.find_elements(By.CSS_SELECTOR, '#lst50, #lst100')

    for row in rows:
        try:
            rank = row.find_element(By.CSS_SELECTOR, ".rank").text
            title = row.find_element(By.CSS_SELECTOR, ".rank01 a").text
            artist = row.find_element(By.CSS_SELECTOR, ".rank02 a").text
            album = row.find_element(By.CSS_SELECTOR, ".rank03 a").text
            img_url = row.find_element(By.CSS_SELECTOR, "td div a img").get_attribute("src")

            try:
                like_cnt = row.find_element(By.CSS_SELECTOR, ".cnt").text.replace("총건수", "").replace(",", "").strip()
            except:
                like_cnt = "0"

            all_chart_data.append({
                "연도": year,
                "시작일": start_date,
                "종료일": end_date,
                "주차": current_week_text,
                "순위": rank,
                "곡명": title,
                "아티스트": artist,
                "앨범": album,
                "좋아요": like_cnt,
                "이미지URL": img_url
            })

        except:
            continue


try:
    driver.get("https://www.melon.com")
    time.sleep(2)

    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "멜론차트"))).click()
    time.sleep(0.5)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span'))).click()
    time.sleep(0.5)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="d_chart_search"]/div/h4[1]/a'))).click()
    time.sleep(0.5)

    # 연대 선택
    driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[1]/span/label').click()
    time.sleep(0.5)

    # 연도 선택
    year_list = ['2025', '2024']

    for year in year_list:
        print(f"\n===== {year} 시작 =====")

        year_selector = f'input[name="year"][value="{year}"]'
        year_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, year_selector)))
        driver.execute_script("arguments[0].click();", year_element)
        time.sleep(1)

        for month in range(1, 13):
            try:
                month_xpath = f'//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[{month}]/span/label'
                driver.find_element(By.XPATH, month_xpath).click()
                time.sleep(1)
            except:
                break

            # ✅ 매달마다 주차 다시 가져오기
            weeks = driver.find_elements(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li')

            for w_idx in range(1, len(weeks) + 1):
                try:
                    week_xpath = f'//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li[{w_idx}]/span/label'
                    week_element = driver.find_element(By.XPATH, week_xpath)

                    week_text = week_element.text
                    week_element.click()
                    time.sleep(1)

                    # 주간 차트 선택
                    driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span/label').click()

                    # 검색 버튼
                    driver.find_element(By.XPATH, '//*[@id="d_srch_form"]/div[2]/button/span/span').click()
                    time.sleep(1)

                    # ✅ 핵심: 한 번만 호출 (중복 제거)
                    extract_songs(week_text, year)

                    print(f"✅ {week_text} 완료 / 누적 {len(all_chart_data)}")

                except Exception as e:
                    print(f"주차 오류: {e}")
                    continue

    # ✅ 데이터프레임 생성
    if all_chart_data:
        df = pd.DataFrame(all_chart_data)

        # 🔥 중복 제거 (안전장치)
        df = df.drop_duplicates(subset=['연도', '주차', '순위', '곡명'])

        df.to_csv("melon_2024_2025.csv", index=False, encoding="utf-8-sig")
        print("저장 완료")

    else:
        print("데이터 없음")

except Exception as e:
    print(f"⚠️ 오류: {e}")

finally:
    driver.quit()