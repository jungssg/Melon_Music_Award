from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# 브라우저 설정
chrome_options = Options()
# chrome_options.add_argument('--headless')  # 화면 없이 실행하고 싶을 때 주석 해제
# 1. 실제 사용자의 브라우저 정보(User-Agent)로 위장
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
# 2. 자동제어 문구 제거 (멜론 보안 우회 핵심)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 3. 봇 탐지 방지를 위한 드라이버 속성 변경
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """
})


df = pd.read_csv('/Users/js/MMA/Melon_Music_Award/data/mma_2025.csv')
artist_names = df['아티스트'].unique()

final_results = []

print("데이터 수집을 시작합니다...")

for name in artist_names:
    # 아티스트별 '빈 양식' 생성 (정보가 없으면 None 유지)
    artist_form = {
        '아티스트명': name,
        '국적': None,
        '활동유형': None,
        '활동년대': None,
        '활동장르': None,
        '데뷔': None,
        '소속그룹': None,
        '멤버': None
    }
    
    try:
        # 3. 멜론 검색 페이지 접속
        search_url = f"https://www.melon.com/search/total/index.htm?q={name}"
        driver.get(search_url)
        time.sleep(1.5) # 페이지 로딩 대기
        
        # 4. 첫 번째 아티스트 클릭
        try:
            artist_link = driver.find_element(By.CSS_SELECTOR, '#artistList div ul li div div dl dt a')
            artist_link.click()
            time.sleep(1.5)
            
            # 5. 상세 정보 테이블(dl) 수집
            # 알려주신 경로 컨테이너를 타겟팅
            info_dl = driver.find_element(By.CSS_SELECTOR, 'div.atist_dtl_info dl')
            dts = info_dl.find_elements(By.TAG_NAME, 'dt')
            dds = info_dl.find_elements(By.TAG_NAME, 'dd')
            
            # 존재하는 정보만 딕셔너리에 매핑 (항목명이 바껴도 정확히 수집)
            for dt, dd in zip(dts, dds):
                key = dt.text.strip()
                val = dd.text.strip().replace('\n', ', ') # 여러 줄일 경우 쉼표로 구분
                
                if key in artist_form:
                    artist_form[key] = val
            
            print(f"성공: {name}")
            
        except Exception:
            print(f"검색 결과 없음: {name}")
            
    except Exception as e:
        print(f"에러 발생({name}): {e}")
    
    final_results.append(artist_form)

# 6. 데이터프레임 변환 및 저장
df_artist_master = pd.DataFrame(final_results)

# 태블로 분석을 위해 날짜 포맷팅 등 추가 전처리 (선택 사항)
# df_artist_master['데뷔일'] = df_artist_master['데뷔'].str.extract(r'(\d{4}\.\d{2}\.\d{2})')

df_artist_master.to_csv('melon_artist_master.csv', index=False, encoding='utf-8-sig')
print("--- 모든 수집이 완료되었습니다. ---")

driver.quit()