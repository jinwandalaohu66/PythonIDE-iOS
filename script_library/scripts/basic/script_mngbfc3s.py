import photos
from collections import Counter
import datetime

assets = photos.get_assets(media_type='photo', limit=0)
print(f'共 {len(assets)} 张照片')

year_counter = Counter()
for asset in assets:
    ts = asset.creation_date
    if ts:
        year = datetime.datetime.fromtimestamp(ts).year
        year_counter[year] += 1

print('\n按年份分布：')
for year in sorted(year_counter):
    bar = '█' * (year_counter[year] // 10)
    print(f'{year}: {year_counter[year]:4d} 张  {bar}')