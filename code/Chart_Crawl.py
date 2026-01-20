import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. 크롬 옵션 설정
options = uc.ChromeOptions()
options.add_argument('--lang=ko_KR')
options.add_argument('--window-size=1920,1080')

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

all_chart_data = []

# --- 데이터 추출 함수 ---
def extract_songs(current_week_text):
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.lst50, tr.lst100")
    for row in rows:
        try:
            # 1. 순위
            rank = row.find_element(By.CSS_SELECTOR, ".rank").text
            # 2. 곡명
            title = row.find_element(By.CSS_SELECTOR, ".rank01 a").text  
            # 3. 아티스트
            artist = row.find_element(By.CSS_SELECTOR, ".rank02 a").text
            # 4. 앨범명
            album = row.find_element(By.CSS_SELECTOR, ".rank03 a").text
            # 5. 앨범 이미지 URL
            img_element = row.find_element(By.CSS_SELECTOR, "td div a img")   
            img_url = img_element.get_attribute("src")
            # 6. 좋아요 수
            try:
                like_cnt = row.find_element(By.CSS_SELECTOR, ".cnt").get_attribute("innerText").replace("총건수", "").replace(",", "").strip()
            except:
                like_cnt = "0"

            all_chart_data.append({
                "주차": current_week_text,
                "순위": rank,
                "곡명": title,
                "아티스트": artist,
                "앨범": album,
                "좋아요": like_cnt,
                "이미지URL": img_url
            })
        except Exception as e:
            print(f"데이터 추출 중 개별 오류 발생: {e}")
            continue

try:
    # 1. 멜론 홈페이지 접속
    driver.get("https://www.melon.com")
    time.sleep(3)

    # 2. 상단 '멜론차트' 메뉴 클릭
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "멜론차트"))).click()
    time.sleep(1)

    # 3. '차트파인더' 클릭
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span'))).click()
    time.sleep(1)

    # 4. 주간차트 탭 클릭
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="d_chart_search"]/div/h4[1]/a'))).click()
    time.sleep(0.5)
    
    # 5. 연대 선택 (2020년대)
    driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[1]/span/label').click()
    time.sleep(0.5)
    
    # 6. 연도 선택 (2025년)
    # driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[1]/span/label').click()
    # time.sleep(0.5)
    #2024년
    driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[2]/span/label').click()
    time.sleep(0.5)

    # 7. 월별 루프 (1월 ~ 12월)
    for month in range(1, 13):
        month_xpath = f'//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[{month}]/span/label'
        
        # 월이 존재하는지 체크 (미래의 월은 없을 수 있음)
        try:
            driver.find_element(By.XPATH, month_xpath).click()
            time.sleep(0.5)
        except:
            print(f"{month}월 데이터가 아직 없어 종료합니다.")
            break

        # 8. 주차 루프
        weeks = driver.find_elements(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li')
        
        for w_idx in range(1, len(weeks) + 1):
            week_xpath = f'//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li[{w_idx}]/span/label'
            week_element = driver.find_element(By.XPATH, week_xpath)
            week_text = week_element.text
            week_element.click()
            time.sleep(2)

            # 9. 장르 선택 (국내종합)
            driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span/label').click()
            
            # 10. 검색 버튼 클릭
            driver.find_element(By.XPATH, '//*[@id="d_srch_form"]/div[2]/button/span/span').click()
            time.sleep(2) # 첫 페이지(1~50위) 로딩 대기
            # [1~50위 수집]
            extract_songs(week_text)

            # [51~100위 수집]
            try:
                next_page_btn = driver.find_element(By.XPATH, '//*[@id="frm"]/div[2]/span/a')
                next_page_btn.click()
                time.sleep(1.5)
                
                extract_songs(week_text) # 같은 주차 텍스트로 51~100위 추가 수집
            except:
                print(f"51~100위 버튼이 없습니다. (주차: {week_text})")

            print(f"✅ {week_text} 1~100위 완료 (현재 누적 데이터: {len(all_chart_data)}건)")


    # 12. 데이터프레임 저장 및 MMA 비교 준비
    if all_chart_data:
        df = pd.DataFrame(all_chart_data)
        # 중복 데이터 제거 (주차, 순위, 곡명이 모두 일치하는 경우 하나만 남김)
        df = df.drop_duplicates(subset=['주차', '순위', '곡명'], keep='first')
        df.to_csv("melon_weekly_2024_full.csv", index=False, encoding="utf-8-sig")
        print(f"\n총 {len(df)}건의 데이터를 'melon_weekly_2024_full.csv'로 저장했습니다.")
         
    else:
        print("수집된 데이터가 없습니다.")

except Exception as e:
    print(f"⚠️ 오류 발생: {e}")

finally:
    driver.quit()