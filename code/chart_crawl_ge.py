import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ [최적화] 옵션 설정
options = uc.ChromeOptions()
# 자신의 크롬 버전과 유사한 최신 User-Agent 사용 (아래는 예시)
options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
options.add_argument('--lang=ko_KR')
options.add_argument('--no-first-run')
options.add_argument('--no-service-autorun')
options.add_argument('--password-store=basic')

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

all_chart_data = []

def extract_songs(current_week_text, year):
    # (데이터 추출 로직은 이전과 동일)
    rows = driver.find_elements(By.CSS_SELECTOR, '#lst50, #lst101')
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
                "year": int(year), "week": current_week_text,
                "rank": int(rank) if rank.isdigit() else None,
                "title": title, "artist": artist, "album": album,
                "like_cnt": int(like_cnt) if like_cnt.isdigit() else 0,
                "img_url": img_url
            })
        except: continue

try:
    # ✅ [변경] 메인 페이지부터 단계적으로 접근 (406 에러 방어)
    driver.get("https://www.melon.com")
    time.sleep(2)

    # 차트 파인더 페이지로 이동
    driver.get("https://www.melon.com/chart/search/index.htm")
    time.sleep(2)

    # 연도/월/주차 선택 로직 시작
    # (이하 기존 코드와 동일하지만, 클릭 전 wait를 더 넉넉히 줌)
    
    # 예시: 2020년대 클릭
    decade_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[1]/span/label')))
    driver.execute_script("arguments[0].click();", decade_btn)
    time.sleep(0.5)

    year_list = ['2024']
    for year in year_list:
        print(f"===== {year} 시작 =====")
        year_xpath = f'//input[@name="year" and @value="{year}"]/..//label'
        wait.until(EC.element_to_be_clickable((By.XPATH, year_xpath))).click()
        time.sleep(0.8)

        for month in range(1, 13):
            # (월 선택 코드...)
            month_xpath = f'//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[{month}]/span/label'
            wait.until(EC.element_to_be_clickable((By.XPATH, month_xpath))).click()
            time.sleep(0.5)

            weeks = driver.find_elements(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li')
            for w_idx in range(1, len(weeks) + 1):
                try:
                    week_xpath = f'//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li[{w_idx}]/span/label'
                    week_el = wait.until(EC.element_to_be_clickable((By.XPATH, week_xpath)))
                    week_text = week_el.text
                    week_el.click()
                    time.sleep(0.5)

                    # 주간차트 & 검색 클릭
                    driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span/label').click()
                    driver.find_element(By.XPATH, '//*[@id="d_srch_form"]/div[2]/button').click()
                    
                    # ✅ 데이터 로딩 충분히 대기
                    time.sleep(2.5) 
                    
                    extract_songs(week_text, year)
                    
                    # 2페이지(51~100위) 이동
                    driver.execute_script("movePage(2);")
                    time.sleep(2.0)
                    extract_songs(week_text, year)

                    print(f"✅ {week_text} 완료 (누적 {len(all_chart_data)})")

                except Exception as e:
                    print(f"오류: {e}")
                    continue

except Exception as e:
    print(f"⚠️ 실행 중 중단됨: {e}")

finally:
    if 'df' in locals() or all_chart_data:
        df = pd.DataFrame(all_chart_data)
        df.to_csv("melon_results.csv", index=False, encoding="utf-8-sig")
    driver.quit()