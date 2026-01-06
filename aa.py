import pandas as pd

# 1. 수집된 데이터 불러오기
df = pd.read_csv("melon_weekly_2025_full.csv")

# 2. 데이 정제
df_clean = df.dropna(subset=['순위', '곡명', '아티스트'])
# 3. 정제된 데이터 저장
df_clean.to_csv("melon_weekly_2025_cleaned.csv", index=False, encoding="utf-8-sig")

print(f"정제 전: {len(df)}건 -> 정제 후: {len(df_clean)}건")