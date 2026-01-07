import pandas as pd

# # 1. 수집된 데이터 불러오기
# df = pd.read_csv("melon_weekly_2024_full.csv")

# # 2. 데이 정제
# df_clean = df.dropna(subset=['순위', '곡명', '아티스트'])
# # 3. 정제된 데이터 저장
# df_clean.to_csv("melon_weekly_2024_cleaned.csv", index=False, encoding="utf-8-sig")

# print(f"정제 전: {len(df)}건 -> 정제 후: {len(df_clean)}건")

# 4. 연도 컬럼 추가
# 2024년 데이터 처리
df_2024 = pd.read_csv("data/melon_weekly_2024_cleaned.csv")
df_2024.insert(0, '연도', 2024)  # 맨 앞에 '연도' 컬럼 추가

# 2025년 데이터 처리
df_2025 = pd.read_csv("data/melon_weekly_2025_cleaned.csv")
df_2025.insert(0, '연도', 2025)  # 맨 앞에 '연도' 컬럼 추가

# 5. 두 데이터 합치기 (위아래로 연결)
df_total = pd.concat([df_2024, df_2025], ignore_index=True)

# 6. 아까 발생했던 비어있는 행(결측치) 한 번 더 정리
df_total = df_total.dropna(subset=['순위', '곡명', '아티스트'])

# 7. 최종 통합 데이터 저장
df_total.to_csv("melon_weekly_24_25_total.csv", index=False, encoding="utf-8-sig")

print(f"병합 완료! 전체 데이터 수: {len(df_total)}건")
print(df_total.head())